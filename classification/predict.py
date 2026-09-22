"""Load a trained pipeline and classify new text without retraining."""

import argparse
from pathlib import Path

import joblib

from .data import LABEL_NAMES
from .features import text_to_document_feature_frame, text_to_feature_frame
from .models import prediction_scores


DEFAULT_MODEL_PATH = Path("artifacts/classification/final_text_classifier.joblib")


def predict_text(
    text: str,
    model_path: str | Path | None = None,
    unit: str = "sentence",
) -> dict[str, object]:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Text must be a non-empty string.")
    if unit not in {"sentence", "document"}:
        raise ValueError("Prediction unit must be 'sentence' or 'document'.")
    if model_path is None:
        model_path = (
            DEFAULT_MODEL_PATH
            if unit == "sentence"
            else Path("artifacts/document_classification/final_text_classifier.joblib")
        )
    artifact_path = Path(model_path)
    if not artifact_path.is_file():
        raise FileNotFoundError(f"Trained model not found: {artifact_path}")
    samples = (
        text_to_feature_frame(text)
        if unit == "sentence"
        else text_to_document_feature_frame(text)
    )
    model = joblib.load(artifact_path)
    predictions = model.predict(samples)
    scores, score_type = prediction_scores(model, samples)
    document_score = float(scores.mean())
    threshold = 0.5 if score_type == "ai_probability" else 0.0
    document_prediction = int(document_score >= threshold)
    sentence_results = [
        {
            "text": sentence,
            "label": LABEL_NAMES[int(prediction)],
            "score": float(score),
            "score_type": score_type,
        }
        for sentence, prediction, score in zip(samples["text"], predictions, scores, strict=True)
    ]
    return {
        "label": LABEL_NAMES[document_prediction],
        "numeric_label": document_prediction,
        "score": document_score,
        "score_type": score_type,
        "sentence_results": sentence_results,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Classify text using a saved model.")
    parser.add_argument("text", help="Text to classify")
    parser.add_argument("--unit", choices=["sentence", "document"], default="sentence")
    parser.add_argument("--model")
    args = parser.parse_args()
    print(predict_text(args.text, args.model, args.unit))


if __name__ == "__main__":
    main()
