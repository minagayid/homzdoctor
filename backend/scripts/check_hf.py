"""Quick connectivity check for the HomzDoctor Hugging Face agents.

Run from the backend dir:  python scripts/check_hf.py
Verifies the token, the text model, and the vision (LVLM) model with REAL calls.
"""
from __future__ import annotations

import base64
import io
import os
import sys
from pathlib import Path

# Load backend/.env so HF_TOKEN etc. are available.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv  # noqa: E402

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

from huggingface_hub import InferenceClient  # noqa: E402

TOKEN = os.getenv("HF_TOKEN", "")
TEXT_MODEL = os.getenv("HF_MODEL", "Qwen/Qwen3-4B-Instruct")
VLM_MODEL = os.getenv("HF_VLM_MODEL", "Qwen/Qwen2.5-VL-7B-Instruct")
PROVIDER = os.getenv("HF_VLM_PROVIDER", "") or None


def ok(msg: str) -> None:
    print(f"  [OK]   {msg}")


def fail(msg: str) -> None:
    print(f"  [FAIL] {msg}")


def tiny_png_data_url() -> str:
    """A 2x2 grey PNG as a data URL (no external file needed)."""
    try:
        from PIL import Image
    except Exception:
        # 1x1 transparent PNG, hard-coded.
        raw = base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
        )
        return "data:image/png;base64," + base64.b64encode(raw).decode()
    img = Image.new("RGB", (2, 2), (128, 128, 128))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def main() -> int:
    print("HomzDoctor — Hugging Face check")
    print(f"  token present: {bool(TOKEN)}")
    print(f"  text model:    {TEXT_MODEL}")
    print(f"  vision model:  {VLM_MODEL}  (provider={PROVIDER or 'auto'})")
    print("-" * 50)

    if not TOKEN:
        fail("HF_TOKEN is empty — add it to backend/.env")
        return 1

    client = InferenceClient(token=TOKEN, timeout=120)

    # 1) Text model
    try:
        r = client.chat_completion(
            model=TEXT_MODEL,
            messages=[{"role": "user", "content": "Reply with the single word: ready"}],
            max_tokens=10,
        )
        ok(f"text model responded: {r.choices[0].message.content.strip()!r}")
    except Exception as exc:
        fail(f"text model failed: {exc}")

    # 2) Vision model
    vkwargs = {"token": TOKEN, "timeout": 120}
    if PROVIDER:
        vkwargs["provider"] = PROVIDER
    vclient = InferenceClient(**vkwargs)
    try:
        r = vclient.chat_completion(
            model=VLM_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What colour is this image? One word."},
                        {"type": "image_url", "image_url": {"url": tiny_png_data_url()}},
                    ],
                }
            ],
            max_tokens=10,
        )
        ok(f"vision model responded: {r.choices[0].message.content.strip()!r}")
    except Exception as exc:
        fail(f"vision model failed: {exc}")
        print("         -> If it says 'not supported'/'no provider', the model")
        print("            isn't served serverlessly. Keep Qwen/Qwen2.5-VL-7B-Instruct.")

    print("-" * 50)
    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
