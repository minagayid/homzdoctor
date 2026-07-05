"""
API Routes for HomzDoctor.
Defines all RESTful endpoints for the healthcare platform.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import HTTPBearer
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.medical import *
from core.database import get_db
from core.security import hash_password, verify_password, create_access_token
from api.deps import get_current_user, require_doctor
from models.medical import (
    User as UserModel,
    UserProfile as UserProfileModel,
    MedicalRecord as MedicalRecordModel,
    DoctorReview as DoctorReviewModel,
    Prescription as PrescriptionModel,
    Pharmacy as PharmacyModel,
    Appointment as AppointmentModel,
)
from services.medical import LVLMDiagnosticService, PharmacyService, PatientAssistantService
from core.seed import seed_user_data  # MOCK DATA — remove for production (see core/seed.py)

router = APIRouter()
security = HTTPBearer()

# Agent-backed services (singletons; load their model clients lazily).
lvlm_service = LVLMDiagnosticService()
pharmacy_service = PharmacyService()
patient_assistant_service = PatientAssistantService()


async def _index_record(record: MedicalRecordModel) -> None:
    """Best-effort: embed a record's findings/diagnosis for retrieval in chat.

    No-op when the vector store isn't configured. Never raises to the caller.
    """
    text_parts = [p for p in (record.findings, record.diagnosis, record.doctor_notes) if p]
    if not text_parts:
        return
    try:
        from services.vector_store import get_vector_store

        store = get_vector_store()
        if not store.available():
            return
        await store.upsert(
            [
                {
                    "text": " ".join(text_parts),
                    "payload": {
                        "source": "record",
                        "title": f"{record.record_type} record #{record.id}",
                        "patient_id": record.patient_id,
                        "status": record.status,
                    },
                }
            ]
        )
    except Exception:
        pass


@router.get("/status")
async def system_status():
    """Report which subsystems are actually live (DB, AI models, vector DB).

    Makes silent fallbacks visible: if the AI or database isn't configured on
    the deployment, this endpoint says so instead of the app pretending to work.
    """
    from core.config import settings
    from core.database import check_db
    from services.vector_store import get_vector_store

    db = await check_db()
    ai_configured = bool(settings.HF_TOKEN)
    return {
        "service": "homzdoctor-api",
        "version": "0.1.0",
        "database": db,
        "ai": {
            "configured": ai_configured,
            "llm": {"available": lvlm_service is not None and ai_configured, "model": settings.HF_MODEL},
            "vlm": {"available": lvlm_service.available, "model": settings.HF_VLM_MODEL},
            "note": None if ai_configured else "HF_TOKEN not set — AI agents return fallback responses.",
        },
        "vector_db": get_vector_store().status(),
    }


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


# --- Profile & account settings ---------------------------------------------

# Fields that live on the user_profiles row (everything except full_name).
_PROFILE_FIELDS = (
    "phone", "avatar_url", "bio", "gender", "date_of_birth", "address", "city",
    "country", "specialty", "license_number", "hospital", "years_experience",
    "qualifications", "consultation_fee", "language", "timezone", "theme",
    "notify_email", "notify_sms", "notify_push", "notify_whatsapp",
)


async def _get_or_create_profile(db: AsyncSession, user_id: int) -> UserProfileModel:
    """Fetch the user's profile row, creating a blank one on first access."""
    profile = (
        await db.execute(select(UserProfileModel).where(UserProfileModel.user_id == user_id))
    ).scalar_one_or_none()
    if profile is None:
        profile = UserProfileModel(user_id=user_id)
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
    return profile


def _build_profile(user: UserModel, profile: UserProfileModel) -> Profile:
    """Merge the user identity + profile row into a single response model."""
    data = {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at,
    }
    for field in _PROFILE_FIELDS:
        data[field] = getattr(profile, field)
    return Profile(**data)


