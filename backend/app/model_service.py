"""Load both fitted pipelines once and provide thread-safe inference data."""

import json
import re
import time
from pathlib import Path

import joblib
import numpy as np

from classification.features import text_to_document_feature_frame, text_to_feature_frame
from classification.models import prediction_scores

from .normalisation import normalise_security_text


class ModelService:
    def __init__(self, sentence_path: Path, document_path: Path, test_delay_ms: int = 0) -> None:
        for path in (sentence_path, document_path):
            if not path.is_file():
                raise RuntimeError(f"Required trained model is missing: {path.name}")
        self.sentence_model = joblib.load(sentence_path)
        self.document_model = joblib.load(document_path)
        self.test_delay_ms = test_delay_ms
        self.sentence_name = self._model_name(sentence_path)
        self.document_name = self._model_name(document_path)
        self._verify_probabilities()

    @staticmethod
    def _model_name(model_path: Path) -> str:
        metadata_path = model_path.with_name("model_metadata.json")
        if not metadata_path.is_file():
            return "trained classifier"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        return str(metadata.get("selected_model_display", "trained classifier"))

    def _verify_probabilities(self) -> None:
        for model in (self.sentence_model, self.document_model):
            if not hasattr(model, "predict_proba"):
                raise RuntimeError("A loaded model does not provide calibrated class probabilities.")

    def predict(self, original_text: str) -> dict[str, object]:
        if self.test_delay_ms:
            time.sleep(self.test_delay_ms / 1_000)
        normalised = normalise_security_text(original_text)
        sentence_frame = text_to_feature_frame(normalised)
        document_frame = text_to_document_feature_frame(normalised)

        document_scores, score_type = prediction_scores(self.document_model, document_frame)
        if score_type != "ai_probability":
            raise RuntimeError("Document model did not return AI probabilities.")
        ai_probability = float(document_scores[0])
        prediction = "ai" if ai_probability >= 0.5 else "human"

        sentence_predictions = self.sentence_model.predict(sentence_frame)
        sentence_scores, sentence_score_type = prediction_scores(self.sentence_model, sentence_frame)
        if sentence_score_type != "ai_probability":
            raise RuntimeError("Sentence model did not return AI probabilities.")

        # Keep submitted characters for safe text-node display. This splitter is linear and
        # mirrors the model splitter without normalising the user's displayed content.
        display_sentences = [
            part.strip()
            for part in re.split(r"(?<=[.!?])\s+", original_text.strip())
            if re.search(r"\w", part)
        ]
        if len(display_sentences) != len(sentence_frame):
            display_sentences = sentence_frame["text"].tolist()
        sentence_results = [
            {
                "text": display,
                "label": "ai" if int(label) == 1 else "human",
                "ai_probability": float(score),
            }
            for display, label, score in zip(
                display_sentences, sentence_predictions, sentence_scores, strict=True
            )
        ]
        confidence_range = self._bootstrap_range(sentence_scores)
        return {
            "prediction": prediction,
            "ai_probability": ai_probability,
            "confidence": ai_probability if prediction == "ai" else 1.0 - ai_probability,
            "confidence_range": confidence_range,
            "sentence_results": sentence_results,
            "normalisation_applied": normalised != original_text.strip(),
        }

    @staticmethod
    def _bootstrap_range(scores: np.ndarray) -> dict[str, object] | None:
        if len(scores) < 2 or not np.isfinite(scores).all():
            return None
        generator = np.random.default_rng(42)
        means = generator.choice(scores, size=(1_000, len(scores)), replace=True).mean(axis=1)
        lower, upper = np.quantile(means, [0.025, 0.975])
        return {
            "lower": float(lower),
            "upper": float(upper),
            "method": "95% bootstrap interval across sentence AI probabilities",
        }
