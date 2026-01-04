import apiClient from './apiClient';
import { BiometricsCreateRequest, BiometricsPatchRequest, BiometricsLogResponse, BiometricsListResponse } from '../types/logs';

export const BiometricService = {
  createLog: async (data: BiometricsCreateRequest): Promise<BiometricsLogResponse> => {
    const response = await apiClient.post('/biometrics', data);
    return response.data;
  },

  getHistory: async (fromDate?: string, toDate?: string, limit: number = 30): Promise<BiometricsListResponse> => {
    const params: any = { limit };
    if (fromDate) params.from = fromDate;
    if (toDate) params.to = toDate;
    const response = await apiClient.get('/biometrics', { params });
    return response.data;
  },

  getLatest: async (): Promise<BiometricsLogResponse> => {
    const response = await apiClient.get('/biometrics/latest');
    return response.data;
  },

  updateLog: async (biometricId: number, data: BiometricsPatchRequest): Promise<BiometricsLogResponse> => {
    const response = await apiClient.patch(`/biometrics/${biometricId}`, data);
    return response.data;
  },

  deleteLog: async (biometricId: number): Promise<void> => {
    await apiClient.delete(`/biometrics/${biometricId}`);
  },

  getSummary: async (fromDate: string, toDate: string): Promise<any> => {
    const response = await apiClient.get('/biometrics/summary', {
      params: { from: fromDate, to: toDate }
    });
    return response.data;
  }
};

