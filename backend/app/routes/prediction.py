from fastapi import APIRouter, Request

from ..errors import AppError
from ..schemas import ErrorResponse, PredictionRequest, PredictionResponse
from ..validation import validate_prediction_text


router = APIRouter(tags=["prediction"])


@router.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Analyse writing",
    description=(
        "Validates and normalises plain text, uses the document classifier for the overall result, "
        "and uses the sentence classifier for sentence-level probabilities."
    ),
    responses={
        400: {"model": ErrorResponse, "description": "Empty, short or unsafe input"},
        413: {"model": ErrorResponse, "description": "Character, byte or sentence limit exceeded"},
        429: {"model": ErrorResponse, "description": "Per-client request limit exceeded"},
        503: {"model": ErrorResponse, "description": "Inference capacity or timeout exceeded"},
    },
)
async def predict(data: PredictionRequest, request: Request) -> PredictionResponse:
    settings = request.app.state.settings
    text = validate_prediction_text(data.text, settings)
    client = request.client.host if request.client else "unknown"
    if not await request.app.state.rate_limiter.allow(client):
        raise AppError(429, "RATE_LIMITED", "Too many requests. Please retry after the rate-limit window.")

    service = request.app.state.model_service

    if settings.dos_protection_enabled:
        result = await request.app.state.inference_gate.run_sync(lambda: service.predict(text))
    else:
        import asyncio
        result = await asyncio.to_thread(service.predict, text)
    return PredictionResponse.model_validate(result)
