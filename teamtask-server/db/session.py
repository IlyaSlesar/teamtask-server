from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from settings import settings

from db.base import Base


engine = create_async_engine(
    settings.database_url,
    echo=settings.sqlalchemy_echo
)

AsyncSessionLocal = async_sessionmaker(bind=engine)


async def get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
