"""Command-line training workflow for the three text classifiers."""

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import joblib
import pandas as pd

from .data import load_dataset, split_dataset
from .features import NUMERIC_FEATURES
from .models import DISPLAY_NAMES, build_models, evaluate_models, select_model


@dataclass(frozen=True)
class TrainingConfig:
    dataset: str
    unit: str = "sentence"
    zip_member: str | None = None
    text_column: str = "text"
    label_column: str = "label"
    id_column: str | None = "id"
    output_dir: str = "outputs/classification"
    artifact_dir: str = "artifacts/classification"
    random_seed: int = 42
    max_features: int = 20_000
    xgboost_estimators: int = 80
    remove_exact_duplicates: bool = True


def run_training(config: TrainingConfig) -> dict[str, object]:
    if config.unit not in {"sentence", "document"}:
        raise ValueError("Training unit must be 'sentence' or 'document'.")
    output_dir = Path(config.output_dir)
    artifact_dir = Path(config.artifact_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    artifact_dir.mkdir(parents=True, exist_ok=True)
    print("Loading and validating dataset...", flush=True)
    data = load_dataset(
        config.dataset,
        text_column=config.text_column,
        label_column=config.label_column,
        id_column=config.id_column,
        zip_member=config.zip_member,
        remove_exact_duplicates=config.remove_exact_duplicates,
    )
    audit = data.attrs.get("audit", {})
    row_name = "sentence" if config.unit == "sentence" else "document"
    print(
        f"Prepared {len(data):,} {row_name} rows from "
        f"{data['doc_id'].nunique():,} documents.",
        flush=True,
    )
    splits = split_dataset(data, random_seed=config.random_seed)
    models = build_models(
        random_seed=config.random_seed,
        max_features=config.max_features,
        xgboost_estimators=config.xgboost_estimators,
    )

    for model_name, model in models.items():
        print(f"Training {DISPLAY_NAMES[model_name]} on the training split...", flush=True)
        model.fit(splits.train, splits.train["label"])
    validation_metrics, _ = evaluate_models(models, splits.validation, "validation")
    selected_name = select_model(validation_metrics)

    train_validation = pd.concat([splits.train, splits.validation], ignore_index=True)
    for model_name, model in models.items():
        print(f"Refitting {DISPLAY_NAMES[model_name]} on train + validation...", flush=True)
        model.fit(train_validation, train_validation["label"])
    test_metrics, test_predictions = evaluate_models(models, splits.test, "test")
    validation_metrics.to_csv(output_dir / "validation_metrics.csv", index=False)
    test_metrics.to_csv(output_dir / "model_comparison.csv", index=False)
    test_predictions.to_csv(output_dir / "test_predictions.csv", index=False)

    artifact_path = artifact_dir / "final_text_classifier.joblib"
    joblib.dump(models[selected_name], artifact_path)
    loaded_model = joblib.load(artifact_path)
    if not (loaded_model.predict(splits.test) == models[selected_name].predict(splits.test)).all():
        raise RuntimeError("Reloaded model predictions do not match the saved model.")

    metadata = {
        "status": f"trained_on_person_2_{config.unit}_dataset",
        "unit": config.unit,
        "selected_model": selected_name,
        "selected_model_display": DISPLAY_NAMES[selected_name],
        "selection_rule": "highest validation F1, then validation accuracy",
        "evaluation_unit": (
            "sentence, with document-grouped splitting"
            if config.unit == "sentence"
            else "full source document"
        ),
        "score_note": "Linear SVM scores are decision scores, not probabilities.",
        "class_mapping": {"0": "human", "1": "ai"},
        "numeric_features": NUMERIC_FEATURES,
        "dataset_audit": audit,
        "split_rows": {
            "train": len(splits.train),
            "validation": len(splits.validation),
            "test": len(splits.test),
        },
        "split_documents": {
            "train": int(splits.train["doc_id"].nunique()),
            "validation": int(splits.validation["doc_id"].nunique()),
            "test": int(splits.test["doc_id"].nunique()),
        },
        "config": asdict(config),
    }
    metadata_path = artifact_dir / "model_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return {
        "selected_model": selected_name,
        "artifact_path": str(artifact_path),
        "metadata_path": str(metadata_path),
        "validation_metrics": validation_metrics,
        "test_metrics": test_metrics,
        "audit": audit,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train and compare text classifiers.")
    parser.add_argument("--unit", choices=["sentence", "document"], default="sentence")
    parser.add_argument("--dataset")
    parser.add_argument("--zip-member")
    parser.add_argument("--text-column", default="text")
    parser.add_argument("--label-column", default="label")
    parser.add_argument("--id-column", default="id")
    parser.add_argument("--output-dir")
    parser.add_argument("--artifact-dir")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--max-features", type=int, default=20_000)
    parser.add_argument("--xgboost-estimators", type=int, default=80)
    parser.add_argument("--keep-exact-duplicates", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.unit == "sentence":
        default_dataset = "data/processed/final_dataset.csv"
        default_output = "outputs/classification"
        default_artifact = "artifacts/classification"
    else:
        default_dataset = "data/processed/para_dataset.csv"
        default_output = "outputs/document_classification"
        default_artifact = "artifacts/document_classification"
    config = TrainingConfig(
        dataset=args.dataset or default_dataset,
        unit=args.unit,
        zip_member=args.zip_member,
        text_column=args.text_column,
        label_column=args.label_column,
        id_column=args.id_column or None,
        output_dir=args.output_dir or default_output,
        artifact_dir=args.artifact_dir or default_artifact,
        random_seed=args.seed,
        max_features=args.max_features,
        xgboost_estimators=args.xgboost_estimators,
        remove_exact_duplicates=not args.keep_exact_duplicates,
    )
    try:
        result = run_training(config)
    except (FileNotFoundError, ValueError) as error:
        raise SystemExit(f"Training stopped: {error}") from None
    print(result["test_metrics"].to_string(index=False))
    print(f"Selected from validation results: {result['selected_model']}")
    print(f"Saved model: {result['artifact_path']}")


if __name__ == "__main__":
    main()
