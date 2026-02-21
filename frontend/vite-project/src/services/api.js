import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Dashboard APIs
export const getDashboardStatistics = async () => {
  const response = await api.get('/dashboard/statistics');
  return response.data;
};

export const getRiskFactors = async () => {
  const response = await api.get('/dashboard/risk-factors');
  return response.data;
};

export const getRiskyLocations = async (limit = 10) => {
  const response = await api.get(`/dashboard/risky-locations?limit=${limit}`);
  return response.data;
};

export const getSeverityAnalysis = async () => {
  const response = await api.get('/dashboard/severity-analysis');
  return response.data;
};

export const getGeoDistribution = async () => {
  const response = await api.get('/dashboard/geo-distribution');
  return response.data;
};

export const getTimeTrends = async () => {
  const response = await api.get('/dashboard/time-trends');
  return response.data;
};

// Heatmap APIs
export const getRiskHeatmap = async (sampleSize = 1000, severity = null) => {
  const params = new URLSearchParams({ sample_size: sampleSize });
  if (severity !== null) {
    params.append('severity', severity);
  }
  const response = await api.get(`/risk_heatmap?${params.toString()}`);
  return response.data;
};

export const getClusteredHeatmap = async (gridSize = 0.05) => {
  const response = await api.get(`/risk_heatmap_clustered?grid_size=${gridSize}`);
  return response.data;
};

// Prediction APIs
export const predictRisk = async (data) => {
  const response = await api.post('/predict', data);
  return response.data;
};

export const predictLocationRisk = async (lat, lon) => {
  const response = await api.post(`/predict_location?lat=${lat}&lon=${lon}`);
  return response.data;
};

export default api;