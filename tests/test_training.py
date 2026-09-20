import json

import pandas as pd
import pytest

from classification.predict import predict_text
from classification.train import TrainingConfig, run_training


@pytest.fixture
def small_dataset(tmp_path):
    human_templates = [
        "I went to the shops after class and forgot my umbrella",
        "My notes are messy but this is how I understood the topic",
        "We met at the library and worked through the tutorial together",
        "I changed my mind halfway through writing this paragraph",
    ]
    ai_templates = [
        "This comprehensive overview examines the key considerations in detail",
        "Furthermore the following structured analysis highlights important factors",
        "In conclusion this systematic explanation provides a balanced perspective",
        "The implementation demonstrates a robust and efficient approach to the task",
    ]
    rows = []
    for index in range(20):
        rows.append({
            "doc_id": f"h-{index}", "sent_id": 0,
            "text": f"{human_templates[index % 4]} {index}", "label": "human"
        })
        rows.append({
            "doc_id": f"a-{index}", "sent_id": 0,
            "text": f"{ai_templates[index % 4]} {index}", "label": "ai"
        })
    path = tmp_path / "test_fixture.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def test_training_saving_loading_prediction_and_exports(tmp_path, small_dataset):
    output_dir = tmp_path / "outputs"
    artifact_dir = tmp_path / "artifacts"
    result = run_training(
        TrainingConfig(
            dataset=str(small_dataset),
            output_dir=str(output_dir),
            artifact_dir=str(artifact_dir),
            max_features=500,
            xgboost_estimators=8,
        )
    )

    assert result["selected_model"] in {"logistic_regression", "linear_svm", "xgboost"}
    assert set(result["test_metrics"]["model"]) == {"Logistic Regression", "Linear SVM", "XGBoost"}
    assert (output_dir / "validation_metrics.csv").is_file()
    assert (output_dir / "model_comparison.csv").is_file()
    assert (output_dir / "test_predictions.csv").is_file()
    assert (artifact_dir / "final_text_classifier.joblib").is_file()

    prediction = predict_text(
        "I rewrote this sentence because the first version sounded strange.",
        artifact_dir / "final_text_classifier.joblib",
    )
    assert prediction["label"] in {"human", "ai"}
    assert prediction["score_type"] in {"ai_probability", "ai_decision_score"}

    metadata = json.loads((artifact_dir / "model_metadata.json").read_text(encoding="utf-8"))
    assert metadata["selection_rule"].startswith("highest validation F1")


def test_predict_rejects_empty_text(tmp_path):
    with pytest.raises(ValueError, match="non-empty"):
        predict_text("   ", tmp_path / "missing.joblib")
