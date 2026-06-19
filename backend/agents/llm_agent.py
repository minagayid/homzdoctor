"""
Real LLM-backed agent for HomzDoctor Patient Assistant.

Requires:
    pip install huggingface_hub

Environment:
    HF_TOKEN   - Hugging Face API token
    HF_MODEL   - Default model (default: Qwen/Qwen3-4B-Instruct)
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional
import logging

from agents.core import BaseAgent

LOG = logging.getLogger(__name__)

DEFAULT_MODEL = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
DEFAULT_TOKEN = os.getenv("HF_TOKEN", "")
HF_TIMEOUT = int(os.getenv("HF_TIMEOUT", "60"))

_SYSTEM_PROMPT = (
    "You are a friendly, clear medical assistant for patients.\n"
    "Explain diagnoses, tests, and care plans in plain language.\n"
    "Do not give emergency advice. When uncertain, say so and recommend consulting a clinician."
)


class HFLLMNotAvailable(Exception):
    pass


class _HFClient:
    def __init__(self, model: str, token: str, timeout: int) -> None:
        try:
            from huggingface_hub import InferenceClient  # type: ignore
        except Exception as exc:
            raise HFLLMNotAvailable("huggingface_hub is not installed") from exc

        self._client = InferenceClient(token=token, timeout=timeout)
        self.model = model

    def chat(self, messages: List[Dict[str, str]], max_tokens: int = 512) -> str:
        try:
            completion = self._client.chat_completion(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.9,
            )
        except Exception as exc:
            raise HFLLMNotAvailable(f"HuggingFace inference failed: {exc}") from exc

        try:
            return completion.choices[0].message.content
        except Exception:
            return str(completion)


class _Client:
    def __init__(self, model: str, token: str, timeout: int) -> None:
        try:
            self._impl = _HFClient(model, token, timeout)
        except HFLLMNotAvailable:
            self._impl = None

    def available(self) -> bool:
        return self._impl is not None

    def chat(self, messages: List[Dict[str, str]], max_tokens: int = 512) -> str:
        if self._impl is None:
            raise HFLLMNotAvailable("LLM client is not available")
        return self._impl.chat(messages, max_tokens=max_tokens)


_client = _Client(model=DEFAULT_MODEL, token=DEFAULT_TOKEN, timeout=HF_TIMEOUT)


class LLMPatientAssistantAgent(BaseAgent):
    def __init__(self) -> None:
        super().__init__("PatientAssistant")
        LOG.info("PatientAssistant initialized with model=%s available=%s", DEFAULT_MODEL, _client.available())

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        query = (data.get("query") or "").strip()
        if not query:
            return {"response": "Please provide a question.", "sources": [], "confidence": 0.0}

        context = data.get("context") or {}
        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": query},
        ]

        if context:
            messages.insert(
                1,
                {
                    "role": "system",
                    "content": f"Relevant context: {context}",
                },
            )

        response_text = self._fallback(query)
        model_used = "fallback"
        if _client.available():
            try:
                response_text = _client.chat(messages, max_tokens=350)
                model_used = DEFAULT_MODEL
            except Exception as exc:
                LOG.warning("LLM inference failed, using fallback response: %s", exc)
                response_text = self._fallback(query)

        return {
            "response": response_text,
            "sources": [],
            "confidence": 0.0,
            "model": model_used,
        }

    def _fallback(self, query: str) -> str:
        lower = query.lower()
        if any(word in lower for word in ["pain", "hurt", "ache"]):
            return "If this is severe or new, seek urgent medical care. Otherwise, note what makes it better or worse and share this with your clinician."
        if "medication" in lower:
            return "Take medications exactly as prescribed. If you miss a dose, follow your pharmacist or clinician's instructions."
        if "report" in lower or "result" in lower or "diagnosis" in lower:
            return "Reports show findings your clinician can interpret. For exact meaning, ask them to walk through it with you."
        return "This is a general health inquiry. A clinician can give you advice matched to your exact history and current symptoms."

    async def explain_report(self, report: Dict[str, Any]) -> str:
        summary = report.get("report", {})
        if isinstance(summary, dict):
            summary = summary.get("patient") or summary.get("physician") or str(summary)
        prompt = f"Explain this medical report in plain language for a patient: {summary}"
        messages = [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]
        fallback = "I can give a simplified overview, but only your clinician can explain your exact results."
        if _client.available():
            try:
                return _client.chat(messages, max_tokens=300)
            except Exception:
                pass
        return fallback
