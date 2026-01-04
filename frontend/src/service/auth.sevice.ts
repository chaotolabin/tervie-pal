import apiClient from './apiClient';
import { LoginRequest, RegisterRequest, AuthTokensResponse, GenericMessageResponse } from '../types/auth';

export const AuthService = {
  register: async (data: RegisterRequest): Promise<AuthTokensResponse> => {
    const response = await apiClient.post('/auth/register', data);
    return response.data;
  },

  login: async (data: LoginRequest): Promise<AuthTokensResponse> => {
    const response = await apiClient.post('/auth/login', data);
    return response.data;
  },

  refresh: async (refreshToken: string): Promise<{ access_token: string; refresh_token: string }> => {
    const response = await apiClient.post('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  },

  logout: async (refreshToken: string): Promise<void> => {
    await apiClient.post('/auth/logout', { refresh_token: refreshToken });
    localStorage.clear();
  },

  forgotPassword: async (email: string, frontendUrl?: string): Promise<GenericMessageResponse> => {
    const response = await apiClient.post('/auth/forgot-password', { 
      email,
      frontend_url: frontendUrl 
    });
    return response.data;
  },

  resetPassword: async (token: string, newPassword: string): Promise<void> => {
    await apiClient.post('/auth/reset-password', {
      token,
      new_password: newPassword
    });
  }
};