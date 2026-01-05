import axios, { AxiosError } from 'axios';

// Detect environment - simple and safe
const API_BASE_URL = window.location.hostname === 'localhost' 
  ? 'http://localhost:8000/api/v1'
  : 'https://tervie-backend.onrender.com/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Tự động thêm Token vào Header
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor để tự động refresh token khi hết hạn
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: any) => void;
  reject: (error?: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as any;

    // Nếu lỗi 401 và chưa retry
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Nếu đang refresh, thêm request vào queue
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return api(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = localStorage.getItem('refresh_token');
      
      if (!refreshToken) {
        // Không có refresh token, đăng xuất
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        processQueue(new Error('No refresh token'), null);
        window.location.href = '/login';
        return Promise.reject(error);
      }

      try {
        const REFRESH_URL = window.location.hostname === 'localhost'
          ? 'http://localhost:8000/api/v1/auth/refresh'
          : 'https://tervie-backend.onrender.com/api/v1/auth/refresh';
          
        // Gọi API refresh token
        const response = await axios.post(
          REFRESH_URL,
          { refresh_token: refreshToken },
          { headers: { 'Content-Type': 'application/json' } }
        );

        const { access_token, refresh_token: newRefreshToken } = response.data;
        
        // Lưu token mới
        localStorage.setItem('access_token', access_token);
        if (newRefreshToken) {
          localStorage.setItem('refresh_token', newRefreshToken);
        }

        // Cập nhật header cho request gốc
        originalRequest.headers.Authorization = `Bearer ${access_token}`;

        // Xử lý queue
        processQueue(null, access_token);

        // Retry request gốc
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh token cũng hết hạn, đăng xuất
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        processQueue(refreshError, null);
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

export default api;