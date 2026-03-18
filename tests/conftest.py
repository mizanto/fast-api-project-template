from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings, get_settings
from app.db.session import dispose_all_engines
from app.main import create_app


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        app_name="Test App",
        database_url="sqlite+aiosqlite:///:memory:",
        debug=True,
        log_level="DEBUG",
    )


@pytest.fixture
async def async_client(test_settings: Settings) -> AsyncGenerator[AsyncClient, None]:
    test_app = create_app(test_settings)
    test_app.dependency_overrides[get_settings] = lambda: test_settings
    async with AsyncClient(
        transport=ASGITransport(app=test_app),
        base_url="http://test",
    ) as client:
        yield client
    test_app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
async def cleanup_engines():
    yield
    await dispose_all_engines()

