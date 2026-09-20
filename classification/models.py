"""Model definitions and evaluation helpers."""

from collections.abc import Mapping, Sequence

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import LinearSVC
from xgboost import XGBClassifier

from .data import LABEL_NAMES
from .features import NUMERIC_FEATURES


MODEL_ORDER = ("logistic_regression", "linear_svm", "xgboost")
DISPLAY_NAMES = {
    "logistic_regression": "Logistic Regression",
    "linear_svm": "Linear SVM",
    "xgboost": "XGBoost",
}


def build_models(
    random_seed: int = 42,
    max_features: int = 20_000,
    xgboost_estimators: int = 80,
    numeric_features: Sequence[str] = NUMERIC_FEATURES,
) -> dict[str, Pipeline]:
    """Build three classifiers using the same TF-IDF and numeric inputs."""
    feature_builder = ColumnTransformer(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 2),
                    min_df=2,
                    max_df=0.98,
                    max_features=max_features,
                    sublinear_tf=True,
                    dtype=np.float32,
                ),
                "text",
            ),
            (
                "numeric",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler(with_mean=False)),
                    ]
                ),
                list(numeric_features),
            ),
        ]
    )
    classifiers = {
        "logistic_regression": SGDClassifier(
            loss="log_loss",
            max_iter=1_000,
            tol=1e-3,
            class_weight="balanced",
            random_state=random_seed,
        ),
        "linear_svm": LinearSVC(
            class_weight="balanced", random_state=random_seed, max_iter=10_000, tol=1e-3
        ),
        "xgboost": XGBClassifier(
            n_estimators=xgboost_estimators,
            max_depth=4,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="binary:logistic",
            eval_metric="logloss",
            tree_method="hist",
            random_state=random_seed,
            n_jobs=4,
        ),
    }
    return {
        name: Pipeline([("features", clone(feature_builder)), ("classifier", classifier)])
        for name, classifier in classifiers.items()
    }


def calculate_metrics(y_true: pd.Series, y_pred: np.ndarray) -> dict[str, float]:
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_true, y_pred, average="binary", pos_label=1, zero_division=0
    )
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
    }


def prediction_scores(model: Pipeline, samples: pd.DataFrame) -> tuple[np.ndarray, str]:
    if hasattr(model, "predict_proba"):
        return model.predict_proba(samples)[:, 1], "ai_probability"
    if hasattr(model, "decision_function"):
        return model.decision_function(samples), "ai_decision_score"
    return np.full(len(samples), np.nan), "unavailable"


def evaluate_models(
    models: Mapping[str, Pipeline], data: pd.DataFrame, split_name: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    metric_rows: list[dict[str, object]] = []
    prediction_frames: list[pd.DataFrame] = []
    trace_columns = ["sample_id", "doc_id", "sent_id", "source", "prompt", "text"]
    for model_name in MODEL_ORDER:
        model = models[model_name]
        predictions = model.predict(data)
        scores, score_type = prediction_scores(model, data)
        metric_rows.append(
            {
                "model": DISPLAY_NAMES[model_name],
                "split": split_name,
                **calculate_metrics(data["label"], predictions),
            }
        )
        frame = data[trace_columns].copy()
        frame["true_label"] = data["label"].map(LABEL_NAMES)
        frame["predicted_label"] = pd.Series(predictions, index=data.index).map(LABEL_NAMES)
        frame["model"] = DISPLAY_NAMES[model_name]
        frame["score"] = scores
        frame["score_type"] = score_type
        frame["split"] = split_name
        prediction_frames.append(frame)
    return pd.DataFrame(metric_rows), pd.concat(prediction_frames, ignore_index=True)


def select_model(validation_metrics: pd.DataFrame) -> str:
    display_to_key = {display: key for key, display in DISPLAY_NAMES.items()}
    order = {DISPLAY_NAMES[name]: index for index, name in enumerate(MODEL_ORDER)}
    ranked = validation_metrics.assign(model_order=validation_metrics["model"].map(order)).sort_values(
        ["f1", "accuracy", "model_order"], ascending=[False, False, True]
    )
    return display_to_key[str(ranked.iloc[0]["model"])]
