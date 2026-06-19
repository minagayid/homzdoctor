"""Hugging Face vision (LVLM) client for HomzDoctor.

Wraps ``huggingface_hub.InferenceClient.chat_completion`` with multimodal
(image + text) messages so the diagnostic agent can read X-ray / CT / MRI
images and lab-report pages.

Environment:
    HF_TOKEN        - Hugging Face access token (same token as the text LLM).
    HF_VLM_MODEL    - Vision-language model id (default below).
    HF_VLM_PROVIDER - Optional inference provider (e.g. "hf-inference",
                      "nebius", "together"). Leave empty for auto.
    HF_TIMEOUT      - Request timeout in seconds.

Model notes:
    The default is a general open VLM available on HF inference providers. For
    medical-tuned reasoning you can switch HF_VLM_MODEL to a model you have
    access to, e.g. ``google/medgemma-4b-it`` (gated — request access on the
    model page first). See docs/AGENTS_SETUP.md.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

try:
    from huggingface_hub import InferenceClient  # type: ignore
except Exception:  # pragma: no cover - import guard
    InferenceClient = None

DEFAULT_VLM_MODEL = os.getenv("HF_VLM_MODEL", "google/gemma-3-27b-it")
DEFAULT_TOKEN = os.getenv("HF_TOKEN", "")
VLM_PROVIDER = os.getenv("HF_VLM_PROVIDER", "") or None
HF_TIMEOUT = int(os.getenv("HF_TIMEOUT", "120"))


class HFVisionError(Exception):
    pass


class HFVisionService:
    """Thin multimodal chat wrapper around the HF Inference client."""

    def __init__(
        self,
        token: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> None:
        self.token = token or DEFAULT_TOKEN
        self.model = model or DEFAULT_VLM_MODEL
        self.provider = provider if provider is not None else VLM_PROVIDER
        if InferenceClient is None:
            raise HFVisionError("huggingface_hub is not installed")
        if not self.token:
            raise HFVisionError("HF_TOKEN is not set")
        kwargs: Dict[str, Any] = {"token": self.token, "timeout": HF_TIMEOUT}
        if self.provider:
            kwargs["provider"] = self.provider
        self._client = InferenceClient(**kwargs)

    @staticmethod
    def _content(text: str, image_data_urls: List[str]) -> List[Dict[str, Any]]:
        """Build a multimodal message content list (text + images)."""
        parts: List[Dict[str, Any]] = [{"type": "text", "text": text}]
        for url in image_data_urls:
            parts.append({"type": "image_url", "image_url": {"url": url}})
        return parts

    def analyze(
        self,
        prompt: str,
        image_data_urls: List[str],
        system: Optional[str] = None,
        max_tokens: int = 700,
        temperature: float = 0.2,
    ) -> str:
        """Run a single multimodal completion and return the text content."""
        messages: List[Dict[str, Any]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": self._content(prompt, image_data_urls)})

        try:
            completion = self._client.chat_completion(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
            )
        except Exception as exc:
            raise HFVisionError(f"Vision inference failed: {exc}") from exc

        try:
            return completion.choices[0].message.content
        except Exception:
            return str(completion)


_service_singleton: Optional[HFVisionService] = None


def get_hf_vision_service() -> HFVisionService:
    global _service_singleton
    if _service_singleton is None:
        _service_singleton = HFVisionService()
    return _service_singleton
