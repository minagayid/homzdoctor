"""
Database configuration and setup for HomzDoctor.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

from core.config import settings

# SQLite needs check_same_thread disabled for async use; other drivers take no extra args.
connect_args = (
    {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

# Create async engine. The driver is chosen entirely by DATABASE_URL:
#   - prototype: sqlite+aiosqlite:///./homzdoctor.db
#   - production: postgresql+asyncpg://user:pass@host:5432/dbname
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    poolclass=NullPool,
    connect_args=connect_args,
)

# Create async session
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

# Base model for SQLAlchemy
Base = declarative_base()


async def get_db():
    """Get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    # Import models so their tables register on Base.metadata before create_all.
    import models.medical  # noqa: F401

    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)
