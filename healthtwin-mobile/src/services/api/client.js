import axios from 'axios';

const DEFAULT_API_URL = process.env.EXPO_PUBLIC_API_BASE_URL || 'http://10.0.2.2:5000';

export const apiClient = axios.create({
  baseURL: DEFAULT_API_URL,
  timeout: 15000,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
});

export function setApiBaseUrl(nextUrl) {
  const sanitized = (nextUrl || '').trim().replace(/\/+$/, '');
  if (!sanitized) return;
  apiClient.defaults.baseURL = sanitized;
}

export function normalizeApiError(error) {
  if (error?.response?.data?.error) return error.response.data.error;
  if (error?.response?.data?.message) return error.response.data.message;
  if (error?.message) return error.message;
  return 'Request failed. Please try again.';
}
