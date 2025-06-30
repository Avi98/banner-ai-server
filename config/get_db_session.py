from typing import AsyncGenerator
from models.banner_var_model import Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from config.db_config import AsyncSessionLocal
from config.env_variables import get_settings

settings = get_settings()


async def init_db():
    try:
        engine = create_async_engine(settings.get_database_url, echo=True)

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        await engine.dispose()
    except Exception as e:
        print(f"Database initialization failed: {e}")
        print(f"Database URL: {settings.DATABASE_URL}")  # Remove password in production
        raise


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
