"""
Pydantic schemas for HomzDoctor.
"""

from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles."""
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"


class UserBase(BaseModel):
    """Base user schema.

    Accepts camelCase keys from the frontend (e.g. ``fullName``) via the alias
    generator, while ``populate_by_name`` still allows snake_case (``full_name``).
    """
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    email: str
    full_name: str
    role: UserRole = UserRole.PATIENT
    is_active: bool = True


class UserCreate(UserBase):
    """User creation schema."""
    password: str


class User(UserBase):
    """User response schema (serialized with camelCase keys)."""
    id: int
    created_at: datetime

    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )


class LoginRequest(BaseModel):
    """Login credentials."""
    email: str
    password: str


class Token(BaseModel):
    """JWT access token response."""
    access_token: str
    token_type: str = "bearer"


class MedicalRecordCreate(BaseModel):
    """Schema for creating a medical record (camelCase accepted)."""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    record_type: str  # e.g., "xray", "mri", "ct", "lab_report"
    file_path: str
    findings: Optional[str] = None
    diagnosis: Optional[str] = None


class MedicalRecordUpdate(BaseModel):
    """Schema for updating a medical record. All fields optional (partial update)."""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    record_type: Optional[str] = None
    file_path: Optional[str] = None
    findings: Optional[str] = None
    diagnosis: Optional[str] = None


class MedicalRecord(BaseModel):
    """Medical record response schema (serialized with camelCase keys)."""
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )

    id: int
    patient_id: int
    record_type: str  # e.g., "xray", "mri", "ct", "lab_report"
    file_path: str
    file_metadata: Optional[dict] = None
    findings: Optional[str] = None
    diagnosis: Optional[str] = None
    confidence_score: Optional[float] = None
    doctor_reviewed: bool = False
    doctor_notes: Optional[str] = None
    status: str
    created_at: datetime


class DoctorReview(BaseModel):
    """Doctor review schema."""
    id: int
    record_id: int
    doctor_id: int
    action: str  # approve, modify, reject
    notes: Optional[str] = None
    prescription: Optional[dict] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class PrescriptionCreate(BaseModel):
    """Schema for creating a prescription (camelCase accepted)."""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    patient_id: int
    record_id: int
    medications: List[dict]


class Prescription(BaseModel):
    """Prescription response schema (serialized with camelCase keys)."""
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )

    id: int
    doctor_id: int
    patient_id: int
    record_id: int
    medications: List[dict]
    approved: bool = False
    created_at: datetime


class Pharmacy(BaseModel):
    """Pharmacy response schema (serialized with camelCase keys)."""
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )

    id: int
    name: str
    address: str
    latitude: float
    longitude: float
    phone: Optional[str] = None
    is_open: bool = True
    created_at: datetime


class MedicationAdherence(BaseModel):
    """Medication adherence response schema (serialized with camelCase keys)."""
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )

    id: int
    prescription_id: int
    medication_name: str
    scheduled_time: datetime
    status: str  # taken, skipped, missed
    taken_at: Optional[datetime] = None


class AppointmentCreate(BaseModel):
    """Schema for booking an appointment (camelCase accepted)."""
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    reason: str
    scheduled_time: datetime


class Appointment(BaseModel):
    """Appointment response schema (serialized with camelCase keys)."""
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )

    id: int
    patient_id: int
    doctor_id: Optional[int] = None
    reason: Optional[str] = None
    scheduled_time: datetime
    status: str
    created_at: datetime
