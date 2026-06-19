"""Live test of the doctor role flow against the ASGI app."""
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


async def reg_login(c, email, role):
    await c.post("/auth/register", json={"email": email, "password": "secret123", "fullName": f"{role} test", "role": role})
    tok = (await c.post("/auth/login", json={"email": email, "password": "secret123"})).json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


async def main() -> None:
    transport = ASGITransport(app=app)
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=transport, base_url="http://test/api/v1") as c:
            patient_h = await reg_login(c, "pat.role@homz.app", "patient")
            doctor_h = await reg_login(c, "doc.role@homz.app", "doctor")

            # Patient is blocked from doctor endpoints (403).
            r = await c.get("/doctors/dashboard", headers=patient_h)
            print("patient -> /doctors/dashboard:", r.status_code, "(expect 403)")

            # Doctor sees stats.
            r = await c.get("/doctors/dashboard", headers=doctor_h)
            print("doctor -> dashboard:", r.status_code, r.json())

            # Doctor sees a pending queue (patient registration seeds a pending MRI record).
            r = await c.get("/doctors/records/pending", headers=doctor_h)
            queue = r.json()
            print("doctor -> pending count:", len(queue))
            if queue:
                rec = next((x for x in queue if x["status"] == "pending"), queue[0])
                print("  first pending:", rec["patientName"], "|", rec["recordType"], "|", rec["status"])
                # Approve it with an edited diagnosis.
                r = await c.post(f"/doctors/review/{rec['id']}", headers=doctor_h,
                                 json={"action": "approve", "notes": "Looks normal.", "diagnosis": "No acute findings"})
                print("  review approve:", r.status_code, "-> status:", r.json()["status"], "reviewed:", r.json()["doctorReviewed"])

            # After approval, pending count should drop by one.
            r = await c.get("/doctors/records/pending", headers=doctor_h)
            print("doctor -> pending count after approve:", len(r.json()))


if __name__ == "__main__":
    asyncio.run(main())
