import apiClient from './apiClient';
import { FoodSearchResponse, FoodDetail } from '../types/food';

export const FoodService = {
  search: async (query: string, limit: number = 20): Promise<FoodSearchResponse> => {
    const response = await apiClient.get('/foods/search', {
      params: { q: query, limit }
    });
    return response.data;
  },

  getDetail: async (foodId: number): Promise<FoodDetail> => {
    const response = await apiClient.get(`/foods/${foodId}`);
    return response.data;
  },

  createCustomFood: async (data: any): Promise<FoodDetail> => {
    const response = await apiClient.post('/foods', data);
    return response.data;
  }
};