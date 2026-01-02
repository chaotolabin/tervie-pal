"""
Database Adapter - Chuyển đổi backend format sang chatbot format
"""

from sqlalchemy.orm import Session
from app.models.food import Food


class DatabaseAdapter:
    """Chuyển đổi giữa backend và chatbot"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _to_chatbot_format(self, food: Food) -> dict:
     
        
        # Extract nutrients từ relationship
        nutrients = {}
        
        try:
            for nutrient in food.nutrients:
                # Key là nutrient_name: "protein", "fat", "carbs", "calories"
                key = nutrient.nutrient_name.lower()
                nutrients[key] = float(nutrient.amount_per_100g)
        except Exception as e:
            print(f"⚠️  Error parsing nutrients for food_id {food.id}: {e}")
        
        return {
            "id": food.id,
            "food_id": food.id,
            "name": food.name,
            "group": food.food_group or "Other",
            "calories": nutrients.get('calories', 0),
            
            "protein": nutrients.get('protein', 0),
            "fat": nutrients.get('fat', 0),
            "carbs": nutrients.get('carbs', 0),
        }