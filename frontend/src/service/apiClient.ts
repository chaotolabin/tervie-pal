import api from '../utils/axiosInstance';

export const logService = {
  // Lấy toàn bộ nhật ký ăn uống & tập luyện trong ngày
  getDailyLogs: (date: string) => api.get(`/logs/${date}`),
  // Tạo log bữa ăn mới
  createFoodLog: (data: any) => api.post('/logs/food', data),
  // Lấy tóm tắt dinh dưỡng (Calories, P, C, F)
  getNutritionSummary: (date: string) => api.get(`/logs/summary/${date}`),
};

export const biometricService = {
  // Tạo log cân nặng/chiều cao mới
  createLog: (data: any) => api.post('/biometrics', data),
  // Lấy lịch sử chỉ số
  getHistory: (limit = 30) => api.get(`/biometrics?limit=${limit}`),
};

export const blogService = {
  // Lấy bảng tin (Feed)
  getFeed: (params: any) => api.get('/blog/feed', { params }),
  // Like bài viết
  likePost: (postId: string) => api.post(`/blog/posts/${postId}/like`),
};