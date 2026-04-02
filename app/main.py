import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_v1_router
from app.core.config import Settings, get_settings
from app.core.logging import configure_logging
from app.core.version import read_project_version_from_pyproject


def create_app(settings: Settings) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Place startup/shutdown logic here (e.g. warm up caches, init telemetry, etc.)
        app.state.started_at = time.monotonic()
        app.state.version = read_project_version_from_pyproject()
        configure_logging(level=settings.log_level)
        yield

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )

    # CORS defaults are intentionally safe: credentials are disabled unless you explicitly
    # configure specific origins (never use allow_credentials=True with ["*"]).
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_v1_router, prefix=settings.api_v1_prefix)

    return app


# Uvicorn entrypoint: `uvicorn app.main:app --reload`
app = create_app(get_settings())
