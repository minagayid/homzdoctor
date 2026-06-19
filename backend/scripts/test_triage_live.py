"""Verify the LVLM triage gate rejects non-medical uploads."""
from __future__ import annotations

import asyncio
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv  # noqa: E402

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

from agents.lvlm_agent import LVLMDiagnosticAgent  # noqa: E402


def terms_pdf_like_image() -> bytes:
    """An image full of terms-and-conditions text (non-medical)."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (700, 500), (255, 255, 255))
    d = ImageDraw.Draw(img)
    lines = [
        "TERMS AND CONDITIONS",
        "By opting in to our SMS messaging service you agree to receive",
        "recurring automated marketing messages. Message frequency varies.",
        "Message and data rates may apply. Reply STOP to opt out, HELP for help.",
        "We are not liable for delayed or undelivered messages. See Privacy Policy.",
        "This agreement does not constitute legal advice.",
    ]
    y = 30
    for ln in lines:
        d.text((30, y), ln, fill=(0, 0, 0))
        y += 40
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def xray_like_image() -> bytes:
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (320, 320), (12, 12, 16))
    d = ImageDraw.Draw(img)
    d.ellipse([60, 60, 260, 300], fill=(40, 40, 48))
    d.ellipse([90, 110, 150, 240], fill=(20, 20, 26))
    d.ellipse([170, 110, 230, 240], fill=(20, 20, 26))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


async def main() -> None:
    agent = LVLMDiagnosticAgent()
    print("available:", agent.available())

    print("\n--- Non-medical (terms & conditions) ---")
    r1 = await agent.process({"file_bytes": terms_pdf_like_image(), "filename": "terms.png", "modality": "xray"})
    print("rejected:", r1.get("rejected"))
    print("document_type:", r1.get("document_type"))
    print("confidence:", r1.get("confidence"))
    print("message:", r1.get("message"))

    print("\n--- Medical (synthetic chest x-ray) ---")
    r2 = await agent.process({"file_bytes": xray_like_image(), "filename": "xray.png", "modality": "xray"})
    print("rejected:", r2.get("rejected"))
    print("confidence:", r2.get("confidence"))
    print("primary_impression:", (r2.get("final_diagnosis") or {}).get("primary_impression", "")[:120])


if __name__ == "__main__":
    asyncio.run(main())
