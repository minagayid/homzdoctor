import { apiClient } from './axios';
import type { PharmacySearchResult, OrderResult } from '../types';

export interface PharmacySearchParams {
  lat?: number;
  lon?: number;
  radius_km?: number;
}

export interface OrderRequest {
  prescription_id: number;
  patient_confirmed: boolean;
}

export const pharmaciesApi = {
  /** Search nearby pharmacies, ranked by distance from (lat, lon). */
  search: (params: PharmacySearchParams = {}) =>
    apiClient
      .get<PharmacySearchResult>('/pharmacies/search', { params })
      .then((r) => r.data),

  inventory: (pharmacyId: number, drugName?: string) =>
    apiClient
      .get(`/pharmacies/${pharmacyId}/inventory`, { params: { drug_name: drugName } })
      .then((r) => r.data),

  /** Place a medication order for a doctor-approved prescription. */
  order: (pharmacyId: number, payload: OrderRequest) =>
    apiClient.post<OrderResult>(`/pharmacies/${pharmacyId}/order`, payload).then((r) => r.data),
};
