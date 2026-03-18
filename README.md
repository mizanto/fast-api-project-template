# Template FastAPI Project

Opinionated FastAPI template with:

- **Async SQLAlchemy** (`AsyncSession`) + Unit of Work
- **Pydantic Settings** (`.env` support)
- **Alembic** (async `env.py`) for migrations
- **CORS** middleware enabled (configurable)
- **Logging** setup wired into app lifespan
- **Tests scaffold** showing `dependency_overrides`

## Prerequisites

- **Python**: 3.12+
- **pip** and a virtual environment tool (`venv`, `uv`, etc.)

## Quickstart (local)

Create and activate a virtual environment, then install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create `.env` from the example:

```bash
cp .env.example .env
```

Run the app:

```bash
uvicorn app.main:app --reload
```

Health check:

- `GET /api/v1/health`

## Configuration

Configuration lives in `app/core/config.py` and is loaded from `.env` (see `.env.example`).

Important variables:

- **`APP_NAME`**: shown in OpenAPI title
- **`DEBUG`**: enables debug mode and SQLAlchemy echo
- **`LOG_LEVEL`**: default log verbosity (must be one of `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`; invalid values will raise at startup)
- **`API_V1_PREFIX`**: default `/api/v1`
- **`DATABASE_URL`**:
  - SQLite (async): `sqlite+aiosqlite:///./app.db`
  - PostgreSQL (async): `postgresql+asyncpg://user:pass@host:5432/dbname` (requires adding `asyncpg`)
- **`CORS_ALLOWED_ORIGINS`**: controls which origins are allowed by CORS middleware.
  - `*` or empty string: allow all origins.
  - Single origin: `https://example.com`
  - Multiple origins (comma-separated): `https://example.com,https://admin.example.com`

## Architecture

This template uses a simple layering approach:

- **router (API layer)**: parses/validates input and returns DTOs
- **service (business logic)**: orchestrates use-cases
- **Unit of Work (transaction)**: groups writes/reads that must succeed together
- **repository (data access)**: isolates persistence concerns and uses `AsyncSession`

```mermaid
flowchart TD
    router --> service[Service (business logic)]
    service --> uow[UnitOfWork (transaction)]
    uow --> repo[Repository (data access)]
```

### Example: router -> service (UoW) -> repo

The following is a self-contained example to illustrate the layering pattern; it does not
correspond to a concrete module in this template.

```python
class Item(BaseModel):
    name: str


class ItemRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list(self) -> list[Item]:
        # Placeholder example. Replace with your ORM model.
        result = await self._session.execute(select(Item.name))
        return list(result.scalars())


class ItemService:
    def __init__(self, uow_factory: Callable[[], UnitOfWork]) -> None:
        self._uow_factory = uow_factory

    async def list_items(self) -> list[Item]:
        async with self._uow_factory() as uow:
            repo = ItemRepo(uow.session)
            return await repo.list()


@router.get("/items")
async def list_items_route() -> dict[str, list[Item]]:
    # The service uses UnitOfWork internally, so this route doesn't need to inject get_db().
    service = ItemService(uow_factory=UnitOfWork)
    items = await service.list_items()
    return {"items": items}
```

## Database migrations (Alembic)

Apply existing migrations:

```bash
alembic upgrade head
```

Create a new migration (autogenerate diffs from `Base.metadata`):

```bash
alembic revision --autogenerate -m "your message"
```

## Testing

Install dev dependencies:

```bash
pip install -r requirements-dev.txt
```

Run tests:

```bash
pytest
```

The tests demonstrate overriding settings via:
`app.dependency_overrides[get_settings] = lambda: test_settings`.

## Docker

Build:

```bash
docker build -t fastapi-template .
```

Run:

```bash
docker run --rm -p 8000:8000 fastapi-template
```

The Docker image is intended as a lean production runtime image: it includes only
application (non-test) dependencies and is not meant for running the test suite inside
the container.

## Project structure

```text
app/
  api/v1/
    routes/
      health.py
    router.py
  core/
    config.py
    logging.py
  db/
    base.py
    session.py
    uow.py
  main.py
migrations/
  env.py
  versions/
alembic.ini
requirements.txt
requirements-dev.txt
pyproject.toml
```
