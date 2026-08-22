"""
DocTensor FastAPI application.

Run locally:
    uvicorn doctensor.api.app:app --reload --port 8000

Run with Docker Compose:
    docker-compose up
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from doctensor.api.config import get_settings
from doctensor.api.routes.health import router as health_router
from doctensor.api.routes.extract import router as extract_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure storage root exists
    settings = get_settings()
    if settings.storage_backend == "local":
        import os
        os.makedirs(settings.storage_root, exist_ok=True)
    yield
    # Shutdown: nothing special needed


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "DocTensor — Universal Document Extraction API.\n\n"
            "Supports PDF (native + scanned), JPG, PNG and more.\n"
            "Outputs structured JSON or Markdown."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS — permissive for local dev; tighten in production via env
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Routers
    app.include_router(health_router)
    app.include_router(extract_router)

    return app


# Module-level app instance (used by uvicorn)
app = create_app()
