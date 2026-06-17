"""
MOCK / DEMO DATA SEEDING  ⚠️

This module exists ONLY to populate the prototype with sample data so the app is
explorable. To switch to real data:

  1. Delete this file.
  2. Remove the `seed_global(...)` call in `main.py` (lifespan).
  3. Remove the `seed_user_data(...)` call in `api/routes.py` (register_user).

Everything mock lives here so it's easy to rip out in one place.
"""

from datetime import datetime, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.medical import (
    User,
    MedicalRecord,
    Prescription,
    MedicationAdherence,
    Pharmacy,
    Appointment,
)
from core.security import hash_password

DEMO_DOCTOR_EMAIL = "dr.demo@homzdoctor.app"

# --- Reference / global mock data (shared by all users) ---------------------

SAMPLE_PHARMACIES = [
    {
        "name": "CityCare Pharmacy",
        "address": "123 Main St, Springfield",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "phone": "+1-555-0101",
        "is_open": True,
    },
    {
        "name": "GreenCross Drugstore",
        "address": "45 Oak Ave, Springfield",
        "latitude": 37.7790,
        "longitude": -122.4310,
        "phone": "+1-555-0102",
        "is_open": True,
    },
    {
        "name": "MediPlus 24/7",
        "address": "9 Elm Blvd, Springfield",
        "latitude": 37.7700,
        "longitude": -122.4100,
        "phone": "+1-555-0103",
        "is_open": False,
    },
]


async def seed_global(db: AsyncSession) -> None:
    """Seed shared reference data (pharmacies + a demo reviewing doctor). Idempotent."""
    pharmacy_count = (await db.execute(select(func.count()).select_from(Pharmacy))).scalar_one()
    if pharmacy_count == 0:
        db.add_all([Pharmacy(**p) for p in SAMPLE_PHARMACIES])

    doctor = (
        await db.execute(select(User).where(User.email == DEMO_DOCTOR_EMAIL))
    ).scalar_one_or_none()
    if doctor is None:
        db.add(
            User(
                email=DEMO_DOCTOR_EMAIL,
                hashed_password=hash_password("demodoctor"),
                full_name="Dr. Sarah Chen",
                role="doctor",
                is_active=True,
            )
        )

    await db.commit()


# --- Per-user mock data (seeded on registration) ----------------------------


def _sample_records(user_id: int) -> list[MedicalRecord]:
    return [
        MedicalRecord(
            patient_id=user_id,
            record_type="xray",
            file_path="chest_xray_0481.dcm",
            findings="No acute cardiopulmonary abnormality detected.",
            diagnosis="Normal chest X-ray",
            confidence_score=0.92,
            doctor_reviewed=True,
            doctor_notes="Concur with AI findings. Routine follow-up in 12 months.",
            status="reviewed",
        ),
        MedicalRecord(
            patient_id=user_id,
            record_type="lab_report",
            file_path="cbc_panel.pdf",
            findings="Complete blood count within normal limits.",
            confidence_score=0.88,
            doctor_reviewed=True,
            status="reviewed",
        ),
        MedicalRecord(
            patient_id=user_id,
            record_type="mri",
            file_path="brain_mri_t1.dcm",
            findings="Awaiting AI analysis.",
            status="pending",
        ),
    ]


async def seed_user_data(db: AsyncSession, user_id: int) -> None:
    """Seed sample per-patient data: records → a prescription → adherence rows."""
    # 1. Medical records (flush to assign ids before referencing them).
    records = _sample_records(user_id)
    db.add_all(records)
    await db.flush()

    # 2. A prescription tied to the first (reviewed) record + the demo doctor.
    doctor = (
        await db.execute(select(User).where(User.email == DEMO_DOCTOR_EMAIL))
    ).scalar_one_or_none()
    doctor_id = doctor.id if doctor else user_id

    prescription = Prescription(
        doctor_id=doctor_id,
        patient_id=user_id,
        record_id=records[0].id,
        medications=[
            {"name": "Amoxicillin", "dose": "500mg", "frequency": "3x daily", "duration": "7 days"},
            {"name": "Ibuprofen", "dose": "200mg", "frequency": "as needed", "duration": "5 days"},
        ],
        approved=True,
    )
    db.add(prescription)
    await db.flush()

    # 3. Medication adherence entries for that prescription.
    now = datetime.utcnow()
    db.add_all(
        [
            MedicationAdherence(
                prescription_id=prescription.id,
                medication_name="Amoxicillin",
                scheduled_time=now + timedelta(hours=2),
                status="pending",
            ),
            MedicationAdherence(
                prescription_id=prescription.id,
                medication_name="Ibuprofen",
                scheduled_time=now - timedelta(hours=4),
                status="taken",
                taken_at=now - timedelta(hours=4),
            ),
        ]
    )

    # 4. A couple of sample appointments.
    doctor_id = doctor.id if doctor else None
    db.add_all(
        [
            Appointment(
                patient_id=user_id,
                doctor_id=doctor_id,
                reason="Follow-up on chest X-ray results",
                scheduled_time=now + timedelta(days=3, hours=2),
                status="scheduled",
            ),
            Appointment(
                patient_id=user_id,
                doctor_id=doctor_id,
                reason="Annual physical check-up",
                scheduled_time=now - timedelta(days=20),
                status="completed",
            ),
        ]
    )

    await db.commit()
