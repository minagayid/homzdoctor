import { apiClient } from './axios';
import type { EscalationResponse } from '../types';

export const escalationApi = {
  check: (symptoms: Record<string, unknown>) =>
    apiClient.post<EscalationResponse>('/escalation/check', symptoms).then((r) => r.data),
};
