export interface FoodNutrient {
  nutrient_name: string;
  amount_per_100g: number;
  unit: string;
}

export interface FoodPortion {
  id: number;
  amount: number;
  unit: string;
  grams: number;
}

export interface FoodListItem {
  id: number;
  name: string;
  food_group?: string;
  is_custom: boolean;
  calories_100g: number;
}

export interface FoodDetail extends FoodListItem {
  portions: FoodPortion[];
  nutrients: FoodNutrient[];
}

export interface FoodSearchResponse {
  items: FoodListItem[];
  total: number;
}