import logging
import time
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_db

log = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health")
async def health(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, str]:
    """
    Health check endpoint

    Returns:
        dict[str, str]: A dictionary with the status, database, environment, version, and uptime
        - status: "ok" if the application is healthy, "error" if it is not
        - database: "connected" if the database is connected, "disconnected" if it is not
        - is_debug: whether the application is running in debug mode
        - version: the version of the application
        - uptime: the uptime of the application

    Example:
        {
            status: "ok",
            database: "connected",
            is_debug: true,
            version: "1.0.0",
            uptime: "100 seconds"
        }
    """
    log.info("Health check endpoint called")
    try:
        await db.execute(text("SELECT 1"))
    except Exception as e:
        log.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection error") from e

    uptime = time.monotonic() - request.app.state.started_at
    uptime_str = f"{uptime:.2f} seconds"
    return {
        "status": "ok",
        "database": "connected",
        "is_debug": str(settings.debug),
        "version": str(request.app.state.version),
        "uptime": uptime_str,
    }
