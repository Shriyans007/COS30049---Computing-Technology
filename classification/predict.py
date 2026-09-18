"""Load a trained pipeline and classify new text without retraining."""

import argparse
from pathlib import Path

import joblib

from .data import LABEL_NAMES
from .models import prediction_scores


DEFAULT_MODEL_PATH = Path("artifacts/classification/final_text_classifier.joblib")


def predict_text(text: str, model_path: str | Path = DEFAULT_MODEL_PATH) -> dict[str, object]:
    """Predict one text sample using a saved preprocessing/model pipeline."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Text must be a non-empty string.")
    artifact_path = Path(model_path)
    if not artifact_path.is_file():
        raise FileNotFoundError(
            f"Trained model not found: {artifact_path}. Run the training command first."
        )

    model = joblib.load(artifact_path)
    cleaned_text = text.strip()
    prediction = int(model.predict([cleaned_text])[0])
    scores, score_type = prediction_scores(model, [cleaned_text])
    return {
        "label": LABEL_NAMES[prediction],
        "numeric_label": prediction,
        "score": float(scores[0]),
        "score_type": score_type,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify text using a saved model.")
    parser.add_argument("text", help="Text to classify")
    parser.add_argument("--model", default=str(DEFAULT_MODEL_PATH))
    args = parser.parse_args()
    print(predict_text(args.text, args.model))


if __name__ == "__main__":
    main()

