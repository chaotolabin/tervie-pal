export interface ErrorResponse {
  detail: string;
}

export interface GenericMessageResponse {
  message: string;
}

export type Gender = 'male' | 'female';

export enum ActivityLevel {
  SEDENTARY = 'sedentary',
  LOW_ACTIVE = 'low_active',
  MODERATELY_ACTIVE = 'moderately_active',
  VERY_ACTIVE = 'very_active',
  EXTREMELY_ACTIVE = 'extremely_active'
}