import logging
from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings

log = logging.getLogger(__name__)
router = APIRouter(tags=["health"])


@router.get("/health")
async def health(
    settings: Annotated[Settings, Depends(get_settings)],
) -> dict[str, str]:
    log.info("Health check endpoint called")
    return {"status": "ok", "app": settings.app_name}
