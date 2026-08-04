"""Shared fixtures. Integration tests run against real Postgres — never a mock.

The schema is built once per session from the model metadata. Between tests
every table is truncated, which keeps the suite order-independent while still
letting the application code commit for real.
"""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from quecomemos.core.config import get_settings
from quecomemos.core.db import Base, get_db
from quecomemos.main import create_app
from quecomemos.models_registry import import_all_models

import_all_models()


def _test_database_url() -> str:
    settings = get_settings()
    return settings.test_database_url or settings.database_url


async def _ensure_database_exists(url: str) -> None:
    database_name = url.rsplit("/", 1)[-1]
    admin_url = url.rsplit("/", 1)[0] + "/postgres"
    admin_engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
    async with admin_engine.connect() as connection:
        exists = await connection.scalar(
            text("select 1 from pg_database where datname = :name"), {"name": database_name}
        )
        if not exists:
            await connection.execute(text(f'create database "{database_name}"'))
    await admin_engine.dispose()


@pytest.fixture(scope="session")
async def engine() -> AsyncIterator[AsyncEngine]:
    url = _test_database_url()
    await _ensure_database_exists(url)

    test_engine = create_async_engine(url)
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    yield test_engine
    await test_engine.dispose()


@pytest.fixture(autouse=True)
async def _clean_tables(engine: AsyncEngine) -> AsyncIterator[None]:
    yield
    table_names = ", ".join(f'"{table.name}"' for table in Base.metadata.sorted_tables)
    async with engine.begin() as connection:
        await connection.execute(text(f"truncate {table_names} restart identity cascade"))


@pytest.fixture
async def db(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session


@pytest.fixture
async def client(engine: AsyncEngine) -> AsyncIterator[AsyncClient]:
    app = create_app()

    async def override_get_db() -> AsyncIterator[AsyncSession]:
        async with AsyncSession(engine, expire_on_commit=False) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def _never_touch_the_dev_database() -> None:
    """Guard: a misconfigured TEST_DATABASE_URL must not truncate real data."""
    settings = get_settings()
    if settings.test_database_url is None:
        pytest.fail("TEST_DATABASE_URL must be set so tests never run against dev data")


@pytest.fixture
def api_prefix() -> str:
    return get_settings().api_prefix
