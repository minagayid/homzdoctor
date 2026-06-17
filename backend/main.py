"""
HomzDoctor - FastAPI Backend Application
Main entry point for the healthcare AI platform.
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn

from api.routes import router
from core.config import settings
from core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await init_db()

    # MOCK DATA — seed shared demo data (pharmacies + demo doctor). Remove for production.
    from core.database import AsyncSessionLocal
    from core.seed import seed_global

    async with AsyncSessionLocal() as db:
        await seed_global(db)

    yield
    # Shutdown
    pass


app = FastAPI(
    title="HomzDoctor API",
    description="AI Healthcare Platform - Intelligent Healthcare Copilot",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

security = HTTPBearer()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to HomzDoctor - AI Healthcare Platform",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "homzdoctor-api"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
