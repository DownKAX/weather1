from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.auth.redis_repository import get_session
from app.core.settings import settings

DB_URL = settings.DATABASE_URL
engine = create_async_engine(DB_URL, echo=False)
AsyncSessionMaker = async_sessionmaker(autocommit=False, bind=engine, expire_on_commit=False, class_=AsyncSession)

async def get_session():
    async with AsyncSessionMaker() as session:
        yield session