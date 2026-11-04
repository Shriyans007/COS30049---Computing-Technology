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
    text: str = Field(description="Plain text to assess. It is never interpreted as HTML.")


class ConfidenceRange(BaseModel):
    lower: float = Field(ge=0, le=1)
    upper: float = Field(ge=0, le=1)
    method: str


class SentencePrediction(BaseModel):
    text: str
    label: Literal["human", "ai"]
    ai_probability: float = Field(ge=0, le=1)


class PredictionResponse(BaseModel):
    prediction: Literal["human", "ai"]
    ai_probability: float = Field(ge=0, le=1)
    confidence: float = Field(ge=0, le=1)
    confidence_range: ConfidenceRange | None = None
    sentence_results: list[SentencePrediction]
    normalisation_applied: bool


class HealthResponse(BaseModel):
    status: Literal["ok"]
    model_ready: bool


class ModelInfoResponse(BaseModel):
    sentence_model: str
    document_model: str
    class_mapping: dict[str, str]
    limits: dict[str, int]
    normalisation: list[str]


class ErrorBody(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorBody
