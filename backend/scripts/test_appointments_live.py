"""Live test of appointment create/update/cancel/delete against the ASGI app."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dotenv import load_dotenv  # noqa: E402

load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=True)

import httpx  # noqa: E402
from httpx import ASGITransport  # noqa: E402
from main import app  # noqa: E402

EMAIL = "appt.test@homzdoctor.app"
PWD = "secret123"


async def main() -> None:
    transport = ASGITransport(app=app)
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=transport, base_url="http://test/api/v1") as c:
            await c.post("/auth/register", json={"email": EMAIL, "password": PWD, "fullName": "Appt Test", "role": "patient"})
            tok = (await c.post("/auth/login", json={"email": EMAIL, "password": PWD})).json()["access_token"]
            h = {"Authorization": f"Bearer {tok}"}

            r = await c.post("/appointments", headers=h, json={"reason": "Initial visit", "scheduledTime": "2026-07-01T10:00:00"})
            appt = r.json()
            aid = appt["id"]
            print("create:", r.status_code, "| reason:", appt["reason"])

            r = await c.put(f"/appointments/{aid}", headers=h, json={"reason": "Rescheduled visit", "scheduledTime": "2026-07-02T14:30:00"})
            print("update:", r.status_code, "| reason:", r.json()["reason"], "| time:", r.json()["scheduledTime"])

            r = await c.put(f"/appointments/{aid}/cancel", headers=h)
            print("cancel:", r.status_code, "| status:", r.json()["status"])

            r = await c.delete(f"/appointments/{aid}", headers=h)
            print("delete:", r.status_code, "(expect 204)")

            r = await c.get(f"/appointments/{aid}", headers=h)
            print("get after delete:", r.status_code, "(expect 404)")


if __name__ == "__main__":
    asyncio.run(main())
