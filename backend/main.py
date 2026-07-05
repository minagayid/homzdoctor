"""
HomzDoctor - FastAPI Backend Application
Main entry point for the healthcare AI platform.
"""

import logging

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import uvicorn

from api.routes import router
from core.config import settings
from core.database import init_db

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger("homzdoctor")


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

    # Seed the RAG knowledge base into Qdrant (best-effort; no-op if the vector
    # store is not configured — the assistant still works without retrieval).
    try:
        from services.vector_store import get_vector_store
        from core.knowledge import knowledge_documents

        store = get_vector_store()
        if store.available():
            written = await store.upsert(knowledge_documents())
            LOG.info("Seeded %d knowledge snippets into Qdrant.", written)
        else:
            LOG.info("Vector store not configured (%s) — RAG disabled.", store.status().get("error"))
    except Exception as exc:  # never block startup on RAG seeding
        LOG.warning("Knowledge base seeding skipped: %s", exc)

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
    """Liveness probe (kept lightweight for Railway healthchecks).

    For a detailed readiness view (DB connectivity, AI model + vector DB
    configuration) call ``GET /api/v1/status``.
    """
    return {"status": "healthy", "service": "homzdoctor-api"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
