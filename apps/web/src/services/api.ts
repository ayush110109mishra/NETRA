import axios, { AxiosError } from 'axios';
import {
  ApiResponse,
  ApiErrorResponse,
  HealthCheckData,
  SystemStatus,
  CommandKpis,
  Assessment,
  Entity,
  Alert,
  Event,
  Evidence,
  IntelligenceFeedItem,
  AskNetraQuery,
  AskNetraResponse,
} from '@netra/shared';

// Use environment variable if provided, or default to Vite proxy / relative path
const BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

// Request interceptor: add client correlation tags
apiClient.interceptors.request.use(
  (config) => {
    config.headers['X-Client-Timestamp'] = new Date().toISOString();
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor: extract response envelope or uniform error message
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<ApiErrorResponse>) => {
    const errorData = error.response?.data;
    const message =
      errorData?.error?.message ||
      error.message ||
      'Tactical network communication error';

    return Promise.reject(new Error(message));
  }
);

/**
 * Core API service operations
 */
export const netraApi = {
  getHealth: async (): Promise<HealthCheckData> => {
    const response = await apiClient.get<ApiResponse<HealthCheckData>>('/health');
    return response.data.data;
  },

  getSystemStatus: async (): Promise<SystemStatus> => {
    const response = await apiClient.get<ApiResponse<SystemStatus>>('/system');
    return response.data.data;
  },

  getKpis: async (): Promise<CommandKpis> => {
    const response = await apiClient.get<ApiResponse<CommandKpis>>('/kpis');
    return response.data.data;
  },

  getAssessment: async (): Promise<Assessment> => {
    const response = await apiClient.get<ApiResponse<Assessment>>('/assessment');
    return response.data.data;
  },

  getEntities: async (params?: { type?: string; status?: string }): Promise<Entity[]> => {
    const response = await apiClient.get<ApiResponse<Entity[]>>('/entities', { params });
    return response.data.data;
  },

  getEntityById: async (id: string): Promise<Entity> => {
    const response = await apiClient.get<ApiResponse<Entity>>(`/entities/${id}`);
    return response.data.data;
  },

  getAlerts: async (params?: { severity?: string; status?: string }): Promise<Alert[]> => {
    const response = await apiClient.get<ApiResponse<Alert[]>>('/alerts', { params });
    return response.data.data;
  },

  getEvents: async (params?: { type?: string; severity?: string }): Promise<Event[]> => {
    const response = await apiClient.get<ApiResponse<Event[]>>('/events', { params });
    return response.data.data;
  },

  getEvidence: async (params?: { entityId?: string; eventId?: string }): Promise<Evidence[]> => {
    const response = await apiClient.get<ApiResponse<Evidence[]>>('/evidence', { params });
    return response.data.data;
  },

  getFeed: async (): Promise<IntelligenceFeedItem[]> => {
    const response = await apiClient.get<ApiResponse<IntelligenceFeedItem[]>>('/feed');
    return response.data.data;
  },

  askNetra: async (queryPayload: AskNetraQuery): Promise<AskNetraResponse> => {
    const response = await apiClient.post<ApiResponse<AskNetraResponse>>('/ask', queryPayload);
    return response.data.data;
  },
};
