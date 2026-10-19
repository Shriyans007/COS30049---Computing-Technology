from pathlib import Path

import pytest

from backend.app.model_service import ModelService


def test_missing_model_refuses_startup(tmp_path):
    with pytest.raises(RuntimeError, match="missing"):
        ModelService(tmp_path / "sentence.joblib", tmp_path / "document.joblib")
