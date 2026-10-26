"""FastAPI application factory and lifespan-managed model loading."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings
from .errors import error_payload, install_error_handlers
from .model_service import ModelService
from .routes.health import router as health_router
from .routes.prediction import router as prediction_router
from .security import InferenceGate, SlidingWindowRateLimiter


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    app.state.model_service = ModelService(
        settings.sentence_model_path,
        settings.document_model_path,
        settings.inference_test_delay_ms,
    )
    app.state.inference_gate = InferenceGate(
        settings.max_concurrent_inferences,
        settings.inference_queue_timeout_seconds,
        settings.inference_timeout_seconds,
    )
    app.state.rate_limiter = SlidingWindowRateLimiter(
        settings.rate_limit_requests, settings.rate_limit_window_seconds
    )
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="Secure API around the team's Assignment 2 AI-content classifiers.",
        lifespan=lifespan,
        debug=False,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Accept"],
    )

    @app.middleware("http")
    async def require_json_and_bound_body(request: Request, call_next):
        if request.method == "POST" and request.url.path == "/api/v1/predict":
            content_type = request.headers.get("content-type", "").split(";", 1)[0].lower()
            if content_type != "application/json":
                return JSONResponse(error_payload("UNSUPPORTED_MEDIA_TYPE", "Content-Type must be application/json."), status_code=415)
            length = request.headers.get("content-length")
            if length and length.isdigit() and int(length) > settings.max_bytes + 1_000:
                return JSONResponse(error_payload("REQUEST_TOO_LARGE", "The request body is too large."), status_code=413)
        return await call_next(request)

    install_error_handlers(app)
    app.include_router(health_router, prefix="/api/v1")
    app.include_router(prediction_router, prefix="/api/v1")
    return app


app = create_app()
