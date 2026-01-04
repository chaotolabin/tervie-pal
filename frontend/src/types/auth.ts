import { Gender, ActivityLevel } from './common';

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  full_name: string;
  gender: Gender;
  date_of_birth: string; // YYYY-MM-DD
  height_cm: number;
  weight_kg: number;
  goal_weight_kg?: number;
  goal_type: string;
  baseline_activity: ActivityLevel;
  weekly_goal: number;
  weekly_exercise_min?: number;
}

export interface LoginRequest {
  email_or_username: string;
  password: string;
  device_label?: string;
}

export interface AuthTokensResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: UserPublic;
}

export interface UserPublic {
  id: string; // UUID
  username: string;
  email: string;
  role: 'user' | 'admin';
}