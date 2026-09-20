import pandas as pd
import pytest

from classification.data import load_dataset, split_dataset


def test_load_dataset_normalises_supported_labels(tmp_path):
    path = tmp_path / "dataset.csv"
    pd.DataFrame(
        {
            "id": range(8),
            "text": [f"sample {index}" for index in range(8)],
            "label": ["human"] * 4 + ["AI"] * 4,
        }
    ).to_csv(path, index=False)

    data = load_dataset(path)

    assert data["label"].tolist() == [0, 0, 0, 0, 1, 1, 1, 1]


def test_load_dataset_rejects_missing_columns(tmp_path):
    path = tmp_path / "dataset.csv"
    pd.DataFrame({"body": ["example"], "label": ["human"]}).to_csv(path, index=False)

    with pytest.raises(ValueError, match="missing required columns"):
        load_dataset(path)


def test_split_dataset_is_reproducible():
    data = pd.DataFrame(
        {
            "sample_id": range(40),
            "doc_id": range(40),
            "text": [f"document {index}" for index in range(40)],
            "label": [0, 1] * 20,
        }
    )

    first = split_dataset(data, random_seed=7)
    second = split_dataset(data, random_seed=7)

    assert first.train["sample_id"].tolist() == second.train["sample_id"].tolist()
    assert set(first.test["label"]) == {0, 1}
    assert set(first.train["doc_id"]).isdisjoint(first.validation["doc_id"])
    assert set(first.train["doc_id"]).isdisjoint(first.test["doc_id"])
    assert set(first.validation["doc_id"]).isdisjoint(first.test["doc_id"])


def test_load_dataset_keeps_document_sentences_together_and_repairs_features(tmp_path):
    path = tmp_path / "sentences.csv"
    rows = []
    for document in range(8):
        label = document % 2
        for sentence in range(2):
            rows.append(
                {
                    "doc_id": document,
                    "sent_id": sentence,
                    "text": f"Unique document {document} sentence {sentence} words.",
                    "label": label,
                    "avg_word_len": 999,
                }
            )
    pd.DataFrame(rows).to_csv(path, index=False)

    data = load_dataset(path)
    splits = split_dataset(data)

    assert data["avg_word_len"].max() < 20
    assert set(data.loc[data["is_last_sent"] == 1, "sent_id"]) == {1}
    split_for_document = {}
    for name, frame in (("train", splits.train), ("validation", splits.validation), ("test", splits.test)):
        for document_id in frame["doc_id"].unique():
            assert document_id not in split_for_document
            split_for_document[document_id] = name
