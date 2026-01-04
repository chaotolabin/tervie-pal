import apiClient from './apiClient';
import { FoodLogEntryCreate, DailyLogsResponse, DailyNutritionSummary, FoodLogEntryPatch, FoodLogItemUpdate, ExerciseLogEntryCreate, ExerciseLogEntryPatch, ExerciseLogItemUpdate } from '../types/logs';

export const LogService = {
  // ========== FOOD LOGS ==========
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

  // Lấy food logs trong ngày
  getDailyFoodLogs: async (date: string): Promise<any[]> => {
    const response = await apiClient.get(`/logs/food/daily/${date}`);
    return response.data;
  },

  // Lấy chi tiết một bữa ăn
  getFoodLogDetail: async (entryId: number): Promise<any> => {
    const response = await apiClient.get(`/logs/food/${entryId}`);
    return response.data;
  },

  // Cập nhật bữa ăn
  updateFoodLog: async (entryId: number, data: FoodLogEntryPatch): Promise<any> => {
    const response = await apiClient.patch(`/logs/food/${entryId}`, data);
    return response.data;
  },

  // Cập nhật món ăn trong bữa ăn
  updateFoodLogItem: async (itemId: number, data: FoodLogItemUpdate): Promise<any> => {
    const response = await apiClient.patch(`/logs/food/items/${itemId}`, data);
    return response.data;
  },

  // Xóa một log item
  deleteFoodLog: async (entryId: number): Promise<void> => {
    await apiClient.delete(`/logs/food/${entryId}`);
  },

  // ========== EXERCISE LOGS ==========
  // Tạo log buổi tập
  addExerciseLog: async (data: ExerciseLogEntryCreate): Promise<any> => {
    const response = await apiClient.post('/logs/exercise', data);
    return response.data;
  },

  // Lấy exercise logs trong ngày
  getDailyExerciseLogs: async (date: string): Promise<any[]> => {
    const response = await apiClient.get(`/logs/exercise/daily/${date}`);
    return response.data;
  },

  // Lấy chi tiết một buổi tập
  getExerciseLogDetail: async (entryId: number): Promise<any> => {
    const response = await apiClient.get(`/logs/exercise/${entryId}`);
    return response.data;
  },

  // Cập nhật buổi tập
  updateExerciseLog: async (entryId: number, data: ExerciseLogEntryPatch): Promise<any> => {
    const response = await apiClient.patch(`/logs/exercise/${entryId}`, data);
    return response.data;
  },

  // Cập nhật bài tập trong buổi tập
  updateExerciseLogItem: async (itemId: number, data: ExerciseLogItemUpdate): Promise<any> => {
    const response = await apiClient.patch(`/logs/exercise/items/${itemId}`, data);
    return response.data;
  },

  // Xóa buổi tập
  deleteExerciseLog: async (entryId: number): Promise<void> => {
    await apiClient.delete(`/logs/exercise/${entryId}`);
  },

  // ========== SUMMARY ==========
  // Lấy nhanh summary (Dùng cho Dashboard)
  getSummary: async (date: string): Promise<DailyNutritionSummary> => {
    const response = await apiClient.get(`/logs/summary/${date}`);
    return response.data;
  }
};