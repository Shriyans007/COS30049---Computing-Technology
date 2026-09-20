"""Dataset loading, quality checks, and document-grouped splitting."""

import re
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from .features import NUMERIC_FEATURES, sentence_features


LABEL_NAMES = {0: "human", 1: "ai"}
LABEL_VALUES = {
    "0": 0, "human": 0, "human-written": 0, "human_written": 0,
    "1": 1, "ai": 1, "ai-generated": 1, "ai_generated": 1,
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
        raise ValueError(f"Unsupported label {value!r}. Expected human, ai, 0, or 1.")
    return LABEL_VALUES[key]


def _read_csv(path: Path, zip_member: str | None) -> pd.DataFrame:
    if path.suffix.lower() != ".zip":
        return pd.read_csv(path)
    with ZipFile(path) as archive:
        candidates = [name for name in archive.namelist() if name.endswith("clean_dataset.csv")]
        member = zip_member or (candidates[0] if len(candidates) == 1 else None)
        if not member or member not in archive.namelist():
            raise ValueError(
                "Could not uniquely locate clean_dataset.csv in the ZIP. "
                "Pass --zip-member with its archive path."
            )
        with archive.open(member) as csv_file:
            return pd.read_csv(csv_file)


def _add_or_repair_features(data: pd.DataFrame) -> pd.DataFrame:
    max_sent_id = data.groupby("doc_id")["sent_id"].transform("max")
    data["doc_pos"] = data["sent_id"] / max_sent_id.clip(lower=1)
    data["is_first_sent"] = data["sent_id"].eq(0).astype(int)
    data["is_last_sent"] = data["sent_id"].eq(max_sent_id).astype(int)

    missing_features = [name for name in NUMERIC_FEATURES if name not in data.columns]
    if missing_features:
        generated = []
        for index, row in data[["text", "sent_id"]].iterrows():
            generated.append(sentence_features(row["text"], int(row["sent_id"]), int(max_sent_id.loc[index]) + 1))
        generated_frame = pd.DataFrame(generated, index=data.index)
        for name in missing_features:
            data[name] = generated_frame[name]

    def average_word_length(text: str) -> float:
        words = re.findall(r"\b\w+\b", str(text))
        return sum(len(word) for word in words) / max(len(words), 1)

    # Person 2's file used sentence characters / word count. Repair it to the
    # actual average length of the words so spaces and punctuation are excluded.
    data["avg_word_len"] = data["text"].map(average_word_length)
    for feature in NUMERIC_FEATURES:
        data[feature] = pd.to_numeric(data[feature], errors="coerce")
    if data[NUMERIC_FEATURES].isna().any().any():
        raise ValueError("Engineered feature columns contain missing or non-numeric values.")
    if not np.isfinite(data[NUMERIC_FEATURES].to_numpy(dtype=float)).all():
        raise ValueError("Engineered feature columns contain infinite values.")
    return data


def _remove_duplicate_documents(data: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    document_text = (
        data.sort_values(["doc_id", "sent_id"])
        .groupby("doc_id", sort=False)["text"]
        .agg(" ".join)
    )
    duplicate_ids = set(document_text.index[document_text.duplicated(keep="first")])
    return data.loc[~data["doc_id"].isin(duplicate_ids)].copy(), len(duplicate_ids)


def _remove_sentence_overlap(data: pd.DataFrame) -> tuple[pd.DataFrame, int, int]:
    label_counts = data.groupby("text")["label"].nunique()
    conflicting_texts = set(label_counts.index[label_counts > 1])
    conflict_rows = int(data["text"].isin(conflicting_texts).sum())
    filtered = data.loc[~data["text"].isin(conflicting_texts)].copy()
    before_deduplication = len(filtered)
    filtered = filtered.drop_duplicates("text", keep="first")
    return filtered, conflict_rows, before_deduplication - len(filtered)


def load_dataset(
    path: str | Path,
    text_column: str = "text",
    label_column: str = "label",
    id_column: str | None = "id",
    zip_member: str | None = None,
    remove_exact_duplicates: bool = True,
) -> pd.DataFrame:
    """Load and standardise sentence rows while retaining document groups."""
    dataset_path = Path(path)
    if not dataset_path.is_file():
        raise FileNotFoundError(f"Dataset not found: {dataset_path}")
    raw = _read_csv(dataset_path, zip_member)
    missing = {text_column, label_column}.difference(raw.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

    data = pd.DataFrame()
    data["text"] = raw[text_column].fillna("").astype(str).str.strip()
    if (data["text"].str.len() == 0).any():
        raise ValueError("Dataset contains empty text values.")
    data["label"] = raw[label_column].map(_normalise_label)
    if "doc_id" in raw.columns:
        data["doc_id"] = raw["doc_id"]
    elif id_column and id_column in raw.columns:
        data["doc_id"] = raw[id_column]
    else:
        data["doc_id"] = raw.index
    data["sent_id"] = raw["sent_id"] if "sent_id" in raw.columns else 0
    data["source"] = raw["source"].fillna("unknown") if "source" in raw.columns else "unknown"
    data["prompt"] = raw["prompt"].fillna("unknown") if "prompt" in raw.columns else "unknown"
    for feature in NUMERIC_FEATURES:
        if feature in raw.columns:
            data[feature] = raw[feature]

    if data.duplicated(["doc_id", "sent_id"]).any():
        raise ValueError("Each doc_id/sent_id pair must be unique.")
    if (data.groupby("doc_id")["label"].nunique() > 1).any():
        raise ValueError("Every sentence in a document must have the same label.")
    if (data.groupby("doc_id")["source"].nunique() > 1).any():
        raise ValueError("Every sentence in a document must have the same source.")

    original_rows = len(data)
    original_documents = data["doc_id"].nunique()
    duplicate_documents_removed = conflicting_rows_removed = duplicate_sentence_rows_removed = 0
    if remove_exact_duplicates:
        data, duplicate_documents_removed = _remove_duplicate_documents(data)
        data, conflicting_rows_removed, duplicate_sentence_rows_removed = _remove_sentence_overlap(data)

    data = _add_or_repair_features(data)
    data["sample_id"] = data["doc_id"].astype(str) + ":" + data["sent_id"].astype(str)
    if data["sample_id"].duplicated().any():
        raise ValueError("Generated sample IDs are not unique.")
    document_counts = data.drop_duplicates("doc_id")["label"].value_counts()
    if set(document_counts.index) != {0, 1} or document_counts.min() < 4:
        raise ValueError("Each class needs at least 4 documents for grouped splitting.")

    data = data.reset_index(drop=True)
    data.attrs["audit"] = {
        "original_rows": original_rows,
        "original_documents": int(original_documents),
        "duplicate_documents_removed": duplicate_documents_removed,
        "conflicting_sentence_rows_removed": conflicting_rows_removed,
        "duplicate_sentence_rows_removed": duplicate_sentence_rows_removed,
        "final_rows": len(data),
        "final_documents": int(data["doc_id"].nunique()),
    }
    return data


def split_dataset(
    data: pd.DataFrame,
    random_seed: int = 42,
    test_size: float = 0.15,
    validation_size: float = 0.15,
) -> DatasetSplits:
    """Create stratified splits at document level to prevent sentence leakage."""
    if test_size <= 0 or validation_size <= 0 or test_size + validation_size >= 1:
        raise ValueError("Split sizes must be positive and total less than 1.")
    documents = data.drop_duplicates("doc_id")[["doc_id", "label"]]
    train_validation_docs, test_docs = train_test_split(
        documents, test_size=test_size, random_state=random_seed, stratify=documents["label"]
    )
    validation_share = validation_size / (1 - test_size)
    train_docs, validation_docs = train_test_split(
        train_validation_docs,
        test_size=validation_share,
        random_state=random_seed,
        stratify=train_validation_docs["label"],
    )

    def select(document_ids: pd.Series) -> pd.DataFrame:
        return data.loc[data["doc_id"].isin(set(document_ids))].reset_index(drop=True)

    return DatasetSplits(
        train=select(train_docs["doc_id"]),
        validation=select(validation_docs["doc_id"]),
        test=select(test_docs["doc_id"]),
    )
