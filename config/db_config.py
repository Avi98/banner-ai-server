from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from config.env_variables import get_settings

settings = get_settings()

print(f"database url: {settings.get_database_url}")

engine = create_async_engine(settings.get_database_url, echo=True)

async def asyncSession():
	return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False) 
# AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
