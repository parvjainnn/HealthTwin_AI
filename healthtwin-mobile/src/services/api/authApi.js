import { apiClient } from './client';

export async function loginApi(payload) {
  const { data } = await apiClient.post('/api/mobile/auth/login', payload);
  return data;
}

export async function registerApi(payload) {
  const { data } = await apiClient.post('/api/mobile/auth/register', payload);
  return data;
}

export async function meApi() {
  const { data } = await apiClient.get('/api/mobile/auth/me');
  return data;
}

export async function logoutApi() {
  const { data } = await apiClient.post('/api/mobile/auth/logout');
  return data;
}
