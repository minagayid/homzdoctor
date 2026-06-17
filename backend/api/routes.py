"""
API Routes for HomzDoctor.
Defines all RESTful endpoints for the healthcare platform.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import HTTPBearer
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.medical import *
from core.database import get_db
from core.security import hash_password, verify_password, create_access_token
from api.deps import get_current_user
from models.medical import (
    User as UserModel,
    MedicalRecord as MedicalRecordModel,
    Prescription as PrescriptionModel,
    Pharmacy as PharmacyModel,
    Appointment as AppointmentModel,
)
from core.seed import seed_user_data  # MOCK DATA — remove for production (see core/seed.py)

router = APIRouter()
security = HTTPBearer()


@router.post("/auth/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user (patient or doctor)."""
    existing = (
        await db.execute(select(UserModel).where(UserModel.email == payload.email))
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = UserModel(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        role=payload.role.value,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # MOCK DATA — seed demo records/prescription/adherence (remove for production).
    await seed_user_data(db, user.id)

    return user


@router.post("/auth/login", response_model=Token)
async def login_user(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate a user and return a JWT access token."""
    user = (
        await db.execute(select(UserModel).where(UserModel.email == credentials.email))
    ).scalar_one_or_none()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token = create_access_token(subject=str(user.id))
    return Token(access_token=token)


@router.get("/auth/me", response_model=User)
async def read_current_user(current_user: UserModel = Depends(get_current_user)):
    """Return the currently authenticated user."""
    return current_user


# Medical Records
@router.post("/medical/records", response_model=MedicalRecord, status_code=status.HTTP_201_CREATED)
async def create_medical_record(
    payload: MedicalRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Create a new medical record for the authenticated patient."""
    record = MedicalRecordModel(
        patient_id=current_user.id,
        record_type=payload.record_type,
        file_path=payload.file_path,
        findings=payload.findings,
        diagnosis=payload.diagnosis,
        status="pending",
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


@router.get("/medical/records", response_model=List[MedicalRecord])
async def list_medical_records(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """List the authenticated patient's medical records (newest first)."""
    result = await db.execute(
        select(MedicalRecordModel)
        .where(MedicalRecordModel.patient_id == current_user.id)
        .order_by(MedicalRecordModel.created_at.desc())
    )
    return result.scalars().all()


@router.get("/medical/records/{record_id}", response_model=MedicalRecord)
async def get_medical_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Retrieve a single medical record owned by the authenticated patient."""
    record = (
        await db.execute(
            select(MedicalRecordModel).where(
                MedicalRecordModel.id == record_id,
                MedicalRecordModel.patient_id == current_user.id,
            )
        )
    ).scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")
    return record


@router.post("/medical/records/{record_id}/upload")
async def upload_medical_file(record_id: int, file: UploadFile = File(...)):
    """Upload medical file (image, DICOM, PDF) for a record."""
    return {"message": "File uploaded", "filename": file.filename}


# Doctor Review
@router.post("/doctors/review/{record_id}")
async def doctor_review(record_id: int, review: DoctorReview):
    """Doctor reviews and approves/rejects/modifies AI findings."""
    return {
        "record_id": record_id,
        "action": review.action,
        "status": "reviewed"
    }


@router.get("/doctors/dashboard")
async def get_doctor_dashboard():
    """Get doctor's dashboard with pending reviews."""
    return {
        "pending_reviews": [],
        "approved_records": [],
        "rejected_records": []
    }


# Prescriptions
@router.post("/prescriptions", response_model=Prescription, status_code=status.HTTP_201_CREATED)
async def create_prescription(
    payload: PrescriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Create a new prescription (the current user acts as the prescribing doctor)."""
    prescription = PrescriptionModel(
        doctor_id=current_user.id,
        patient_id=payload.patient_id,
        record_id=payload.record_id,
        medications=payload.medications,
        approved=False,
    )
    db.add(prescription)
    await db.commit()
    await db.refresh(prescription)
    return prescription


@router.get("/prescriptions", response_model=List[Prescription])
async def list_prescriptions(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """List the authenticated patient's prescriptions (newest first)."""
    result = await db.execute(
        select(PrescriptionModel)
        .where(PrescriptionModel.patient_id == current_user.id)
        .order_by(PrescriptionModel.created_at.desc())
    )
    return result.scalars().all()


@router.get("/prescriptions/{prescription_id}", response_model=Prescription)
async def get_prescription(
    prescription_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Retrieve a prescription owned by the authenticated patient."""
    prescription = (
        await db.execute(
            select(PrescriptionModel).where(
                PrescriptionModel.id == prescription_id,
                PrescriptionModel.patient_id == current_user.id,
            )
        )
    ).scalar_one_or_none()
    if prescription is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found")
    return prescription


@router.put("/prescriptions/{prescription_id}/approve", response_model=Prescription)
async def approve_prescription(
    prescription_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Mark a prescription as approved."""
    prescription = (
        await db.execute(
            select(PrescriptionModel).where(PrescriptionModel.id == prescription_id)
        )
    ).scalar_one_or_none()
    if prescription is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescription not found")
    prescription.approved = True
    await db.commit()
    await db.refresh(prescription)
    return prescription


# Pharmacy
@router.get("/pharmacies/search", response_model=List[Pharmacy])
async def search_pharmacies(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    radius_km: int = 5,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Search pharmacies (prototype: returns all available pharmacies)."""
    result = await db.execute(select(PharmacyModel).order_by(PharmacyModel.name))
    return result.scalars().all()


@router.get("/pharmacies/{pharmacy_id}/inventory")
async def check_pharmacy_inventory(pharmacy_id: int, drug_name: Optional[str] = None):
    """Check pharmacy medication inventory."""
    return {"pharmacy_id": pharmacy_id, "inventory": []}


@router.post("/pharmacies/{pharmacy_id}/order")
async def place_order(pharmacy_id: int, order_data: dict):
    """Place a medication order at a pharmacy."""
    return {"pharmacy_id": pharmacy_id, "order_id": None, "status": "pending"}


# Medication Adherence
@router.post("/adherence/log")
async def log_medication(adherence: MedicationAdherence):
    """Log medication adherence (taken/skipped/missed)."""
    return {"message": "Adherence logged", "adherence_id": adherence.id}


@router.get("/adherence/patient/{patient_id}")
async def get_patient_adherence(patient_id: int):
    """Get patient's medication adherence history."""
    return {"patient_id": patient_id, "adherence_history": []}


@router.get("/adherence/patient/{patient_id}/score")
async def get_adherence_score(patient_id: int):
    """Get patient's adherence score."""
    return {"patient_id": patient_id, "score": 0.0}


# Appointments
@router.post("/appointments", response_model=Appointment, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    payload: AppointmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Schedule a doctor appointment for the authenticated patient."""
    appointment = AppointmentModel(
        patient_id=current_user.id,
        reason=payload.reason,
        scheduled_time=payload.scheduled_time,
        status="scheduled",
    )
    db.add(appointment)
    await db.commit()
    await db.refresh(appointment)
    return appointment


@router.get("/appointments", response_model=List[Appointment])
async def list_appointments(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """List the authenticated patient's appointments (soonest first)."""
    result = await db.execute(
        select(AppointmentModel)
        .where(AppointmentModel.patient_id == current_user.id)
        .order_by(AppointmentModel.scheduled_time.desc())
    )
    return result.scalars().all()


@router.get("/appointments/{appointment_id}", response_model=Appointment)
async def get_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Get an appointment owned by the authenticated patient."""
    appointment = (
        await db.execute(
            select(AppointmentModel).where(
                AppointmentModel.id == appointment_id,
                AppointmentModel.patient_id == current_user.id,
            )
        )
    ).scalar_one_or_none()
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    return appointment


@router.put("/appointments/{appointment_id}/cancel", response_model=Appointment)
async def cancel_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Cancel an appointment owned by the authenticated patient."""
    appointment = (
        await db.execute(
            select(AppointmentModel).where(
                AppointmentModel.id == appointment_id,
                AppointmentModel.patient_id == current_user.id,
            )
        )
    ).scalar_one_or_none()
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    appointment.status = "cancelled"
    await db.commit()
    await db.refresh(appointment)
    return appointment


# AI Diagnostics
@router.post("/ai/analyze")
async def analyze_medical_data(data: dict):
    """Run AI analysis on medical data."""
    return {"analysis_id": None, "status": "processing"}


@router.get("/ai/results/{analysis_id}")
async def get_analysis_results(analysis_id: str):
    """Get AI analysis results."""
    return {"analysis_id": analysis_id, "results": {}}


# Chat / Patient Assistant
@router.post("/chat/query")
async def chat_query(query: dict):
    """Send a query to the Patient Assistant Agent."""
    return {"response": "Patient assistant response", "sources": []}


# Escalation
@router.post("/escalation/check")
async def check_escalation(symptoms: dict):
    """Check for escalation triggers."""
    return {"escalated": False, "alerts": []}
