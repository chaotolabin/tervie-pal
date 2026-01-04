export enum GoalType {
  LOSE_WEIGHT = "lose_weight",
  GAIN_WEIGHT = "gain_weight",
  MAINTAIN_WEIGHT = "maintain_weight",
  BUILD_MUSCLE = "build_muscle",
  IMPROVE_HEALTH = "improve_health"
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
  protein_g: number;
  carbs_g: number;
  fat_g: number;
}