export enum GoalType {
  LOSE_WEIGHT = "lose_weight",
  GAIN_WEIGHT = "gain_weight",
  MAINTAIN_WEIGHT = "maintain_weight",
  BUILD_MUSCLE = "build_muscle",
  IMPROVE_HEALTH = "improve_health"
}

export enum ActivityLevel {
  SEDENTARY = "sedentary",
  LOW_ACTIVE = "low_active",
  MODERATELY_ACTIVE = "moderately_active",
  VERY_ACTIVE = "very_active",
  EXTREMELY_ACTIVE = "extremely_active"
}

export interface GoalCalculateRequest {
  goal_type: GoalType;
  baseline_activity: ActivityLevel;
  weekly_goal?: number;
}

export interface GoalCalculateResponse {
  goal_type: string;
  baseline_activity: string;
  weekly_goal: number;
  weight_kg: number;
  height_cm: number;
  bmr: number;
  tdee: number;
  daily_calorie_target: number;
  protein_grams: number;
  carb_grams: number;
  fat_grams: number;
}

export interface GoalResponse {
  user_id: string;
  goal_type: string;
  baseline_activity?: string;
  weekly_goal?: number;
  target_weight_kg?: number;
  daily_calorie_target: number;
  protein_grams?: number;
  fat_grams?: number;
  carb_grams?: number;
  weekly_exercise_min?: number;
  created_at: string;
  updated_at: string;
}

export interface GoalPatchRequest {
  goal_type?: GoalType;
  baseline_activity?: ActivityLevel;
  weekly_goal?: number;
  target_weight_kg?: number;
  weekly_exercise_min?: number;
}