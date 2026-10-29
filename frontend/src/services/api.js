import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT auth header
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('coal_mine_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for session expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Optional: Handle token expiration
    }
    return Promise.reject(error);
  }
);

// Auth
export const loginApi = (email, password) => api.post('/auth/login', { email, password });
export const registerApi = (userData) => api.post('/auth/register', userData);
export const getMeApi = () => api.get('/auth/me');

// Dashboard
export const getDashboardSummaryApi = () => api.get('/dashboard/summary');

// Digital Twin
export const getDigitalTwinApi = (replayOffset = 0) => api.get(`/digital-twin/overview?replay_offset_minutes=${replayOffset}`);
export const getZonePanelApi = (zoneId) => api.get(`/digital-twin/zone-panel/${zoneId}`);

// Zones
export const getZonesApi = () => api.get('/zones/');
export const getZoneDetailsApi = (id) => api.get(`/zones/${id}`);

// PPE Detection
export const getPPEDetectionsApi = (params) => api.get('/ppe/detections', { params });
export const detectPPEApi = (formData) => api.post('/ppe/detect', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});
export const confirmPPEDetectionApi = (id, data) => api.post(`/ppe/confirm/${id}`, data);

// Sensors
export const getSensorsApi = (zoneId) => api.get('/sensors/', { params: { zone_id: zoneId } });
export const getSensorHistoryApi = (sensorId) => api.get(`/sensors/${sensorId}/history`);
export const postSensorReadingApi = (data) => api.post('/sensors/reading', data);
export const uploadSensorCsvApi = (formData) => api.post('/sensors/upload-csv', formData, {
  headers: { 'Content-Type': 'multipart/form-data' }
});
export const triggerSimulatorPulseApi = () => api.post('/sensors/simulate-live-pulse');
export const toggleStreamerApi = (active, interval = 4.0) => api.post(`/sensors/streamer/toggle?active=${active}&interval_seconds=${interval}`);
export const getStreamerStatusApi = () => api.get('/sensors/streamer/status');

// Risk & Explainable AI
export const predictZoneRiskApi = (zoneId, forecastShift) => api.post('/risk/predict', { zone_id: zoneId, forecast_shift: forecastShift });
export const getNextShiftForecastApi = () => api.get('/risk/forecast/next-shift');

// Compliance Cases
export const getCasesApi = (params) => api.get('/compliance/cases', { params });
export const getCaseDetailsApi = (id) => api.get(`/compliance/cases/${id}`);
export const createCaseApi = (data) => api.post('/compliance/cases', data);
export const updateCaseApi = (id, data) => api.patch(`/compliance/cases/${id}`, data);
export const addCaseCommentApi = (id, comment) => api.post(`/compliance/cases/${id}/comments`, { comment });

// Corrective Actions
export const getActionsApi = (params) => api.get('/actions/', { params });
export const createActionApi = (data) => api.post('/actions/', data);
export const updateActionApi = (id, data) => api.patch(`/actions/${id}`, data);

// Workers & Wearables
export const getWorkersApi = (params) => api.get('/workers/', { params });
export const postHealthReadingApi = (data) => api.post('/workers/health-reading', data);

// Equipment
export const getEquipmentApi = (params) => api.get('/equipment/', { params });
export const postEquipmentReadingApi = (data) => api.post('/equipment/reading', data);

// Reports
export const getReportsApi = () => api.get('/reports/');
export const generateReportApi = (data) => api.post('/reports/generate', data);
export const getReportDownloadUrl = (reportId) => `${API_BASE_URL}/reports/download/${reportId}`;

// Governance & Audit
export const getAuditLogsApi = (params) => api.get('/governance/audit-logs', { params });
export const getNotificationsApi = (unreadOnly = false) => api.get('/governance/notifications', { params: { unread_only: unreadOnly } });
export const markNotificationReadApi = (id) => api.post(`/governance/notifications/${id}/read`);
export const markAllNotificationsReadApi = () => api.post('/governance/notifications/read-all');

export default api;

