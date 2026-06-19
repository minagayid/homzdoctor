"""
SQLAlchemy models for HomzDoctor.
"""

from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from core.database import Base


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default="patient")  # patient, doctor, admin
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserProfile(Base):
    """Extended profile + preferences for a user (one-to-one with User).

    Kept in a SEPARATE table so it is auto-created by ``create_all`` without an
    ALTER migration on the existing ``users`` table. A row is created lazily the
    first time a user opens their profile.
    """
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    # --- Common personal info (patients and doctors) ---
    phone = Column(String(50))
    # Stores the avatar IMAGE itself as a base64 data URL (compressed thumbnail),
    # so it lives entirely in the database — no filesystem needed. Text, not a
    # bounded VARCHAR, because encoded images exceed any small length.
    avatar_url = Column(Text)
    bio = Column(Text)
    gender = Column(String(20))
    date_of_birth = Column(String(20))  # ISO date string (kept simple)
    address = Column(Text)
    city = Column(String(120))
    country = Column(String(120))

    # --- Doctor-specific info (only meaningful when user.role == "doctor") ---
    specialty = Column(String(120))
    license_number = Column(String(120))
    hospital = Column(String(255))
    years_experience = Column(Integer)
    qualifications = Column(Text)
    consultation_fee = Column(String(50))

    # --- Preferences ---
    language = Column(String(20), default="en")
    timezone = Column(String(60), default="UTC")
    theme = Column(String(20), default="system")  # light, dark, system

    # --- Notification settings ---
    notify_email = Column(Boolean, default=True)
    notify_sms = Column(Boolean, default=False)
    notify_push = Column(Boolean, default=True)
    notify_whatsapp = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", foreign_keys=[user_id])


class MedicalRecord(Base):
    """Medical record model."""
    __tablename__ = "medical_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    record_type = Column(String(50), nullable=False)  # xray, mri, ct, lab_report, etc.
    file_path = Column(String(500), nullable=False)
    file_metadata = Column(JSON, default={})  # DICOM metadata, dimensions, etc.
    findings = Column(Text)
    diagnosis = Column(Text)
    confidence_score = Column(Float)
    doctor_reviewed = Column(Boolean, default=False)
    doctor_notes = Column(Text)
    status = Column(String(50), default="pending")  # pending, reviewed, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("User", foreign_keys=[patient_id])
    reviews = relationship("DoctorReview", back_populates="medical_record")


class DoctorReview(Base):
    """Doctor review model."""
    __tablename__ = "doctor_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("medical_records.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)  # approve, modify, reject
    notes = Column(Text)
    prescription = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    medical_record = relationship("MedicalRecord", back_populates="reviews")
    doctor = relationship("User", foreign_keys=[doctor_id])


class Prescription(Base):
    """Prescription model."""
    __tablename__ = "prescriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    record_id = Column(Integer, ForeignKey("medical_records.id"), nullable=False)
    medications = Column(JSON, default=[])  # List of medication dicts
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    doctor = relationship("User", foreign_keys=[doctor_id])
    patient = relationship("User", foreign_keys=[patient_id])


class Pharmacy(Base):
    """Pharmacy model."""
    __tablename__ = "pharmacies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    phone = Column(String(50))
    is_open = Column(Boolean, default=True)
    operating_hours = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)


class MedicationAdherence(Base):
    """Medication adherence tracking model."""
    __tablename__ = "medication_adherence"

    id = Column(Integer, primary_key=True, index=True)
    prescription_id = Column(Integer, ForeignKey("prescriptions.id"), nullable=False)
    medication_name = Column(String(255), nullable=False)
    scheduled_time = Column(DateTime, nullable=False)
    status = Column(String(50), default="pending")  # pending, taken, skipped, missed
    taken_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Appointment(Base):
    """Doctor appointment model."""
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"))
    reason = Column(String(255))
    scheduled_time = Column(DateTime, nullable=False)
    status = Column(String(50), default="scheduled")  # scheduled, cancelled, completed
    created_at = Column(DateTime, default=datetime.utcnow)