@router.get("/users/me/profile", response_model=Profile)
async def get_my_profile(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Get the authenticated user's full profile (identity + extended fields)."""
    profile = await _get_or_create_profile(db, current_user.id)
    return _build_profile(current_user, profile)


@router.put("/users/me/profile", response_model=Profile)
async def update_my_profile(
    payload: ProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Update the authenticated user's profile (partial update)."""
    profile = await _get_or_create_profile(db, current_user.id)
    updates = payload.model_dump(exclude_unset=True)

    # full_name lives on the user row.
    if "full_name" in updates:
        new_name = (updates.pop("full_name") or "").strip()
        if new_name:
            current_user.full_name = new_name

    for field, value in updates.items():
        if field in _PROFILE_FIELDS:
            setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)
    await db.refresh(current_user)
    return _build_profile(current_user, profile)


@router.put("/users/me/password")
async def change_my_password(
    payload: PasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Change the authenticated user's password (requires the current one)."""
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    if len(payload.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters",
        )
    current_user.hashed_password = hash_password(payload.new_password)
    await db.commit()
    return {"message": "Password updated"}


# Avatar upload limits.
_AVATAR_MAX_BYTES = 8 * 1024 * 1024  # 8 MB raw upload
_AVATAR_SIZE = 256  # output square px
_AVATAR_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".gif"}


def _encode_avatar(raw: bytes) -> str:
    """Compress an uploaded image to a small square JPEG base64 data URL.

    Returns a ``data:image/jpeg;base64,...`` string stored directly in SQLite.
    """
    import base64
    import io

    try:
        from PIL import Image
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Image processing library (Pillow) is not installed.",
        ) from exc

    try:
        img = Image.open(io.BytesIO(raw))
        img = img.convert("RGB")
        # Center-crop to a square, then resize.
        w, h = img.size
        side = min(w, h)
        left, top = (w - side) // 2, (h - side) // 2
        img = img.crop((left, top, left + side, top + side))
        img = img.resize((_AVATAR_SIZE, _AVATAR_SIZE))
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is not a valid image.",
        ) from exc

    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{encoded}"


@router.post("/users/me/avatar", response_model=Profile)
async def upload_my_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Upload a profile picture. The compressed image is stored in the database."""
    import os

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext and ext not in _AVATAR_EXTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image type '{ext}'.",
        )

    raw = await file.read()
    if len(raw) > _AVATAR_MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Image is too large (max 8 MB).",
        )

    profile = await _get_or_create_profile(db, current_user.id)
    profile.avatar_url = _encode_avatar(raw)
    await db.commit()
    await db.refresh(profile)
    return _build_profile(current_user, profile)


@router.delete("/users/me/avatar", response_model=Profile)
async def delete_my_avatar(
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Remove the profile picture."""
    profile = await _get_or_create_profile(db, current_user.id)
    profile.avatar_url = None
    await db.commit()
    await db.refresh(profile)
    return _build_profile(current_user, profile)


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
    await _index_record(record)  # embed findings for retrieval-augmented chat
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


