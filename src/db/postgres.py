from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import clear_mappers

from src.infrastructure.models import mapper_registry

engine: AsyncEngine | None = None
async_session_maker: async_sessionmaker[AsyncSession] | None = None


async def get_session() -> AsyncSession:  # type: ignore
    async with async_session_maker() as session:
        yield session


async def create_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.create_all)


async def purge_database() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(mapper_registry.metadata.drop_all)
    clear_mappers()
