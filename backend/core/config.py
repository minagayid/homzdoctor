"""Environment-backed settings for a local-first HomzDoctor instance."""

from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from dotenv import load_dotenv
from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)

_ASYNCPG_INCOMPATIBLE_PARAMS = {
    "sslmode",
    "channel_binding",
    "gssencmode",
    "target_session_attrs",
}


def normalize_database_url(url: str) -> str:
    """Normalize common Postgres URLs and anchor relative SQLite paths."""
    if not url:
        return url

    if url.startswith(("postgres://", "postgresql://", "postgresql+psycopg2://")):
        parts = urlsplit(url)
        query = [
            (key, value)
            for key, value in parse_qsl(parts.query)
            if key not in _ASYNCPG_INCOMPATIBLE_PARAMS
        ]
        return urlunsplit(
            (
                "postgresql+asyncpg",
                parts.netloc,
                parts.path,
                urlencode(query),
                parts.fragment,
            )
        )

    prefix = "sqlite+aiosqlite:///"
    if url.startswith(prefix):
        path_part = url[len(prefix) :]
        # A relative path is always resolved against this checkout, so running
        # from another working directory cannot silently create a new database.
        if not path_part.startswith("/") and not (
            len(path_part) >= 3 and path_part[1:3] == ":/"
        ):
            path_part = (BASE_DIR / path_part.removeprefix("./")).resolve().as_posix()
        return f"{prefix}{path_part}"
    return url


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "HomzDoctor"
    ENVIRONMENT: str = "local"
    DEBUG: bool = False
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    SECRET_KEY: str = "homzdoctor-local-development-key-change-me"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    DATABASE_URL: str = "sqlite+aiosqlite:///./homzdoctor.db"
    REDIS_URL: str = ""
    SEED_DEMO_DATA: bool = True

    # Comma-separated text keeps .env files human-friendly on every platform.
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    HF_TOKEN: str = ""
    HF_MODEL: str = "Qwen/Qwen3-4B-Instruct"
    HF_VLM_MODEL: str = "Qwen/Qwen2.5-VL-7B-Instruct"
    GOOGLE_MAPS_API_KEY: str = ""

    # Optional local OpenAI-compatible backend (Ollama/vLLM/llama.cpp/etc.).
    LOCAL_LLM_BASE_URL: str = ""
    LOCAL_LLM_MODEL: str = "gpt-oss-20b"
    LOCAL_LLM_API_KEY: str = ""
    LOCAL_LLM_TIMEOUT: float = 30.0

    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION: str = "homzdoctor_knowledge"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIM: int = 384

    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 100 * 1024 * 1024

    @field_validator("DATABASE_URL")
    @classmethod
    def _normalize_db_url(cls, url: str) -> str:
        return normalize_database_url(url)

    @model_validator(mode="after")
    def _validate_production_security(self) -> "Settings":
        if self.is_production:
            if self.SECRET_KEY == "homzdoctor-local-development-key-change-me" or len(self.SECRET_KEY) < 32:
                raise ValueError("Production requires a unique SECRET_KEY of at least 32 characters")
            if self.is_sqlite:
                raise ValueError("Production requires a persistent PostgreSQL DATABASE_URL")
        return self

    @property
    def allowed_origins(self) -> list[str]:
        raw = self.ALLOWED_ORIGINS.strip()
        if raw.startswith("["):
            try:
                values = json.loads(raw)
                return [str(value) for value in values if str(value).strip()]
            except json.JSONDecodeError:
                return []
        return [item.strip() for item in raw.split(",") if item.strip()]

    @property
    def upload_dir(self) -> Path:
        path = Path(self.UPLOAD_DIR)
        return path if path.is_absolute() else BASE_DIR / path

    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() in {"production", "prod"}

    @property
    def local_llm_configured(self) -> bool:
        return bool(self.LOCAL_LLM_BASE_URL.strip())


settings = Settings()
