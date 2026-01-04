import apiClient from './apiClient';
import { GoalCalculateRequest, GoalCalculateResponse, GoalResponse, GoalPatchRequest } from '../types/goals';

export const GoalService = {
  // Tính toán thử Calo mục tiêu (Không lưu)
  calculatePreview: async (data: GoalCalculateRequest): Promise<GoalCalculateResponse> => {
    const response = await apiClient.post('/goals/calculate', data);
    return response.data;
  },

  // Lưu mục tiêu mới (thay thế toàn bộ)
  createOrUpdateGoal: async (data: any): Promise<GoalResponse> => {
    const response = await apiClient.put('/goals', data);
    return response.data;
  },

  // Cập nhật một phần mục tiêu
  patchGoal: async (data: GoalPatchRequest): Promise<GoalResponse> => {
    const response = await apiClient.patch('/goals', data);
    return response.data;
  },

  getCurrentGoal: async (): Promise<GoalResponse> => {
    const response = await apiClient.get('/goals');
    return response.data;
  }
};