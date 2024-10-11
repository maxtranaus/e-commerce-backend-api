from datetime import timedelta
from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import config, test_data
from app.core.database import db_connection_str, get_async_session
from app.main import app
from app.models.user import User
from app.services.auth_service import create_access_token

db_name = f"{config.db_name}_test"
test_db_connection_str = f"postgresql+asyncpg://{config.db_username}:{config.db_password}@\
{config.db_host}:{config.db_port}/{db_name}"


@pytest_asyncio.fixture(scope="session")
async def test_engine() -> AsyncGenerator[AsyncEngine, None]:
    assert test_db_connection_str != db_connection_str
    engine: AsyncEngine = create_async_engine(
        f"""postgresql+asyncpg://postgres:{config.db_password}@{config.db_host}:{config.db_port}
            /postgres""",
        isolation_level="AUTOCOMMIT",
    )
    async with engine.connect() as conn:
        await conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
        await conn.execute(text(f"CREATE DATABASE {db_name}"))
    test_db_engine = create_async_engine(
        test_db_connection_str,
        isolation_level="AUTOCOMMIT",
    )
    yield test_db_engine
    await test_db_engine.dispose()
    async with engine.connect() as conn:
        await conn.execute(text(f"DROP DATABASE IF EXISTS {db_name}"))
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_session(test_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    session = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)
    async with session() as s:
        async with test_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        yield s

    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await test_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def admin_user(async_session: AsyncSession) -> AsyncGenerator[User, None]:
    user = User(
        id=test_data["initial_user"]["admin"]["id"],
        email=test_data["initial_user"]["admin"]["email"],
        name=test_data["initial_user"]["admin"]["name"],
        password=test_data["initial_user"]["admin"]["password"],  # admin
        role=test_data["initial_user"]["admin"]["role"],
    )
    async_session.add(user)
    yield user


@pytest_asyncio.fixture(scope="function")
async def normal_user(async_session: AsyncSession) -> AsyncGenerator[User, None]:
    user = User(
        id=test_data["initial_user"]["user"]["id"],
        email=test_data["initial_user"]["user"]["email"],
        name=test_data["initial_user"]["user"]["name"],
        password=test_data["initial_user"]["user"]["password"],  # admin
        role=test_data["initial_user"]["user"]["role"],
    )
    async_session.add(user)
    yield user


@pytest_asyncio.fixture(scope="function")
async def client(async_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    app.dependency_overrides[get_async_session] = lambda: async_session
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://localhost:8081"  # type: ignore
    ) as c:
        yield c


@pytest_asyncio.fixture(scope="function")
async def admin_token() -> str:
    return create_access_token(
        test_data["initial_user"]["admin"]["email"],
        test_data["initial_user"]["admin"]["id"],
        test_data["initial_user"]["admin"]["role"],
        timedelta(minutes=20),
    )


@pytest_asyncio.fixture(scope="function")
async def user_token() -> str:
    return create_access_token(
        test_data["initial_user"]["user"]["email"],
        test_data["initial_user"]["user"]["id"],
        test_data["initial_user"]["user"]["role"],
        timedelta(minutes=20),
    )
