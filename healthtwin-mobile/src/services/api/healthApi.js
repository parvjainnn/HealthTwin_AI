import { apiClient } from './client';

export async function analyzeVitals(payload) {
  const { data } = await apiClient.post('/api/analyze', payload);
  return data;
}

export async function saveHealthLog(payload) {
  const { data } = await apiClient.post('/api/save_log', payload);
  return data;
}

export async function fetchHistory() {
  const { data } = await apiClient.get('/api/history');
  return data;
}

export async function fetchWatch(baseHr) {
  const { data } = await apiClient.get(`/api/watch?base_hr=${encodeURIComponent(baseHr || 72)}`);
  return data;
}

export async function askAdvisor(payload) {
  const { data } = await apiClient.post('/api/advisor', payload);
  return data;
}

export async function predictDiabetes(payload) {
  const { data } = await apiClient.post('/api/predict/diabetes', payload);
  return data;
}

export async function predictHeart(payload) {
  const { data } = await apiClient.post('/api/predict/heart', payload);
  return data;
}
