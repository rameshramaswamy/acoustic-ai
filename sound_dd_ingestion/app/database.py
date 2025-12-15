from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings
from typing import AsyncGenerator

# OPTIMIZATION: Use asyncpg driver for non-blocking I/O
# Ensure URL is postgresql+asyncpg://...
ASYNC_DB_URL = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

engine = create_async_engine(
    ASYNC_DB_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=20, # Enterprise tuning: larger pool
    max_overflow=10
)

# Async Session Factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()

# Dependency for FastAPI (Async)
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session