from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(settings.DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

class Base(DeclarativeBase):
    pass

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# sync URL for Celery — replace asyncpg with psycopg2
SYNC_DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql+asyncpg", "postgresql+psycopg2"
)

sync_engine = create_engine(SYNC_DATABASE_URL)

SyncSessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False
)