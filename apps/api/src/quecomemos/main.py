"""Application factory for the Que Comemos? API."""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from quecomemos.core.config import Settings, get_settings
from quecomemos.core.db import dispose_engine
from quecomemos.core.errors import register_exception_handlers
from quecomemos.features.auth.router import router as auth_router
from quecomemos.features.user.router import router as user_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    logger.info("api starting")
    yield
    await dispose_engine()
    logger.info("api stopped")


def _configure_cors(app: FastAPI, settings: Settings) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Que Comemos? API",
        version="0.1.0",
        docs_url=f"{settings.api_prefix}/docs",
        openapi_url=f"{settings.api_prefix}/openapi.json",
        lifespan=lifespan,
    )
    _configure_cors(app, settings)
    register_exception_handlers(app)

    @app.get(f"{settings.api_prefix}/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(auth_router, prefix=settings.api_prefix)
    app.include_router(user_router, prefix=settings.api_prefix)

    return app


app = create_app()
