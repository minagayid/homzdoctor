"""
Database configuration and setup for HomzDoctor.
"""

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool

from core.config import settings

LOG = logging.getLogger("homzdoctor.database")


def _build_connect_args() -> dict:
    """Driver-specific connect kwargs.

    - SQLite (aiosqlite): allow cross-thread use.
    - Postgres (asyncpg): enable TLS when the original URL asked for it. We strip
      libpq's ``sslmode`` in config.normalize_database_url (asyncpg rejects it),
      so re-enable encryption here via asyncpg's own ``ssl`` kwarg whenever a
      remote/managed host is used (Railway's public proxy requires TLS).
    """
    if settings.DATABASE_URL.startswith("sqlite"):
        return {"check_same_thread": False}
    if "asyncpg" in settings.DATABASE_URL:
        import os

        # Managed providers (Railway public proxy, Supabase, Neon…) require TLS.
        # Default ON unless explicitly disabled, but skip it for a local host.
        host_is_local = any(h in settings.DATABASE_URL for h in ("@localhost", "@127.0.0.1", "@postgres", "@db"))
        want_ssl = os.getenv("DATABASE_SSL", "auto").lower()
        if want_ssl == "off" or (want_ssl == "auto" and host_is_local):
            return {}
        return {"ssl": True}
    return {}


# Warn loudly if we're about to run on ephemeral SQLite in production: on
# Railway the container filesystem is wiped on every redeploy, so every
# registered account (and login) silently disappears. Set DATABASE_URL to a
# managed Postgres to persist data — see DEPLOYMENT.md.
if settings.is_sqlite and settings.is_production:
    LOG.warning(
        "⚠️  Using SQLite (%s) in a production-like environment. On Railway the "
        "filesystem is EPHEMERAL — all users/records will be lost on the next "
        "redeploy. Set DATABASE_URL to a Postgres instance. See DEPLOYMENT.md.",
        settings.DATABASE_URL,
    )

# Create async engine. The driver is chosen entirely by DATABASE_URL:
#   - prototype: sqlite+aiosqlite:///./homzdoctor.db
#   - production: postgresql+asyncpg://user:pass@host:5432/dbname
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    poolclass=NullPool,
    connect_args=_build_connect_args(),
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


async def check_db() -> dict:
    """Lightweight connectivity probe used by the /status endpoint."""
    info = {
        "connected": False,
        "dialect": "sqlite" if settings.is_sqlite else "postgresql",
        "ephemeral": settings.is_sqlite,
        "url_host": settings.DATABASE_URL.rsplit("@", 1)[-1] if "@" in settings.DATABASE_URL else "local",
    }
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        info["connected"] = True
    except Exception as exc:  # pragma: no cover - surfaced in status payload
        info["error"] = str(exc)
    return info
