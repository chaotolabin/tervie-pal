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