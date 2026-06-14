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

// ---- Pharmacy ----
export interface PharmacySearchParams {
  lat: number;
  lon: number;
  radius_km?: number;
}

// ---- Escalation ----
export interface EscalationResponse {
  escalated: boolean;
  alerts: unknown[];
}

/** Generic message envelope returned by many placeholder endpoints. */
export interface MessageResponse {
  message: string;
  [key: string]: unknown;
}
