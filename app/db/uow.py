from collections.abc import Callable
from types import TracebackType

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_sessionmaker


class UnitOfWork:
    """
    Unit of Work pattern implementation.

    Examples:
        Service injecting a factory:
            class ItemService:
                def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
                    self._uow_factory = uow_factory

                async def list_items(self) -> list[Item]:
                    async with self._uow_factory() as uow:
                        repo = ItemRepo(uow.session)
                        return await repo.list()

        In tests, prefer passing an explicit ``session_factory`` to avoid
        coupling UnitOfWork to global settings.
    """

    def __init__(
        self,
        session_factory: Callable[[], AsyncSession] | None = None,
        settings: Settings | None = None,
    ) -> None:
        if session_factory is None:
            effective_settings = settings or get_settings()
            session_factory = get_sessionmaker(effective_settings)

        self.session_factory = session_factory
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> "UnitOfWork":
        self.session = self.session_factory()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self.session is None:
            return

        try:
            if exc_type is not None:
                await self.session.rollback()
        finally:
            await self.session.close()

    async def commit(self) -> None:
        if self.session is None:
            raise RuntimeError(
                "UnitOfWork session is not initialized. Use 'async with UnitOfWork()'."
            )
        await self.session.commit()

    async def rollback(self) -> None:
        if self.session is None:
            raise RuntimeError(
                "UnitOfWork session is not initialized. Use 'async with UnitOfWork()'."
            )
        await self.session.rollback()
