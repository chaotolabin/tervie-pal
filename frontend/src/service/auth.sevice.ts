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

  logout: async (refreshToken: string): Promise<void> => {
    await apiClient.post('/auth/logout', { refresh_token: refreshToken });
    localStorage.clear();
  },

  forgotPassword: async (email: string): Promise<GenericMessageResponse> => {
    const response = await apiClient.post('/auth/forgot-password', { email });
    return response.data;
  }
};