"""Probe which HF models actually respond for this token (text + vision).

Run:  python scripts/probe_models.py
Prints a WORKING list you can paste into backend/.env.
"""
from __future__ import annotations

import base64
import io
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv  # noqa: E402

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

from huggingface_hub import InferenceClient  # noqa: E402

TOKEN = os.getenv("HF_TOKEN", "")

TEXT_CANDIDATES = [
    "meta-llama/Llama-3.1-8B-Instruct",
    "meta-llama/Llama-3.3-70B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct",
    "Qwen/Qwen2.5-72B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
    "microsoft/Phi-3.5-mini-instruct",
    "google/gemma-2-2b-it",
    "HuggingFaceTB/SmolLM3-3B",
]

VISION_CANDIDATES = [
    "meta-llama/Llama-3.2-11B-Vision-Instruct",
    "Qwen/Qwen2.5-VL-7B-Instruct",
    "Qwen/Qwen2.5-VL-72B-Instruct",
    "meta-llama/Llama-4-Scout-17B-16E-Instruct",
    "google/gemma-3-27b-it",
    "google/gemma-3-4b-it",
    "zai-org/GLM-4.5V",
]


def tiny_png_url() -> str:
    from PIL import Image

    img = Image.new("RGB", (4, 4), (128, 128, 128))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def short(exc: Exception) -> str:
    s = str(exc)
    for key in ("not supported", "does not exist", "gated", "terms", "402", "quota", "loading"):
        if key in s.lower():
            return key
    return s.splitlines()[-1][:80] if s else type(exc).__name__


def main() -> int:
    if not TOKEN:
        print("HF_TOKEN missing in backend/.env")
        return 1
    client = InferenceClient(token=TOKEN, timeout=90)
    img = tiny_png_url()

    text_ok, vis_ok = [], []

    print("== TEXT models ==")
    for m in TEXT_CANDIDATES:
        try:
            client.chat_completion(
                model=m, messages=[{"role": "user", "content": "say hi"}], max_tokens=5
            )
            print(f"  WORKS   {m}")
            text_ok.append(m)
        except Exception as exc:  # noqa: BLE001
            print(f"  no      {m}  ({short(exc)})")

    print("== VISION models ==")
    for m in VISION_CANDIDATES:
        try:
            client.chat_completion(
                model=m,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "color?"},
                            {"type": "image_url", "image_url": {"url": img}},
                        ],
                    }
                ],
                max_tokens=5,
            )
            print(f"  WORKS   {m}")
            vis_ok.append(m)
        except Exception as exc:  # noqa: BLE001
            print(f"  no      {m}  ({short(exc)})")

    print("\n== SUGGESTED .env ==")
    print(f"HF_MODEL={text_ok[0] if text_ok else '<none worked>'}")
    print(f"HF_VLM_MODEL={vis_ok[0] if vis_ok else '<none worked>'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
