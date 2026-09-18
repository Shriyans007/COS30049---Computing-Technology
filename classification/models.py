"""Model definitions and evaluation helpers."""

from collections.abc import Mapping

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from xgboost import XGBClassifier

from .data import LABEL_NAMES


MODEL_ORDER = ("logistic_regression", "linear_svm", "xgboost")
DISPLAY_NAMES = {
    "logistic_regression": "Logistic Regression",
    "linear_svm": "Linear SVM",
    "xgboost": "XGBoost",
}


def build_models(
    random_seed: int = 42,
    max_features: int = 20_000,
    xgboost_estimators: int = 150,
) -> dict[str, Pipeline]:
    """Build the three classifiers with independent TF-IDF pipelines."""
    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        min_df=1,
        max_df=0.98,
        max_features=max_features,
        sublinear_tf=True,
    )
    classifiers = {
        "logistic_regression": LogisticRegression(
            max_iter=1_000,
            class_weight="balanced",
            random_state=random_seed,
        ),
        "linear_svm": LinearSVC(
            class_weight="balanced",
            random_state=random_seed,
        ),
        "xgboost": XGBClassifier(
            n_estimators=xgboost_estimators,
            max_depth=4,
            learning_rate=0.08,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=random_seed,
            n_jobs=1,
        ),
    }
    return {
        name: Pipeline([("tfidf", clone(vectorizer)), ("classifier", classifier)])
        for name, classifier in classifiers.items()
    }


def calculate_metrics(y_true: pd.Series, y_pred: np.ndarray) -> dict[str, float]:
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true,
        y_pred,
        average="binary",
        pos_label=1,
        zero_division=0,
    )
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
    }


def prediction_scores(model: Pipeline, texts: pd.Series) -> tuple[np.ndarray, str]:
    """Return a valid positive-class score and describe its meaning."""
    if hasattr(model, "predict_proba"):
        return model.predict_proba(texts)[:, 1], "ai_probability"
    if hasattr(model, "decision_function"):
        return model.decision_function(texts), "ai_decision_score"
    return np.full(len(texts), np.nan), "unavailable"


def evaluate_models(
    models: Mapping[str, Pipeline],
    data: pd.DataFrame,
    split_name: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    metric_rows: list[dict[str, object]] = []
    prediction_frames: list[pd.DataFrame] = []

    for model_name in MODEL_ORDER:
        model = models[model_name]
        predictions = model.predict(data["text"])
        scores, score_type = prediction_scores(model, data["text"])
        metric_rows.append(
            {
                "model": DISPLAY_NAMES[model_name],
                "split": split_name,
                **calculate_metrics(data["label"], predictions),
            }
        )
        prediction_frames.append(
            pd.DataFrame(
                {
                    "sample_id": data["sample_id"],
                    "text": data["text"],
                    "true_label": data["label"].map(LABEL_NAMES),
                    "predicted_label": pd.Series(predictions).map(LABEL_NAMES),
                    "model": DISPLAY_NAMES[model_name],
                    "score": scores,
                    "score_type": score_type,
                    "split": split_name,
                }
            )
        )

    return pd.DataFrame(metric_rows), pd.concat(prediction_frames, ignore_index=True)


def select_model(validation_metrics: pd.DataFrame) -> str:
    """Select by validation F1, then accuracy, using stable model order for ties."""
    display_to_key = {display: key for key, display in DISPLAY_NAMES.items()}
    ranked = validation_metrics.assign(
        model_order=validation_metrics["model"].map(
            {DISPLAY_NAMES[name]: index for index, name in enumerate(MODEL_ORDER)}
        )
    ).sort_values(
        ["f1", "accuracy", "model_order"],
        ascending=[False, False, True],
    )
    return display_to_key[str(ranked.iloc[0]["model"])]

