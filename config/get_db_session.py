from core.utils.logger import Logger
from models.banner_var_model import Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine

from config.db_config import asyncSession
from config.env_variables import get_settings

settings = get_settings()



async def init_db():
    logger = Logger.get_logger(
    name=__name__,
)
    
    try:
        engine = create_async_engine(settings.get_database_url, echo=True)

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        await engine.dispose()
    except Exception as e:
        logger.info(f"Database initialization failed: {e}")
        logger.info(f"Database URL: {settings.get_database_url}")


async def get_db() -> AsyncSession:
     session = await asyncSession()
    
     async with session() as db_session:
            try:
                return db_session
            finally:
                 await db_session.aclose()
     