@router.put("/medical/records/{record_id}", response_model=MedicalRecord)
async def update_medical_record(
    record_id: int,
    payload: MedicalRecordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Update fields of a medical record owned by the authenticated patient."""
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

    # Apply only the fields the client actually sent (partial update).
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(record, field, value)

    await db.commit()
    await db.refresh(record)
    return record


@router.delete("/medical/records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_medical_record(
    record_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Delete a medical record owned by the authenticated patient."""
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

    await db.delete(record)
    await db.commit()


@router.post("/medical/records/{record_id}/upload")
async def upload_medical_file(record_id: int, file: UploadFile = File(...)):
    """Upload medical file (image, DICOM, PDF) for a record."""
    return {"message": "File uploaded", "filename": file.filename}


# Doctor — review workflow (doctor/admin only)
def _record_with_patient(record: MedicalRecordModel, patient: Optional[UserModel]) -> dict:
    """Serialize a record plus its patient's name/email for the doctor view."""
    return {
        "id": record.id,
        "patientId": record.patient_id,
        "patientName": patient.full_name if patient else None,
        "patientEmail": patient.email if patient else None,
        "recordType": record.record_type,
        "filePath": record.file_path,
        "findings": record.findings,
        "diagnosis": record.diagnosis,
        "confidenceScore": record.confidence_score,
        "doctorReviewed": record.doctor_reviewed,
        "doctorNotes": record.doctor_notes,
        "status": record.status,
        "createdAt": record.created_at,
    }


@router.get("/doctors/dashboard")
async def get_doctor_dashboard(
    db: AsyncSession = Depends(get_db),
    doctor: UserModel = Depends(require_doctor),
):
    """Doctor dashboard stats: pending reviews, reviewed, patients, prescriptions."""
    records = (await db.execute(select(MedicalRecordModel))).scalars().all()
    pending = [r for r in records if not r.doctor_reviewed and r.status == "pending"]
    reviewed = [r for r in records if r.doctor_reviewed]
    patient_ids = {r.patient_id for r in records}
    rx = (await db.execute(select(PrescriptionModel))).scalars().all()
    pending_rx = [p for p in rx if not p.approved]
    return {
        "pendingReviews": len(pending),
        "reviewedRecords": len(reviewed),
        "totalRecords": len(records),
        "patients": len(patient_ids),
        "pendingPrescriptions": len(pending_rx),
    }


@router.get("/doctors/records/pending")
async def list_pending_reviews(
    db: AsyncSession = Depends(get_db),
    doctor: UserModel = Depends(require_doctor),
):
    """List medical records (across all patients) awaiting doctor review."""
    records = (
        await db.execute(
            select(MedicalRecordModel)
            .where(MedicalRecordModel.doctor_reviewed == False)  # noqa: E712
            .order_by(MedicalRecordModel.created_at.desc())
        )
    ).scalars().all()
    patients = {
        u.id: u for u in (await db.execute(select(UserModel))).scalars().all()
    }
    return [_record_with_patient(r, patients.get(r.patient_id)) for r in records]


@router.post("/doctors/review/{record_id}")
async def doctor_review(
    record_id: int,
    review: DoctorReviewAction,
    db: AsyncSession = Depends(get_db),
    doctor: UserModel = Depends(require_doctor),
):
    """Doctor approves / modifies / rejects AI findings on any patient's record."""
    record = (
        await db.execute(select(MedicalRecordModel).where(MedicalRecordModel.id == record_id))
    ).scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    action = (review.action or "").lower()
    if action not in ("approve", "modify", "reject"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid action")

    # Apply optional clinician edits.
    if review.diagnosis is not None:
        record.diagnosis = review.diagnosis
    if review.findings is not None:
        record.findings = review.findings
    if review.notes is not None:
        record.doctor_notes = review.notes

    record.doctor_reviewed = True
    record.status = {"approve": "approved", "modify": "reviewed", "reject": "rejected"}[action]

    # Audit trail row.
    db.add(
        DoctorReviewModel(
            record_id=record.id,
            doctor_id=doctor.id,
            action=action,
            notes=review.notes,
            prescription=review.prescription or {},
        )
    )
    await db.commit()
    await db.refresh(record)
    await _index_record(record)  # re-embed with the clinician's approved findings

    patient = (
        await db.execute(select(UserModel).where(UserModel.id == record.patient_id))
    ).scalar_one_or_none()
    return _record_with_patient(record, patient)


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
@router.get("/pharmacies/search")
async def search_pharmacies(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    radius_km: int = 5,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Search nearby pharmacies, ranked by distance from (lat, lon).

    Pulls pharmacy candidates from the DB and lets the LLM pharmacy agent rank
    them by real distance (or query Google Places live if GOOGLE_MAPS_API_KEY
    is configured). If no coordinates are supplied, returns the full list.
    """
    result = await db.execute(select(PharmacyModel).order_by(PharmacyModel.name))
    pharmacies = [
        {
            "id": p.id,
            "name": p.name,
            "address": p.address,
            "latitude": p.latitude,
            "longitude": p.longitude,
            "phone": p.phone,
            "is_open": p.is_open,
        }
        for p in result.scalars().all()
    ]
    return await pharmacy_service.find_nearby_pharmacies(
        lat=lat, lon=lon, radius_km=radius_km, pharmacies=pharmacies
    )


@router.get("/pharmacies/{pharmacy_id}/inventory")
async def check_pharmacy_inventory(pharmacy_id: int, drug_name: Optional[str] = None):
    """Check pharmacy medication inventory."""
    return {"pharmacy_id": pharmacy_id, "inventory": []}


@router.post("/pharmacies/{pharmacy_id}/order")
async def place_order(
    pharmacy_id: int,
    order_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Place a medication order for a DOCTOR-APPROVED prescription.

    Body: ``{"prescription_id": int, "patient_confirmed": bool}``. The order is
    assembled by the LLM pharmacy agent; it will refuse unless the prescription
    is approved and the patient has confirmed.
    """
    pharmacy = (
        await db.execute(select(PharmacyModel).where(PharmacyModel.id == pharmacy_id))
    ).scalar_one_or_none()
    if pharmacy is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pharmacy not found")

    prescription_id = order_data.get("prescription_id")
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

    return await pharmacy_service.place_order(
        pharmacy={"id": pharmacy.id, "name": pharmacy.name, "address": pharmacy.address},
        prescription={"approved": prescription.approved, "medications": prescription.medications},
        patient_confirmed=bool(order_data.get("patient_confirmed")),
        order_id=None,
    )


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


async def _get_owned_appointment(
    db: AsyncSession, appointment_id: int, user_id: int
) -> AppointmentModel:
    """Fetch an appointment owned by the user or raise 404."""
    appointment = (
        await db.execute(
            select(AppointmentModel).where(
                AppointmentModel.id == appointment_id,
                AppointmentModel.patient_id == user_id,
            )
        )
    ).scalar_one_or_none()
    if appointment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found")
    return appointment


@router.put("/appointments/{appointment_id}", response_model=Appointment)
async def update_appointment(
    appointment_id: int,
    payload: AppointmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Update (reschedule / edit) an appointment owned by the authenticated patient."""
    appointment = await _get_owned_appointment(db, appointment_id, current_user.id)
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(appointment, field, value)
    await db.commit()
    await db.refresh(appointment)
    return appointment


@router.put("/appointments/{appointment_id}/cancel", response_model=Appointment)
async def cancel_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Cancel an appointment owned by the authenticated patient."""
    appointment = await _get_owned_appointment(db, appointment_id, current_user.id)
    appointment.status = "cancelled"
    await db.commit()
    await db.refresh(appointment)
    return appointment


@router.delete("/appointments/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Permanently delete an appointment owned by the authenticated patient."""
    appointment = await _get_owned_appointment(db, appointment_id, current_user.id)
    await db.delete(appointment)
    await db.commit()


# AI Diagnostics
@router.post("/ai/diagnose")
async def diagnose_medical_file(
    file: UploadFile = File(...),
    modality: Optional[str] = Form(None),
    current_user: UserModel = Depends(get_current_user),
):
    """Run the LVLM diagnostic pipeline on an uploaded image or lab PDF.

    Accepts X-ray / CT / MRI images (jpg, jpeg, png, ...) or lab-report PDFs.
    Runs diagnose -> recheck -> finalise and returns a result that ALWAYS
    requires doctor review before it can drive any treatment.
    """
    raw = await file.read()
    result = await lvlm_service.analyze_file(
        file_bytes=raw, filename=file.filename or "upload", modality=modality
    )
    return result


@router.post("/ai/analyze")
async def analyze_medical_data(data: dict):
    """Run AI analysis on medical data (JSON stub kept for compatibility)."""
    return {"analysis_id": None, "status": "processing"}


@router.get("/ai/results/{analysis_id}")
async def get_analysis_results(analysis_id: str):
    """Get AI analysis results."""
    return {"analysis_id": analysis_id, "results": {}}


# Chat / Patient Assistant
@router.post("/chat/query")
async def chat_query(
    query: dict,
    current_user: UserModel = Depends(get_current_user),
):
    """Send a query to the Patient Assistant Agent (real LLM-backed)."""
    text = (query.get("query") or "").strip()
    if not text:
        return {"response": "Please type a question.", "sources": [], "confidence": 0.0}
    context = query.get("context") or {}
    context.setdefault("user_role", current_user.role)
    return await patient_assistant_service.answer_query(text, context)


# Escalation
@router.post("/escalation/check")
async def check_escalation(symptoms: dict):
    """Check for escalation triggers."""
    return {"escalated": False, "alerts": []}
