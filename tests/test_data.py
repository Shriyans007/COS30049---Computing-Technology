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
            "text": [f"document {index}" for index in range(40)],
            "label": [0, 1] * 20,
        }
    )

    first = split_dataset(data, random_seed=7)
    second = split_dataset(data, random_seed=7)

    assert first.train["sample_id"].tolist() == second.train["sample_id"].tolist()
    assert set(first.test["label"]) == {0, 1}

