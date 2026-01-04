import apiClient from './apiClient';
import { GoalCalculateRequest, GoalCalculateResponse, GoalResponse } from '../types/goals';

export const GoalService = {
  // Tính toán thử Calo mục tiêu (Không lưu)
  calculatePreview: async (data: GoalCalculateRequest): Promise<GoalCalculateResponse> => {
    const response = await apiClient.post('/goals/calculate', data);
    return response.data;
  },

  // Lưu mục tiêu mới
  updateGoal: async (data: any): Promise<GoalResponse> => {
    const response = await apiClient.put('/goals', data);
    return response.data;
  },

  getCurrentGoal: async (): Promise<GoalResponse> => {
    const response = await apiClient.get('/goals');
    return response.data;
  }
};