import { apiClient } from './axios';
import type { Profile, ProfileUpdate, PasswordChange, MessageResponse } from '../types';

export const profileApi = {
  get: () => apiClient.get<Profile>('/users/me/profile').then((r) => r.data),

  update: (payload: ProfileUpdate) =>
    apiClient.put<Profile>('/users/me/profile', payload).then((r) => r.data),

  changePassword: (payload: PasswordChange) =>
    apiClient.put<MessageResponse>('/users/me/password', payload).then((r) => r.data),

  uploadAvatar: (file: File) => {
    const form = new FormData();
    form.append('file', file);
    return apiClient
      .post<Profile>('/users/me/avatar', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      .then((r) => r.data);
  },

  removeAvatar: () => apiClient.delete<Profile>('/users/me/avatar').then((r) => r.data),
};
