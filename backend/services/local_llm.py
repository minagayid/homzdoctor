"""Optional local OpenAI-compatible chat backend.

The client is disabled unless an endpoint is explicitly configured. This keeps
the default application offline and lets users run a local gpt-oss server via
Ollama, vLLM, llama.cpp, or another compatible implementation.
"""

from __future__ import annotations

import json
from typing import Any, Mapping, Sequence
from urllib.error import URLError
from urllib.request import Request, urlopen


class LocalLLMUnavailable(RuntimeError):
    """Raised when a local model is not configured or cannot answer."""


def _chat_url(endpoint: str) -> str:
    base = endpoint.strip().rstrip("/")
    if not base:
        return ""
    if base.endswith("/chat/completions"):
        return base
    if base.endswith("/v1"):
        return f"{base}/chat/completions"
    return f"{base}/v1/chat/completions"


def build_chat_completion_payload(
    *, model: str, messages: Sequence[Mapping[str, str]], max_tokens: int = 350
) -> dict[str, Any]:
    """Build a deterministic non-streaming OpenAI-compatible request body."""
    return {
        "model": model,
        "messages": [dict(message) for message in messages],
        "max_tokens": int(max_tokens),
        "temperature": 0.2,
        "stream": False,
    }


class LocalLLMClient:
    def __init__(
        self,
        *,
        endpoint: str = "",
        model: str = "gpt-oss-20b",
        api_key: str = "",
        timeout: float = 30.0,
    ) -> None:
        self.chat_completions_url = _chat_url(endpoint)
        self.model = model.strip() or "gpt-oss-20b"
        self.api_key = api_key.strip()
        self.timeout = float(timeout)

    @property
    def enabled(self) -> bool:
        return bool(self.chat_completions_url)

    def complete(
        self, messages: Sequence[Mapping[str, str]], *, max_tokens: int = 350
    ) -> str:
        if not self.enabled:
            raise LocalLLMUnavailable("Local LLM endpoint is not configured")
        body = json.dumps(
            build_chat_completion_payload(
                model=self.model, messages=messages, max_tokens=max_tokens
            )
        ).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = Request(self.chat_completions_url, data=body, headers=headers, method="POST")
        try:
            with urlopen(request, timeout=self.timeout) as response:  # nosec B310 - explicit local opt-in
                payload = json.loads(response.read().decode("utf-8"))
        except (OSError, URLError, ValueError) as exc:
            raise LocalLLMUnavailable(f"Local LLM request failed: {exc}") from exc

        try:
            content = payload["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LocalLLMUnavailable("Local LLM returned an invalid chat response") from exc
        if not isinstance(content, str) or not content.strip():
            raise LocalLLMUnavailable("Local LLM returned empty content")
        return content.strip()
