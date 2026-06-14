import { apiClient } from './axios';
import type { PharmacySearchParams, MessageResponse } from '../types';

export const pharmaciesApi = {
  search: (params: PharmacySearchParams) =>
    apiClient.get('/pharmacies/search', { params }).then((r) => r.data),

  inventory: (pharmacyId: number, drugName?: string) =>
    apiClient
      .get(`/pharmacies/${pharmacyId}/inventory`, { params: { drug_name: drugName } })
      .then((r) => r.data),

  order: (pharmacyId: number, orderData: Record<string, unknown>) =>
    apiClient.post<MessageResponse>(`/pharmacies/${pharmacyId}/order`, orderData).then((r) => r.data),
};
