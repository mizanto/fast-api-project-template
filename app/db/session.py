from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings, get_settings

# Default database is SQLite using async driver (aiosqlite):
#   sqlite+aiosqlite:///./app.db
#
# To migrate to PostgreSQL, change `DATABASE_URL` to something like:
#   postgresql+asyncpg://user:pass@host:5432/dbname
# and add `asyncpg` dependency.
_engine_cache: dict[str, AsyncEngine] = {}
_sessionmaker_cache: dict[str, async_sessionmaker[AsyncSession]] = {}
# These caches make engine/sessionmaker creation lazy and override-friendly (tests can swap
# Settings without paying import-time side effects). If you use multiple DB URLs in tests,
# call dispose_all_engines() in teardown to avoid leaking pools across runs.


def _cache_key(settings: Settings) -> str:
    return f"{settings.database_url}|echo={settings.debug}"


def get_engine(settings: Settings) -> AsyncEngine:
    key = _cache_key(settings)
    if key in _engine_cache:
        return _engine_cache[key]

    is_sqlite = settings.database_url.startswith("sqlite")

    # SQLite-only: allow using connections across threads (useful with dev reloaders).
    # For Postgres/MySQL this is ignored.
    connect_args = {"check_same_thread": False} if is_sqlite else {}

    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        connect_args=connect_args,
    )
    _engine_cache[key] = engine
    return engine


def get_sessionmaker(settings: Settings) -> async_sessionmaker[AsyncSession]:
    key = _cache_key(settings)
    if key in _sessionmaker_cache:
        return _sessionmaker_cache[key]

    engine = get_engine(settings)

    # expire_on_commit=False -> after commit objects are not "expired" automatically.
    sessionmaker = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    _sessionmaker_cache[key] = sessionmaker
    return sessionmaker


async def get_db(
    settings: Annotated[Settings, Depends(get_settings)],
) -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency.
    For each request create a separate session and close it guaranteedly.
    """
    sessionmaker = get_sessionmaker(settings)
    async with sessionmaker() as session:
        yield session


async def dispose_all_engines() -> None:
    """Call in test teardown or app shutdown to close all engine connection pools."""
    for engine in _engine_cache.values():
        await engine.dispose()
    _engine_cache.clear()
    _sessionmaker_cache.clear()
