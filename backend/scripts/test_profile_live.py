"""Live test of the profile + password endpoints against the ASGI app.

Run from backend dir:  python scripts/test_profile_live.py
"""
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

EMAIL = "dr.profiletest@homzdoctor.app"
PWD = "secret123"


async def main() -> None:
    transport = ASGITransport(app=app)
    async with app.router.lifespan_context(app):  # run startup (init_db, seed)
        async with httpx.AsyncClient(transport=transport, base_url="http://test/api/v1") as c:
            # Register a DOCTOR (ignore 400 if already exists from a prior run)
            r = await c.post("/auth/register", json={
                "email": EMAIL, "password": PWD, "fullName": "Dr. Profile Test", "role": "doctor",
            })
            print("register:", r.status_code)

            r = await c.post("/auth/login", json={"email": EMAIL, "password": PWD})
            token = r.json()["access_token"]
            h = {"Authorization": f"Bearer {token}"}
            print("login:", r.status_code)

            r = await c.get("/users/me/profile", headers=h)
            print("GET profile:", r.status_code, "role=", r.json().get("role"))

            r = await c.put("/users/me/profile", headers=h, json={
                "fullName": "Dr. Sarah Test",
                "specialty": "Radiology",
                "licenseNumber": "PMC-99887",
                "hospital": "City General",
                "yearsExperience": 9,
                "phone": "+1 555 0190",
                "notifyWhatsapp": True,
                "language": "ur",
            })
            j = r.json()
            print("PUT profile:", r.status_code)
            print("  fullName     =", j.get("fullName"))
            print("  specialty    =", j.get("specialty"))
            print("  yearsExp     =", j.get("yearsExperience"))
            print("  notifyWhats  =", j.get("notifyWhatsapp"))
            print("  language     =", j.get("language"))

            # change password (wrong current -> 400)
            r = await c.put("/users/me/password", headers=h, json={
                "currentPassword": "WRONG", "newPassword": "newsecret123"})
            print("password (wrong current):", r.status_code, "(expect 400)")

            r = await c.put("/users/me/password", headers=h, json={
                "currentPassword": PWD, "newPassword": "newsecret123"})
            print("password (correct):", r.status_code, r.json())

            # login with new password
            r = await c.post("/auth/login", json={"email": EMAIL, "password": "newsecret123"})
            print("re-login with new password:", r.status_code)


if __name__ == "__main__":
    asyncio.run(main())
