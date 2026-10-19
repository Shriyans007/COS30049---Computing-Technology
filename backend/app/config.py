"""Environment-backed API configuration."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=REPOSITORY_ROOT / ".env", env_prefix="A3_", extra="ignore"
    )

    app_name: str = "AI Content Detector API"
    environment: str = "development"
    allowed_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )
    sentence_model_path: Path = REPOSITORY_ROOT / "artifacts/classification/final_text_classifier.joblib"
    document_model_path: Path = REPOSITORY_ROOT / "artifacts/document_classification/final_text_classifier.joblib"
    min_characters: int = 20
    max_characters: int = 10_000
    max_bytes: int = 40_000
    max_sentences: int = 100
    max_concurrent_inferences: int = 2
    inference_queue_timeout_seconds: float = 0.05
    inference_timeout_seconds: float = 15.0
    rate_limit_requests: int = 60
    rate_limit_window_seconds: int = 60
    experiment_mode: bool = False
    dos_protection_enabled: bool = True
    inference_test_delay_ms: int = 0

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_origins(cls, value: object) -> object:
        if isinstance(value, str) and not value.lstrip().startswith("["):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value

    def validate_security(self) -> None:
        if not self.allowed_origins or "*" in self.allowed_origins:
            raise RuntimeError("A3_ALLOWED_ORIGINS must list explicit trusted origins.")
        if not self.dos_protection_enabled and not self.experiment_mode:
            raise RuntimeError("DoS protection can only be disabled in explicit experiment mode.")
        if self.inference_test_delay_ms and not self.experiment_mode:
            raise RuntimeError("Artificial inference delay is restricted to experiment mode.")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate_security()
    return settings
