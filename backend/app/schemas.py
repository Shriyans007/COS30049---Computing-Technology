"""Pydantic API contracts."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class PredictionRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "text": (
                        "Furthermore, this comprehensive explanation demonstrates how "
                        "artificial intelligence can support structured analysis."
                    )
                }
            ]
        }
    )
    text: str = Field(
        min_length=1,
        max_length=10_000,
        description="Plain text to assess. It is never interpreted as HTML.",
    )


class ConfidenceRange(BaseModel):
    lower: float = Field(ge=0, le=1)
    upper: float = Field(ge=0, le=1)
    method: str


class SentencePrediction(BaseModel):
    text: str
    label: Literal["human", "ai"]
    ai_probability: float = Field(ge=0, le=1)


class PredictionResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "prediction": "ai",
                "ai_probability": 0.91,
                "confidence": 0.91,
                "confidence_range": {
                    "lower": 0.84,
                    "upper": 0.96,
                    "method": "95% bootstrap interval across sentence AI probabilities",
                },
                "sentence_results": [
                    {"text": "Example sentence.", "label": "ai", "ai_probability": 0.93}
                ],
                "normalisation_applied": False,
            }
        }
    )
    prediction: Literal["human", "ai"]
    ai_probability: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    confidence_range: ConfidenceRange | None = None
    sentence_results: list[SentencePrediction]
    normalisation_applied: bool


class HealthResponse(BaseModel):
    model_config = ConfigDict(json_schema_extra={"example": {"status": "ok", "model_ready": True}})
    status: Literal["ok"]
    model_ready: bool


class ModelInfoResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "sentence_model": "Logistic Regression",
                "document_model": "Linear SVM",
                "class_mapping": {"0": "human", "1": "ai"},
                "limits": {
                    "minimum_characters": 20,
                    "maximum_characters": 10000,
                    "maximum_utf8_bytes": 40000,
                    "maximum_sentences": 100,
                },
                "normalisation": ["Unicode NFKC", "zero-width character removal"],
            }
        }
    )
    sentence_model: str
    document_model: str
    class_mapping: dict[str, str]
    limits: dict[str, int]
    normalisation: list[str]


class ErrorBody(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": {
                    "code": "TEXT_TOO_LARGE",
                    "message": "Text must not exceed the configured limits.",
                }
            }
        }
    )
    error: ErrorBody
