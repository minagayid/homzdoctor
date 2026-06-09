"""
Pydantic schemas for HomzDoctor.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles."""
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"


class UserBase(BaseModel):
    """Base user schema."""
    email: str
    full_name: str
    role: UserRole = UserRole.PATIENT
    is_active: bool = True


class UserCreate(UserBase):
    """User creation schema."""
    password: str


class User(UserBase):
    """User response schema."""
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class MedicalRecord(BaseModel):
    """Medical record schema."""
    id: int
    patient_id: int
    record_type: str  # e.g., "xray", "mri", "ct", "lab_report"
    file_path: str
    findings: Optional[str] = None
    diagnosis: Optional[str] = None
    confidence_score: Optional[float] = None
    doctor_reviewed: bool = False
    doctor_notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


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


class Prescription(BaseModel):
    """Prescription schema."""
    id: int
    doctor_id: int
    patient_id: int
    record_id: int
    medications: List[dict]
    approved: bool = False
    created_at: datetime
    
    class Config:
        from_attributes = True


class Pharmacy(BaseModel):
    """Pharmacy schema."""
    id: int
    name: str
    address: str
    latitude: float
    longitude: float
    phone: Optional[str] = None
    is_open: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True


class MedicationAdherence(BaseModel):
    """Medication adherence schema."""
    id: int
    prescription_id: int
    medication_name: str
    scheduled_time: datetime
    status: str  # taken, skipped, missed
    taken_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
