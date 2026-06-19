export interface User {
  id: number;
  email: string;
  fullName: string;
  role: 'patient' | 'doctor' | 'admin';
  isActive: boolean;
  createdAt: string;
  /** Base64 data URL of the profile picture (synced from the profile API). */
  avatarUrl?: string;
}

export interface MedicalRecord {
  id: number;
  patientId: number;
  recordType: string;
  filePath: string;
  fileMetadata?: Record<string, unknown>;
  findings?: string;
  diagnosis?: string;
  confidenceScore?: number;
  doctorReviewed: boolean;
  doctorNotes?: string;
  status: string;
  createdAt: string;
}

export interface DoctorReview {
  id: number;
  recordId: number;
  doctorId: number;
  action: string;
  notes?: string;
  prescription?: Record<string, unknown>;
  createdAt: string;
}

export interface Prescription {
  id: number;
  doctorId: number;
  patientId: number;
  recordId: number;
  medications: Array<Record<string, unknown>>;
  approved: boolean;
  createdAt: string;
}

export interface Pharmacy {
  id: number;
  name: string;
  address: string;
  latitude: number;
  longitude: number;
  phone?: string;
  isOpen: boolean;
  createdAt: string;
}

export interface MedicationAdherence {
  id: number;
  prescriptionId: number;
  medicationName: string;
  scheduledTime: string;
  status: string;
  takenAt?: string;
}

export interface Appointment {
  id: number;
  patientId: number;
  doctorId?: number;
  reason?: string;
  scheduledTime: string;
  status: string;
  createdAt: string;
}

// Request/response payload types.
export * from './api';
