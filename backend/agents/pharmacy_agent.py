"""
LLM-backed Pharmacy agent for HomzDoctor.

Two jobs:
    1. SEARCH  - find pharmacies in the patient's nearby area, ranked by real
                 distance. Uses the Google Places API when GOOGLE_MAPS_API_KEY
                 is set, otherwise ranks the pharmacies passed in from the DB by
                 haversine distance.
    2. ORDER   - drive the prescription ordering procedure for a chosen pharmacy.
                 A regular (text) LLM drafts the patient-facing order summary and
                 confirmation message; hard guardrails enforce that only a
                 DOCTOR-APPROVED, PATIENT-CONFIRMED prescription can be ordered.

⚠️ SAFETY: ordering is gated on ``prescription.approved`` and
``patient_confirmed`` — the agent never auto-orders. It assembles the order;
fulfilment/payment is handled downstream.

Environment:
    HF_TOKEN, HF_MODEL          - text LLM (see services/hf_llm_service.py)
    GOOGLE_MAPS_API_KEY         - optional, enables live Places search
"""

from __future__ import annotations

import logging
import math
import os
from typing import Any, Dict, List, Optional

from agents.core import BaseAgent

LOG = logging.getLogger(__name__)

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

_SYSTEM_PROMPT = (
    "You are a pharmacy coordination assistant. You help patients fulfil "
    "DOCTOR-APPROVED prescriptions at a nearby pharmacy. You are concise, "
    "factual, and never give medical advice or change a prescription."
)


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two points in kilometres."""
    radius = 6371.0
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (
        math.sin(d_lat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2
    )
    return radius * 2 * math.asin(math.sqrt(a))


class LLMPharmacyAgent(BaseAgent):
    """Pharmacy search + prescription ordering, coordinated by a text LLM."""

    def __init__(self) -> None:
        super().__init__("LLMPharmacy")
        self._llm = None
        try:
            from services.hf_llm_service import get_hf_llm_service

            self._llm = get_hf_llm_service()
            LOG.info("LLMPharmacy initialised with model=%s", self._llm.model)
        except Exception as exc:
            LOG.warning("LLMPharmacy LLM backend unavailable, summaries disabled: %s", exc)
            self._llm = None

    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        action = data.get("action")
        if action == "search":
            return await self.search_pharmacies(data)
        if action == "order":
            return await self.place_order(data)
        return {"error": f"Unknown pharmacy action: {action}"}

    # --- search -------------------------------------------------------------

    async def search_pharmacies(self, data: Dict[str, Any]) -> Dict[str, Any]:
        lat = data.get("latitude")
        lon = data.get("longitude")
        radius_km = float(data.get("radius_km", 5))
        candidates: List[Dict[str, Any]] = list(data.get("pharmacies") or [])

        results: List[Dict[str, Any]] = []
        source = "database"

        if lat is not None and lon is not None and GOOGLE_MAPS_API_KEY and not candidates:
            live = await self._google_places(lat, lon, radius_km)
            if live is not None:
                results = live
                source = "google_places"

        if not results:
            # Rank DB-provided pharmacies by haversine distance.
            for ph in candidates:
                entry = dict(ph)
                if lat is not None and lon is not None and ph.get("latitude") is not None:
                    entry["distance_km"] = round(
                        _haversine_km(lat, lon, ph["latitude"], ph["longitude"]), 2
                    )
                results.append(entry)
            if lat is not None and lon is not None:
                results = [r for r in results if r.get("distance_km", 0) <= radius_km] or results
                results.sort(key=lambda r: r.get("distance_km", float("inf")))

        self.log_action("searching", {"lat": lat, "lon": lon, "radius": radius_km, "found": len(results)})

        summary = self._summarize_search(results, radius_km) if results else (
            "No pharmacies found in the requested area."
        )

        return {
            "pharmacies": results,
            "count": len(results),
            "source": source,
            "radius_km": radius_km,
            "summary": summary,
        }

    async def _google_places(
        self, lat: float, lon: float, radius_km: float
    ) -> Optional[List[Dict[str, Any]]]:
        try:
            import httpx  # type: ignore
        except Exception:
            return None
        params = {
            "location": f"{lat},{lon}",
            "radius": int(radius_km * 1000),
            "type": "pharmacy",
            "key": GOOGLE_MAPS_API_KEY,
        }
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(PLACES_URL, params=params)
                resp.raise_for_status()
                payload = resp.json()
        except Exception as exc:
            LOG.warning("Google Places lookup failed: %s", exc)
            return None

        out: List[Dict[str, Any]] = []
        for place in payload.get("results", []):
            loc = place.get("geometry", {}).get("location", {})
            p_lat, p_lon = loc.get("lat"), loc.get("lng")
            out.append(
                {
                    "name": place.get("name"),
                    "address": place.get("vicinity"),
                    "latitude": p_lat,
                    "longitude": p_lon,
                    "is_open": place.get("opening_hours", {}).get("open_now"),
                    "rating": place.get("rating"),
                    "place_id": place.get("place_id"),
                    "distance_km": round(_haversine_km(lat, lon, p_lat, p_lon), 2)
                    if p_lat is not None
                    else None,
                }
            )
        out.sort(key=lambda r: r.get("distance_km") or float("inf"))
        return out

    # --- ordering -----------------------------------------------------------

    async def place_order(self, data: Dict[str, Any]) -> Dict[str, Any]:
        prescription = data.get("prescription") or {}
        pharmacy = data.get("pharmacy") or {}
        patient_confirmed = bool(data.get("patient_confirmed"))

        # --- guardrails ---
        if not prescription.get("approved"):
            return {"order_placed": False, "error": "Prescription is not doctor-approved."}
        if not patient_confirmed:
            return {
                "order_placed": False,
                "requires_confirmation": True,
                "error": "Patient confirmation required before ordering.",
                "order_preview": self._build_order_lines(prescription),
            }
        if not pharmacy:
            return {"order_placed": False, "error": "No pharmacy selected."}

        order_lines = self._build_order_lines(prescription)
        order = {
            "order_id": data.get("order_id"),  # assigned by the persistence layer
            "pharmacy": {"id": pharmacy.get("id"), "name": pharmacy.get("name")},
            "items": order_lines,
            "status": "submitted",
        }

        self.log_action("placing_order", {"pharmacy": pharmacy.get("name"), "items": len(order_lines)})
        order["confirmation_message"] = self._confirmation_message(order, pharmacy)
        order["order_placed"] = True
        return order

    @staticmethod
    def _build_order_lines(prescription: Dict[str, Any]) -> List[Dict[str, Any]]:
        lines = []
        for med in prescription.get("medications", []):
            lines.append(
                {
                    "name": med.get("name") or med.get("drug"),
                    "dose": med.get("dose"),
                    "frequency": med.get("frequency"),
                    "duration": med.get("duration"),
                    "quantity": med.get("quantity"),
                }
            )
        return lines

    # --- LLM text helpers (degrade to templates if LLM unavailable) ---------

    def _summarize_search(self, results: List[Dict[str, Any]], radius_km: float) -> str:
        top = results[:3]
        if self._llm is None:
            names = ", ".join(
                f"{r.get('name')} ({r.get('distance_km', '?')} km)" for r in top
            )
            return f"Found {len(results)} pharmacies within {radius_km} km. Nearest: {names}."
        try:
            prompt = (
                f"A patient is looking for a pharmacy within {radius_km} km. "
                f"Here are the nearest options as JSON: {top}. Write one short, "
                "friendly sentence recommending the closest open option and noting "
                "the runner-up. Do not invent details."
            )
            return self._llm.chat(
                [{"role": "system", "content": _SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
                max_tokens=120,
            ).choices[0].message.content
        except Exception:
            names = ", ".join(f"{r.get('name')}" for r in top)
            return f"Found {len(results)} pharmacies within {radius_km} km. Nearest: {names}."

    def _confirmation_message(self, order: Dict[str, Any], pharmacy: Dict[str, Any]) -> str:
        if self._llm is None:
            items = ", ".join(i.get("name", "?") for i in order["items"])
            return (
                f"Your order for {items} has been submitted to {pharmacy.get('name')}. "
                "You will be notified when it is ready."
            )
        try:
            prompt = (
                "Write a brief, reassuring confirmation message to a patient for this "
                f"submitted pharmacy order (JSON): {order}. One short paragraph. "
                "Do not give medical advice or dosing instructions beyond what is listed."
            )
            return self._llm.chat(
                [{"role": "system", "content": _SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
                max_tokens=160,
            ).choices[0].message.content
        except Exception:
            items = ", ".join(i.get("name", "?") for i in order["items"])
            return f"Your order for {items} has been submitted to {pharmacy.get('name')}."
