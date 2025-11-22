from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.settings import settings

DB_URL = settings.DATABASE_URL
def get_session_maker():
    engine = create_async_engine(DB_URL, echo=False, future=True)
    return async_sessionmaker(autocommit=False, bind=engine, expire_on_commit=False, class_=AsyncSession)

engine = create_async_engine(DB_URL, echo=False, future=True)
AsyncSessionMaker = async_sessionmaker(autocommit=False, bind=engine, expire_on_commit=False, class_=AsyncSession)
async def get_session():
    async with AsyncSessionMaker() as session:
        yield session