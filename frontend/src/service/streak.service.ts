import apiClient from './apiClient';

export const StreakService = {
  getStreakInfo: async () => {
    const response = await apiClient.get('/streak');
    return response.data;
  },
  
  getWeekWindow: async (endDay?: string) => {
    const response = await apiClient.get('/streak/week', {
      params: { end_day: endDay }
    });
    return response.data;
  }
};