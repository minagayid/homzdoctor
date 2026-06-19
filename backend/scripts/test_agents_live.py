"""End-to-end live test of the two HomzDoctor agents (real HF calls).

Run from backend dir:  python scripts/test_agents_live.py
"""
from __future__ import annotations

import asyncio
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv  # noqa: E402

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

from agents.lvlm_agent import LVLMDiagnosticAgent  # noqa: E402
from agents.pharmacy_agent import LLMPharmacyAgent  # noqa: E402


def synthetic_xray_png() -> bytes:
    """Make a simple labelled grayscale image to exercise the vision pipeline."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (320, 320), (15, 15, 20))
    d = ImageDraw.Draw(img)
    # crude "chest" shapes
    d.ellipse([60, 60, 260, 300], fill=(40, 40, 48))
    d.ellipse([90, 110, 150, 240], fill=(20, 20, 26))
    d.ellipse([170, 110, 230, 240], fill=(20, 20, 26))
    d.text((90, 20), "CHEST X-RAY (TEST)", fill=(220, 220, 220))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


async def main() -> None:
    print("=" * 60)
    print("LVLM DIAGNOSTIC AGENT")
    print("=" * 60)
    lvlm = LVLMDiagnosticAgent()
    print("backend available:", lvlm.available())
    result = await lvlm.process(
        {"file_bytes": synthetic_xray_png(), "filename": "test_xray.png", "modality": "xray"}
    )
    print("model:", result.get("model"))
    print("confidence:", result.get("confidence"))
    print("doctor_review_required:", result.get("doctor_review_required"))
    print("final_diagnosis:")
    print(json.dumps(result.get("final_diagnosis"), indent=2)[:1200])
    if result.get("error"):
        print("ERROR:", result["error"])

    print()
    print("=" * 60)
    print("PHARMACY AGENT — search")
    print("=" * 60)
    pharm = LLMPharmacyAgent()
    sample = [
        {"id": 1, "name": "CityCare Pharmacy", "latitude": 37.7749, "longitude": -122.4194, "is_open": True},
        {"id": 2, "name": "GreenCross Drugstore", "latitude": 37.7790, "longitude": -122.4310, "is_open": True},
        {"id": 3, "name": "MediPlus 24/7", "latitude": 37.7700, "longitude": -122.4100, "is_open": False},
    ]
    search = await pharm.process(
        {"action": "search", "latitude": 37.7749, "longitude": -122.4194, "radius_km": 5, "pharmacies": sample}
    )
    print("count:", search["count"], "| source:", search["source"])
    for p in search["pharmacies"]:
        print(f"  - {p['name']}  {p.get('distance_km')} km")
    print("summary:", search["summary"])

    print()
    print("=" * 60)
    print("PHARMACY AGENT — order (guardrails)")
    print("=" * 60)
    rx = {"approved": True, "medications": [{"name": "Amoxicillin", "dose": "500mg", "frequency": "3x daily", "duration": "7 days"}]}
    # Step 1: preview (not confirmed) -> should refuse + return preview
    preview = await pharm.process({"action": "order", "pharmacy": sample[0], "prescription": rx, "patient_confirmed": False})
    print("preview (unconfirmed): placed=", preview.get("order_placed"), "| needs_confirm=", preview.get("requires_confirmation"))
    # Step 2: confirmed -> should place
    placed = await pharm.process({"action": "order", "pharmacy": sample[0], "prescription": rx, "patient_confirmed": True})
    print("confirmed: placed=", placed.get("order_placed"), "| status=", placed.get("status"))
    print("confirmation_message:", placed.get("confirmation_message"))
    # Guardrail: unapproved prescription must be refused
    bad = await pharm.process({"action": "order", "pharmacy": sample[0], "prescription": {"approved": False, "medications": []}, "patient_confirmed": True})
    print("unapproved rx refused:", bad.get("order_placed") is False, "->", bad.get("error"))


if __name__ == "__main__":
    asyncio.run(main())
