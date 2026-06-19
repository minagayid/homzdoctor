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


def _normalize_database_url(url: str) -> str:
    """Anchor relative SQLite paths to BASE_DIR.

    A URL like ``sqlite+aiosqlite:///./homzdoctor.db`` is resolved relative to
    the *current working directory*, so launching the server from a different
    folder (VS Code debugger, repo root, etc.) silently opens a DIFFERENT,
    empty database — making registered accounts seem to vanish. Rewriting the
    path to an absolute one keeps everyone pointed at one file.
    """
    prefix = "sqlite+aiosqlite:///"
    if not url.startswith(prefix):
        return url  # non-SQLite (e.g. Postgres) — leave untouched
    path_part = url[len(prefix):]
    if path_part.startswith("/"):
        return url  # already an absolute path (sqlite+aiosqlite:////abs/path)
    # Strip a leading "./" then anchor to BASE_DIR.
    rel = path_part[2:] if path_part.startswith("./") else path_part
    abs_path = (BASE_DIR / rel).resolve()
    return f"{prefix}{abs_path.as_posix()}"


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
    def _anchor_sqlite_path(cls, url: str) -> str:
        """Rewrite a relative SQLite path to an absolute one under BASE_DIR.

        ``sqlite+aiosqlite:///./homzdoctor.db`` resolves against the current
        working directory, so launching the server from a different folder
        opens a DIFFERENT, empty database and registered accounts seem to
        vanish. Anchoring to BASE_DIR keeps everyone on one file. Non-SQLite
        URLs (e.g. Postgres) are returned unchanged.
        """
        prefix = "sqlite+aiosqlite:///"
        if not url.startswith(prefix):
            return url
        path_part = url[len(prefix):]
        if path_part.startswith("/"):
            return url  # already absolute (sqlite+aiosqlite:////abs/path)
        rel = path_part[2:] if path_part.startswith("./") else path_part
        return f"{prefix}{(BASE_DIR / rel).resolve().as_posix()}"
    
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
    
    class Config:
        env_file = str(BASE_DIR / ".env")  # absolute, so it loads from any CWD
        extra = "ignore"  # tolerate extra env vars (HF_*, UPLOAD_DIR, etc.) read elsewhere via os.getenv


settings = Settings()
