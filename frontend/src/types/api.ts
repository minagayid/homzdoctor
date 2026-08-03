/**
 * Request/response payload types for the API layer.
 * Entity types (User, MedicalRecord, ...) live in ./index.
 */
import type { User } from './index';

// ---- Auth ----
export interface UserCreate {
  email: string;
  password: string;
  fullName: string;
  role: User['role'];
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

// ---- Chat / Patient Assistant ----
export interface ChatQuery {
  query: string;
  context?: Record<string, unknown>;
}

export interface ChatResponse {
  response: string;
  sources: unknown[];
}

// ---- AI Diagnostics ----
export type AnalyzeRequest = Record<string, unknown>;

export interface AnalyzeResponse {
  analysis_id: string | null;
  status: string;
}

export interface AnalysisResult {
  analysis_id: string;
  results: Record<string, unknown>;
}

/** Result of the LVLM diagnostic pipeline (`POST /ai/diagnose`). */
export interface DiagnosisResult {
  modality: string;
  model: string;
  pages_analyzed?: number;
  draft_diagnosis?: {
    observations?: string[];
    suspected_conditions?: Array<{ condition: string; likelihood: string }>;
    differential_diagnosis?: string[];
    image_quality?: string;
    confidence?: number;
    urgent_findings?: string[];
    raw?: string;
  };
  recheck?: {
    unsupported_findings?: string[];
    missed_findings?: string[];
    agreement?: string;
    confidence_adjustment?: string;
    notes?: string;
    raw?: string;
  };
  final_diagnosis?: {
    final_findings?: string[];
    primary_impression?: string;
    differential_diagnosis?: string[];
    confidence?: number;
    recommended_next_steps?: string[];
    urgent?: boolean;
  };
  confidence?: number;
  urgent?: boolean;
  doctor_review_required?: boolean;
  disclaimer?: string;
  error?: string;
  /** Set when the upload was not a medical image/report (triage rejected it). */
  rejected?: boolean;
  document_type?: string;
  message?: string;
}

// ---- Pharmacy ----
export interface PharmacySearchParams {
  lat?: number;
  lon?: number;
  radius_km?: number;
}

/** A pharmacy as returned by the search agent (snake_case, distance added). */
export interface PharmacyResult {
  id?: number;
  name: string;
  address?: string;
  latitude?: number;
  longitude?: number;
  phone?: string;
  is_open?: boolean;
  rating?: number;
  place_id?: string;
  distance_km?: number;
}

/** Response of `GET /pharmacies/search`. */
export interface PharmacySearchResult {
  pharmacies: PharmacyResult[];
  count: number;
  source: string;
  radius_km: number;
  summary: string;
}

export interface OrderItem {
  name?: string;
  dose?: string;
  frequency?: string;
  duration?: string;
  quantity?: number;
}

/** Response of `POST /pharmacies/{id}/order`. */
export interface OrderResult {
  order_placed?: boolean;
  requires_confirmation?: boolean;
  error?: string;
  order_id?: number | null;
  pharmacy?: { id?: number; name?: string };
  items?: OrderItem[];
  order_preview?: OrderItem[];
  status?: string;
  confirmation_message?: string;
}

// ---- Profile & settings ----
export interface Profile {
  id: number;
  email: string;
  fullName: string;
  role: 'patient' | 'doctor' | 'admin';
  isActive: boolean;
  createdAt: string;
  // Personal
  phone?: string;
  avatarUrl?: string;
  bio?: string;
  gender?: string;
  dateOfBirth?: string;
  address?: string;
  city?: string;
  country?: string;
  // Doctor-specific
  specialty?: string;
  licenseNumber?: string;
  hospital?: string;
  yearsExperience?: number;
  qualifications?: string;
  consultationFee?: string;
  // Preferences
  language: string;
  timezone: string;
  theme: string;
  // Notifications
  notifyEmail: boolean;
  notifySms: boolean;
  notifyPush: boolean;
  notifyWhatsapp: boolean;
}

export type ProfileUpdate = Partial<Omit<Profile, 'id' | 'email' | 'role' | 'isActive' | 'createdAt'>>;

export interface PasswordChange {
  currentPassword: string;
  newPassword: string;
}

// ---- Escalation ----
export interface EscalationResponse {
  escalated: boolean;
  alerts: unknown[];
}

/** Generic message envelope returned by simple API operations. */
export interface MessageResponse {
  message: string;
  [key: string]: unknown;
}
