// Food Logs
export interface FoodLogItemCreateByPortion {
  food_id: number;
  portion_id: number;
  quantity: number;
}

export interface FoodLogItemCreateByGrams {
  food_id: number;
  grams: number;
}

export interface FoodLogEntryCreate {
  logged_at: string; // ISO DateTime
  meal_type: string; // breakfast, lunch, dinner, snacks
  items: (FoodLogItemCreateByPortion | FoodLogItemCreateByGrams)[];
}

export interface DailyNutritionSummary {
  date: string;
  total_calories_consumed: number;
  total_calories_burned: number;
  net_calories: number;
  total_protein_g: number;
  total_carbs_g: number;
  total_fat_g: number;
}

export interface DailyLogsResponse {
  date: string;
  food_logs: any[]; 
  exercise_logs: any[];
  summary: DailyNutritionSummary;
}

// Biometrics Logs
export interface BiometricsCreateRequest {
  logged_at: string; // ISO DateTime
  weight_kg: number;
  height_cm: number;
}

export interface BiometricsPatchRequest {
  logged_at?: string; // ISO DateTime
  weight_kg?: number;
  height_cm?: number;
}

export interface BiometricsLogResponse {
  id: number;
  user_id: string; // UUID as string
  logged_at: string; // ISO DateTime
  weight_kg: number;
  height_cm: number;
  bmi: number;
  created_at: string; // ISO DateTime
}

export interface BiometricsListResponse {
  items: BiometricsLogResponse[];
}

// Exercise Logs
export interface ExerciseLogItemCreate {
  exercise_id: number;
  duration_min?: number; 
  notes?: string;
}

export interface ExerciseLogEntryCreate {
  logged_at: string; // ISO DateTime
  items: ExerciseLogItemCreate[];
}

export interface ExerciseLogItemUpdate {
  duration_min?: number;
  notes?: string;
}

export interface ExerciseLogEntryPatch {
  logged_at?: string;
}