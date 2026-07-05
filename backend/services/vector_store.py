"""Qdrant-backed vector store for retrieval-augmented chat (RAG).

Provides a thin, dependency-optional wrapper around a Qdrant instance plus an
embedding function served through the Hugging Face Inference API. It powers the
Patient Assistant's ability to ground answers in:

  * a small curated medical knowledge base (seeded on startup), and
  * the patient's own AI-analysed records / diagnoses.

Design goals
------------
* **Never break the app.** If ``qdrant-client`` isn't installed, ``QDRANT_URL``
  is unset, or the HF embedding call fails, the store degrades to *unavailable*
  and callers simply get no retrieved context — the assistant still answers.
* **Light dependencies.** Embeddings are computed via the HF Inference API
  (``feature_extraction``) instead of loading a local transformer, so the
  Railway image stays small.

Environment (see core/config.py):
    QDRANT_URL, QDRANT_API_KEY, QDRANT_COLLECTION,
    EMBEDDING_MODEL, EMBEDDING_DIM, HF_TOKEN
"""

from __future__ import annotations

import asyncio
import hashlib
import logging
from typing import Any, Dict, List, Optional

from core.config import settings

LOG = logging.getLogger("homzdoctor.vector_store")

try:  # qdrant-client is optional — the app runs fine without it.
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as qmodels
except Exception:  # pragma: no cover - import guard
    QdrantClient = None
    qmodels = None


def _stable_id(text: str) -> int:
    """Deterministic 63-bit point id from text (so re-seeding is idempotent)."""
    digest = hashlib.sha1(text.encode("utf-8")).hexdigest()
    return int(digest[:15], 16)


class VectorStore:
    """Small facade over Qdrant + HF embeddings with graceful degradation."""

    def __init__(self) -> None:
        self._client: Optional["QdrantClient"] = None
        self._embedder = None
        self._ready = False
        self._init_error: Optional[str] = None
        self._collection = settings.QDRANT_COLLECTION
        self._dim = settings.EMBEDDING_DIM
        self._connect()

    # --- lifecycle ----------------------------------------------------------

    def _connect(self) -> None:
        if QdrantClient is None:
            self._init_error = "qdrant-client is not installed"
            return
        if not settings.QDRANT_URL:
            self._init_error = "QDRANT_URL is not set"
            return
        try:
            self._client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY or None,
                timeout=20,
            )
        except Exception as exc:  # pragma: no cover
            self._init_error = f"Qdrant connection failed: {exc}"
            self._client = None
            return

        # The embedder shares the HF token/client used by the chat agents.
        try:
            from huggingface_hub import InferenceClient  # type: ignore

            if not settings.HF_TOKEN:
                self._init_error = "HF_TOKEN is not set (needed for embeddings)"
                return
            self._embedder = InferenceClient(token=settings.HF_TOKEN, timeout=60)
        except Exception as exc:  # pragma: no cover
            self._init_error = f"Embedding client unavailable: {exc}"
            return

        self._ready = True

    def available(self) -> bool:
        return self._ready and self._client is not None and self._embedder is not None

    def status(self) -> Dict[str, Any]:
        return {
            "available": self.available(),
            "url_configured": bool(settings.QDRANT_URL),
            "collection": self._collection,
            "embedding_model": settings.EMBEDDING_MODEL,
            "error": None if self.available() else self._init_error,
        }

    # --- embeddings ---------------------------------------------------------

    def _embed_sync(self, text: str) -> Optional[List[float]]:
        """Compute a single embedding vector (mean-pooled if token-level)."""
        try:
            result = self._embedder.feature_extraction(text, model=settings.EMBEDDING_MODEL)
        except Exception as exc:
            LOG.warning("Embedding failed: %s", exc)
            return None

        # feature_extraction may return a 1D sentence vector or a 2D token matrix.
        try:
            vec = result.tolist() if hasattr(result, "tolist") else result
        except Exception:
            vec = result
        if vec and isinstance(vec[0], (list, tuple)):  # token-level → mean pool
            cols = list(zip(*vec))
            vec = [sum(c) / len(c) for c in cols]
        return [float(x) for x in vec] if vec else None

    async def _embed(self, text: str) -> Optional[List[float]]:
        return await asyncio.to_thread(self._embed_sync, text)

    # --- collection management ---------------------------------------------

    def _ensure_collection_sync(self) -> None:
        if self._client is None:
            return
        try:
            existing = {c.name for c in self._client.get_collections().collections}
            if self._collection not in existing:
                self._client.create_collection(
                    collection_name=self._collection,
                    vectors_config=qmodels.VectorParams(
                        size=self._dim, distance=qmodels.Distance.COSINE
                    ),
                )
                LOG.info("Created Qdrant collection '%s' (dim=%d)", self._collection, self._dim)
        except Exception as exc:  # pragma: no cover
            LOG.warning("ensure_collection failed: %s", exc)

    async def ensure_collection(self) -> None:
        if not self.available():
            return
        await asyncio.to_thread(self._ensure_collection_sync)

    # --- writes -------------------------------------------------------------

    async def upsert(self, documents: List[Dict[str, Any]]) -> int:
        """Upsert documents: ``[{"text": str, "payload": {...}}, ...]``.

        Returns the number of points written. No-op (returns 0) when unavailable.
        """
        if not self.available() or not documents:
            return 0
        await self.ensure_collection()

        points = []
        for doc in documents:
            text = (doc.get("text") or "").strip()
            if not text:
                continue
            vector = await self._embed(text)
            if not vector:
                continue
            payload = dict(doc.get("payload") or {})
            payload.setdefault("text", text)
            points.append(
                qmodels.PointStruct(id=_stable_id(text), vector=vector, payload=payload)
            )

        if not points:
            return 0
        try:
            await asyncio.to_thread(
                self._client.upsert, collection_name=self._collection, points=points
            )
            return len(points)
        except Exception as exc:  # pragma: no cover
            LOG.warning("Qdrant upsert failed: %s", exc)
            return 0

    # --- reads --------------------------------------------------------------

    async def search(
        self, query: str, top_k: int = 4, source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Return the top-k payloads most similar to ``query`` (empty if down)."""
        if not self.available() or not query.strip():
            return []
        vector = await self._embed(query)
        if not vector:
            return []

        query_filter = None
        if source:
            query_filter = qmodels.Filter(
                must=[qmodels.FieldCondition(key="source", match=qmodels.MatchValue(value=source))]
            )
        try:
            hits = await asyncio.to_thread(
                self._client.search,
                collection_name=self._collection,
                query_vector=vector,
                limit=top_k,
                query_filter=query_filter,
                with_payload=True,
            )
        except Exception as exc:  # pragma: no cover
            LOG.warning("Qdrant search failed: %s", exc)
            return []

        return [{"score": float(h.score), **(h.payload or {})} for h in hits]


_store_singleton: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    global _store_singleton
    if _store_singleton is None:
        _store_singleton = VectorStore()
    return _store_singleton
