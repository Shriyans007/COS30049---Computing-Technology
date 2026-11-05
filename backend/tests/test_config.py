import pytest

from backend.app.config import REPOSITORY_ROOT, Settings


@pytest.mark.parametrize(
    "configured_value",
    [
        "http://localhost:5173,http://127.0.0.1:5173",
        '["http://localhost:5173", "http://127.0.0.1:5173"]',
    ],
)
def test_allowed_origins_accepts_documented_and_json_formats(
    monkeypatch, configured_value
):
    monkeypatch.setenv("A3_ALLOWED_ORIGINS", configured_value)
    settings = Settings(_env_file=None)
    assert settings.allowed_origins == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


def test_committed_environment_example_can_be_loaded():
    settings = Settings(_env_file=REPOSITORY_ROOT / "backend" / ".env.example")
    settings.validate_security()
