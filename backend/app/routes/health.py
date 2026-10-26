from fastapi import APIRouter, Request

from ..schemas import HealthResponse, ModelInfoResponse


router = APIRouter(tags=["service"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Check API availability",
    description="Lightweight check that does not wait for an inference slot.",
)
async def health(request: Request) -> HealthResponse:
    return HealthResponse(status="ok", model_ready=hasattr(request.app.state, "model_service"))


@router.get(
    "/model-info",
    response_model=ModelInfoResponse,
    summary="Read model and input information",
    description="Returns public model names, class meanings, input limits and normalisation steps.",
)
async def model_info(request: Request) -> ModelInfoResponse:
    service = request.app.state.model_service
    settings = request.app.state.settings
    return ModelInfoResponse(
        sentence_model=service.sentence_name,
        document_model=service.document_name,
        class_mapping={"0": "human", "1": "ai"},
        limits={
            "minimum_characters": settings.min_characters,
            "maximum_characters": settings.max_characters,
            "maximum_utf8_bytes": settings.max_bytes,
            "maximum_sentences": settings.max_sentences,
        },
        normalisation=[
            "Unicode NFKC", "zero-width character removal", "whitespace normalisation",
            "limited Latin-look-alike mapping",
        ],
    )
