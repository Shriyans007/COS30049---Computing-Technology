"""Repeatable Section 2.8 detection-evasion measurement."""

import argparse
import csv
import json
from pathlib import Path
from statistics import mean

import joblib

from classification.features import text_to_document_feature_frame

from backend.app.config import REPOSITORY_ROOT
from backend.app.normalisation import normalise_security_text


HERE = Path(__file__).resolve().parent
DEFAULT_DATA = HERE / "data/detection_evasion_samples.json"
DEFAULT_RESULTS = HERE / "results"
DEFAULT_MODEL = REPOSITORY_ROOT / "artifacts/document_classification/final_text_classifier.joblib"

LATIN_TO_CYRILLIC = str.maketrans(
    {"a": "а", "e": "е", "o": "о", "p": "р", "c": "с", "x": "х", "i": "і"}
)


def attack_variants(text: str) -> dict[str, str]:
    words = text.split()
    zero_width = " ".join(
        word[: max(1, len(word) // 2)] + "\u200b" + word[max(1, len(word) // 2):]
        if len(word) >= 6 else word
        for word in words
    )
    return {
        "confusables": text.translate(LATIN_TO_CYRILLIC),
        "zero_width": zero_width,
        "non_breaking_spaces": "\u00a0".join(words),
        "combined": zero_width.translate(LATIN_TO_CYRILLIC).replace(" ", "\u2009"),
    }


def ai_probability(model, text: str) -> float:
    frame = text_to_document_feature_frame(text)
    return float(model.predict_proba(frame)[0][1])


def run_experiment(data_path: Path, output_dir: Path, model_path: Path) -> dict[str, object]:
    data = json.loads(data_path.read_text(encoding="utf-8"))
    model = joblib.load(model_path)
    if not hasattr(model, "predict_proba"):
        raise RuntimeError("The document model must provide calibrated probabilities.")

    rows: list[dict[str, object]] = []
    eligible = []
    for sample_number, original in enumerate(data["ai_samples"], start=1):
        original_probability = ai_probability(model, original)
        if original_probability >= 0.5:
            eligible.append((sample_number, original, original_probability))

    for sample_number, original, original_probability in eligible:
        for attack_name, attacked in attack_variants(original).items():
            before_probability = ai_probability(model, attacked)
            defended_text = normalise_security_text(attacked)
            after_probability = ai_probability(model, defended_text)
            rows.append(
                {
                    "sample": sample_number,
                    "attack": attack_name,
                    "original_ai_probability": original_probability,
                    "attacked_ai_probability_before_defence": before_probability,
                    "attacked_prediction_before_defence": "ai" if before_probability >= 0.5 else "human",
                    "attacked_ai_probability_after_defence": after_probability,
                    "attacked_prediction_after_defence": "ai" if after_probability >= 0.5 else "human",
                    "evaded_before_defence": before_probability < 0.5,
                    "evaded_after_defence": after_probability < 0.5,
                    "text_changed_by_defence": defended_text != attacked,
                }
            )

    clean_changes = 0
    for control in data["clean_controls"]:
        before = ai_probability(model, control)
        after = ai_probability(model, normalise_security_text(control))
        clean_changes += int((before >= 0.5) != (after >= 0.5))

    variants = len(rows)
    before_evasions = sum(bool(row["evaded_before_defence"]) for row in rows)
    after_evasions = sum(bool(row["evaded_after_defence"]) for row in rows)
    summary = {
        "model": model_path.name,
        "fixed_ai_samples": len(data["ai_samples"]),
        "eligible_original_ai_samples": len(eligible),
        "attacked_variants": variants,
        "evasion_success_rate_before_defence": before_evasions / variants if variants else None,
        "evasion_success_rate_after_defence": after_evasions / variants if variants else None,
        "average_confidence_change_before_defence": mean(
            float(row["attacked_ai_probability_before_defence"]) - float(row["original_ai_probability"])
            for row in rows
        ) if rows else None,
        "average_confidence_change_after_defence": mean(
            float(row["attacked_ai_probability_after_defence"]) - float(row["original_ai_probability"])
            for row in rows
        ) if rows else None,
        "clean_control_count": len(data["clean_controls"]),
        "clean_control_prediction_changes": clean_changes,
        "clean_control_change_rate": clean_changes / len(data["clean_controls"]),
        "remaining_evasions": after_evasions,
        "limitations": (
            "The fixed set is small and authored for a security demonstration. The limited mapping "
            "does not cover every Unicode confusable and may alter legitimate multilingual text."
        ),
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "detection_evasion_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["sample"])
        writer.writeheader()
        writer.writerows(rows)
    (output_dir / "detection_evasion_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_RESULTS)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL)
    args = parser.parse_args()
    print(json.dumps(run_experiment(args.data, args.output_dir, args.model), indent=2))


if __name__ == "__main__":
    main()
