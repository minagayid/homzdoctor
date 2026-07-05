"""
Configuration management for HomzDoctor backend.
"""

import os
from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Absolute path to the backend directory (this file lives in backend/core/).
# Used to anchor both the .env file and the SQLite database so they resolve to
# the SAME files no matter which working directory the server is launched from.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load THIS project's .env by absolute path with override=True, so its values
# win over any global/system env vars left over from another project (e.g. a
# system-wide DATABASE_URL pointing at a different database). Passing the
# explicit path is essential: load_dotenv() with no path only searches upward
# from the current working directory, so launching from outside backend/ would
# miss this file and silently fall back to the leftover system DATABASE_URL.
load_dotenv(BASE_DIR / ".env", override=True)


from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

# Query-string params that libpq/psycopg understand but asyncpg does NOT accept
# as connect kwargs. Railway's *public* Postgres proxy URL often appends
# ``?sslmode=require`` (and sometimes ``channel_binding``); passing those to the
# asyncpg driver raises "connect() got an unexpected keyword argument 'sslmode'".
# We strip them here and re-enable TLS via ``connect_args`` in core/database.py.
_ASYNCPG_INCOMPATIBLE_PARAMS = {"sslmode", "channel_binding", "gssencmode", "target_session_attrs"}


def normalize_database_url(url: str) -> str:
    """Return a URL the async SQLAlchemy engine can actually open.

    Handles the two real-world footguns that made HomzDoctor "lose" accounts:

    1. **Railway / Heroku Postgres schemes.** They inject ``DATABASE_URL`` as
       ``postgres://…`` or ``postgresql://…`` (the *sync* libpq form). The async
       engine needs the ``+asyncpg`` driver, so we rewrite the scheme and drop
       libpq-only query params (e.g. ``sslmode``) that asyncpg rejects.

    2. **Relative SQLite paths.** ``sqlite+aiosqlite:///./homzdoctor.db`` resolves
       against the *current working directory*, so launching from a different
       folder silently opens a DIFFERENT, empty file and registered accounts
       seem to vanish. We anchor the path to BASE_DIR.
    """
    if not url:
        return url

    # --- PostgreSQL: normalise scheme + strip asyncpg-incompatible params ---
    if url.startswith("postgres://") or url.startswith("postgresql://") or url.startswith("postgresql+psycopg2://"):
        parts = urlsplit(url)
        # Force the async driver regardless of the incoming scheme variant.
        scheme = "postgresql+asyncpg"
        query = [(k, v) for k, v in parse_qsl(parts.query) if k not in _ASYNCPG_INCOMPATIBLE_PARAMS]
        return urlunsplit((scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))

    # --- SQLite: anchor relative paths to BASE_DIR ---
    prefix = "sqlite+aiosqlite:///"
    if url.startswith(prefix):
        path_part = url[len(prefix):]
        if path_part.startswith("/"):
            return url  # already an absolute path (sqlite+aiosqlite:////abs/path)
        rel = path_part[2:] if path_part.startswith("./") else path_part
        abs_path = (BASE_DIR / rel).resolve()
        return f"{prefix}{abs_path.as_posix()}"

    return url


class Settings(BaseSettings):
    """Application settings."""
    
    # Application
    APP_NAME: str = "HomzDoctor"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database — defaults to a local SQLite file for prototyping.
    # Set DATABASE_URL in .env to a postgresql+asyncpg URL for production.
    # Relative SQLite paths are anchored to the backend dir by the validator
    # below, so the same file is used no matter where the server is launched.
    DATABASE_URL: str = "sqlite+aiosqlite:///./homzdoctor.db"

    @field_validator("DATABASE_URL")
    @classmethod
    def _normalize_db_url(cls, url: str) -> str:
        """Normalise the DB URL for the async engine (see normalize_database_url)."""
        return normalize_database_url(url)

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def is_production(self) -> bool:
        """Best-effort production detection (Railway sets RAILWAY_ENVIRONMENT)."""
        env = os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("ENVIRONMENT", "")
        return not self.DEBUG or env.lower() in {"production", "prod"}
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # CORS
    ALLOWED_ORIGINS: list = ["*"]  # Configure in production
    
    # AI/ML
    MEDGEMMA_MODEL_PATH: str = os.getenv("MEDGEMMA_MODEL_PATH", "./ml/models/medgemma")
    # Hugging Face agents (also read directly via os.getenv in the agent modules).
    HF_TOKEN: str = os.getenv("HF_TOKEN", "")
    HF_MODEL: str = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
    HF_VLM_MODEL: str = os.getenv("HF_VLM_MODEL", "google/gemma-3-27b-it")
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")

    # --- Vector DB (Qdrant) for retrieval-augmented chat ---
    # QDRANT_URL: full URL of a Qdrant instance (e.g. https://xxx.qdrant.io:6333
    # for Qdrant Cloud, or http://qdrant:6333 for the docker-compose service).
    # Leave blank to disable RAG (the assistant still works, just without
    # retrieved context).
    QDRANT_URL: str = os.getenv("QDRANT_URL", "")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION: str = os.getenv("QDRANT_COLLECTION", "homzdoctor_knowledge")
    # Embedding model served via the HF Inference API (feature-extraction).
    # 384-dim MiniLM keeps the index small; change EMBEDDING_DIM to match if you
    # swap the model.
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    EMBEDDING_DIM: int = int(os.getenv("EMBEDDING_DIM", "384"))

    class Config:
        env_file = str(BASE_DIR / ".env")  # absolute, so it loads from any CWD
        extra = "ignore"  # tolerate extra env vars (HF_*, UPLOAD_DIR, etc.) read elsewhere via os.getenv


settings = Settings()
