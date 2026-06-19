"""Hugging Face Inference client for HomzDoctor backend agents.

Uses `huggingface_hub.InferenceClient` with a single token env var.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

try:
    from huggingface_hub import InferenceClient  # type: ignore
except Exception:
    InferenceClient = None

DEFAULT_MODEL = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
DEFAULT_TOKEN = os.getenv("HF_TOKEN", "")
HF_TIMEOUT = int(os.getenv("HF_TIMEOUT", "60"))


class HFInferenceError(Exception):
    pass


class HFLLMService:
    def __init__(self, token: Optional[str] = None, model: Optional[str] = None) -> None:
        self.token = token or DEFAULT_TOKEN
        self.model = model or DEFAULT_MODEL
        if InferenceClient is None:
            raise HFInferenceError("huggingface_hub is not installed")
        if not self.token:
            raise HFInferenceError("HF_TOKEN is not set")
        self._client = InferenceClient(token=self.token, timeout=HF_TIMEOUT)

    def generate(self, prompt: str, **kwargs: Any) -> str:
        try:
            result = self._client.text_generation(
                prompt=prompt,
                model=self.model,
                max_new_tokens=int(kwargs.get("max_new_tokens", 512)),
                temperature=float(kwargs.get("temperature", 0.7)),
                top_p=float(kwargs.get("top_p", 0.9)),
            )
        except Exception as exc:
            raise HFInferenceError(f"Inference failed: {exc}") from exc
        return result if isinstance(result, str) else getattr(result, "generated_text", str(result))

    def chat(self, messages: List[Dict[str, str]], **kwargs: Any) -> Any:
        try:
            return self._client.chat_completion(
                model=self.model,
                messages=messages,
                max_tokens=int(kwargs.get("max_tokens", 512)),
                temperature=float(kwargs.get("temperature", 0.7)),
                top_p=float(kwargs.get("top_p", 0.9)),
            )
        except Exception as exc:
            raise HFInferenceError(f"Chat inference failed: {exc}") from exc


_service_singleton: Optional[HFLLMService] = None


def get_hf_llm_service() -> HFLLMService:
    global _service_singleton
    if _service_singleton is None:
        _service_singleton = HFLLMService()
    return _service_singleton
