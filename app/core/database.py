from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import config

db_connection_str = f"postgresql+asyncpg://{config.db_username}:{config.db_password}@\
{config.db_host}:{config.db_port}/{config.db_name}"
async_engine = create_async_engine(db_connection_str, echo=True)


# Get asynchroneous session for database
async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
