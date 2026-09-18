"""Dataset loading, validation, and reproducible splitting."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


LABEL_NAMES = {0: "human", 1: "ai"}
LABEL_VALUES = {
    "0": 0,
    "human": 0,
    "human-written": 0,
    "human_written": 0,
    "1": 1,
    "ai": 1,
    "ai-generated": 1,
    "ai_generated": 1,
}


@dataclass(frozen=True)
class DatasetSplits:
    train: pd.DataFrame
    validation: pd.DataFrame
    test: pd.DataFrame


def _normalise_label(value: object) -> int:
    if pd.isna(value):
        raise ValueError("Labels cannot be empty.")
    key = str(value).strip().lower()
    if key.endswith(".0") and key[:-2] in {"0", "1"}:
        key = key[:-2]
    if key not in LABEL_VALUES:
        allowed = "human, ai, 0, or 1"
        raise ValueError(f"Unsupported label {value!r}. Expected {allowed}.")
    return LABEL_VALUES[key]


def load_dataset(
    path: str | Path,
    text_column: str = "text",
    label_column: str = "label",
    id_column: str | None = "id",
) -> pd.DataFrame:
    """Load a CSV and return standardised id, text, and integer label columns."""
    dataset_path = Path(path)
    if not dataset_path.is_file():
        raise FileNotFoundError(
            f"Dataset not found: {dataset_path}. "
            "Add Person 2's processed CSV or pass --dataset with its location."
        )

    data = pd.read_csv(dataset_path)
    required = {text_column, label_column}
    missing = required.difference(data.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

    selected = pd.DataFrame()
    if id_column and id_column in data.columns:
        selected["sample_id"] = data[id_column]
    else:
        selected["sample_id"] = data.index

    selected["text"] = data[text_column].fillna("").astype(str).str.strip()
    if (selected["text"].str.len() == 0).any():
        empty_count = int((selected["text"].str.len() == 0).sum())
        raise ValueError(f"Dataset contains {empty_count} empty text value(s).")

    selected["label"] = data[label_column].map(_normalise_label)
    class_counts = selected["label"].value_counts()
    if set(class_counts.index) != {0, 1}:
        raise ValueError("Dataset must contain both human and AI classes.")
    if class_counts.min() < 4:
        raise ValueError(
            "Each class needs at least 4 samples for the stratified "
            "train/validation/test split."
        )
    if selected["sample_id"].duplicated().any():
        raise ValueError("Sample IDs must be unique.")
    return selected


def split_dataset(
    data: pd.DataFrame,
    random_seed: int = 42,
    test_size: float = 0.15,
    validation_size: float = 0.15,
) -> DatasetSplits:
    """Create stratified train, validation, and test partitions."""
    if test_size <= 0 or validation_size <= 0 or test_size + validation_size >= 1:
        raise ValueError("Split sizes must be positive and total less than 1.")

    train_validation, test = train_test_split(
        data,
        test_size=test_size,
        random_state=random_seed,
        stratify=data["label"],
    )
    validation_share = validation_size / (1 - test_size)
    train, validation = train_test_split(
        train_validation,
        test_size=validation_share,
        random_state=random_seed,
        stratify=train_validation["label"],
    )
    return DatasetSplits(
        train=train.reset_index(drop=True),
        validation=validation.reset_index(drop=True),
        test=test.reset_index(drop=True),
    )

