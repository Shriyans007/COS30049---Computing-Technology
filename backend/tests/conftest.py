import os

import pytest
from fastapi.testclient import TestClient

from backend.app.config import get_settings


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("A3_RATE_LIMIT_REQUESTS", "1000")
    get_settings.cache_clear()
    from backend.app.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client
    get_settings.cache_clear()


@pytest.fixture
def valid_text():
    return (
        "Furthermore, this comprehensive discussion evaluates the important factors. "
        "In conclusion, the structured approach provides a robust overall explanation."
    )
