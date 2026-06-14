"""
Configuration management for HomzDoctor backend.
"""

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# override=True so this project's .env wins over any global env vars (e.g. a
# system-wide DATABASE_URL left over from another project).
load_dotenv(override=True)


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
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://homzdoctor:homzdoctor@localhost:5432/homzdoctor"
    )
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # CORS
    ALLOWED_ORIGINS: list = ["*"]  # Configure in production
    
    # AI/ML
    MEDGEMMA_MODEL_PATH: str = os.getenv("MEDGEMMA_MODEL_PATH", "./ml/models/medgemma")
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # tolerate extra env vars (HF_*, UPLOAD_DIR, etc.) read elsewhere via os.getenv


settings = Settings()
