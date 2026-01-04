import apiClient from './apiClient';
import { FoodLogEntryCreate, DailyLogsResponse, DailyNutritionSummary } from '../types/logs';

export const LogService = {
  // Lấy toàn bộ log của một ngày (Food + Exercise + Summary)
  getDailyLogs: async (date: string): Promise<DailyLogsResponse> => {
    const response = await apiClient.get(`/logs/daily/${date}`);
    return response.data;
  },

  // Thêm món ăn vào nhật ký
  addFoodLog: async (data: FoodLogEntryCreate): Promise<any> => {
    const response = await apiClient.post('/logs/food', data);
    return response.data;
  },

  // Xóa một log item
  deleteFoodLog: async (entryId: string): Promise<void> => {
    await apiClient.delete(`/logs/food/${entryId}`);
  },

  // Lấy nhanh summary (Dùng cho Dashboard)
  getSummary: async (date: string): Promise<DailyNutritionSummary> => {
    const response = await apiClient.get(`/logs/summary/${date}`);
    return response.data;
  }
};