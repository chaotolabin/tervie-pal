"""
RAG Service - ENHANCED VERSION
Phân loại món ăn: Protein, Carbs, Vegetables
"""

import google.generativeai as genai
import chromadb
import random
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.settings import settings
from app.services.nutri_chatbot.database_adapter import DatabaseAdapter
from app.models.food import Food


class RAGService:
    """RAG Service với food category detection"""
    
    # Food category keywords
    PROTEIN_KEYWORDS = [
        'chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna', 'shrimp',
        'egg', 'tofu', 'turkey', 'duck', 'lamb', 'steak', 'meat',
        'gà', 'thịt', 'cá', 'tôm', 'trứng', 'đậu phụ'
    ]
    
    CARBS_KEYWORDS = [
        'rice', 'bread', 'pasta', 'noodles', 'potato', 'sweet potato',
        'oatmeal', 'cereal', 'quinoa', 'corn', 'wheat', 'bagel',
        'cơm', 'bánh mì', 'mì', 'khoai', 'bột', 'ngũ cốc'
    ]
    
    VEGGIE_KEYWORDS = [
        'salad', 'broccoli', 'spinach', 'kale', 'lettuce', 'tomato',
        'cucumber', 'carrot', 'cabbage', 'cauliflower', 'bell pepper',
        'vegetables', 'veggie', 'greens', 'asparagus', 'zucchini',
        'mushroom', 'onion', 'garlic', 'celery', 'eggplant',
        'rau', 'salad', 'súp lơ', 'cà rốt', 'cải', 'rau xào'
    ]
    
    # ✅ NEW: Blacklist - Món KHÔNG được chọn
    BLACKLIST_KEYWORDS = [
        'babyfood', 'baby food', 'infant', 'toddler', 'gerber',
        'formula', 'pediatric', 'junior', 'baby', 'strained',
        'trẻ em', 'bé', 'sữa bột'
    ]
    
    # ✅ NEW: False veggie - Không phải món rau thực sự
    FALSE_VEGGIE_KEYWORDS = [
        'dressing', 'sauce', 'mayo', 'mayonnaise', 'ketchup',
        'mustard', 'relish', 'gravy', 'butter', 'oil',
        'sốt', 'tương', 'dầu', 'Fast'
    ]
    
    def __init__(self, db: Session):
        self.db = db
        self.db_adapter = DatabaseAdapter(db)
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        self.foods_collection = self.chroma_client.get_collection("foods")
    
    def _generate_query_embedding(self, text: str):
        result = genai.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type="retrieval_query"
        )
        return result['embedding']
    
    def _detect_food_category(self, food_name: str) -> str:
        """
        Phát hiện category của món ăn
        
        Returns:
            'protein' | 'carbs' | 'veggie' | 'mixed' | 'snack'
        """
        name_lower = food_name.lower()
        
        # Check snack first (ưu tiên cao nhất cho snack)
        snack_indicators = ['chip', 'candy', 'cookie', 'brownie', 'cake', 
                           'ice cream', 'popcorn', 'pretzel', 'cracker', 
                           'chocolate', 'bar']
        if any(s in name_lower for s in snack_indicators):
            return 'snack'
        
        # Count matches
        protein_score = sum(1 for kw in self.PROTEIN_KEYWORDS if kw in name_lower)
        carbs_score = sum(1 for kw in self.CARBS_KEYWORDS if kw in name_lower)
        veggie_score = sum(1 for kw in self.VEGGIE_KEYWORDS if kw in name_lower)
        
        # Xác định category
        if protein_score > carbs_score and protein_score > veggie_score:
            return 'protein'
        elif carbs_score > protein_score and carbs_score > veggie_score:
            return 'carbs'
        elif veggie_score > protein_score and veggie_score > carbs_score:
            return 'veggie'
        elif protein_score > 0 or carbs_score > 0 or veggie_score > 0:
            return 'mixed'  # Món ăn kết hợp
        
        return 'mixed'
    
    def search_foods(self, query: str, top_k: int = 5, randomize: bool = True):
        """Tìm món ăn cơ bản (giữ nguyên)"""
        
        print(f"🔍 Searching: '{query}'")
        
        query_embedding = self._generate_query_embedding(query)
        search_k = top_k * 4 if randomize else top_k
        
        results = self.foods_collection.query(
            query_embeddings=[query_embedding],
            n_results=search_k
        )
        
        if not results['metadatas'] or len(results['metadatas']) == 0:
            return []
        
        food_ids = [m['food_id'] for m in results['metadatas'][0]]
        
        stmt = select(Food).where(
            Food.id.in_(food_ids),
            Food.deleted_at.is_(None)
        )
        db_foods = self.db.scalars(stmt).all()
        
        foods = []
        for metadata, distance in zip(results['metadatas'][0], results['distances'][0]):
            food_id = metadata['food_id']
            db_food = next((f for f in db_foods if f.id == food_id), None)
            if not db_food:
                continue
            
            food_dict = self.db_adapter._to_chatbot_format(db_food)
            food_dict['similarity'] = 1 - distance

            name_lower = food_dict['name'].lower()
            if any(kw in name_lower for kw in self.BLACKLIST_KEYWORDS):
                continue
            
            
            food_dict['category'] = self._detect_food_category(food_dict['name'])
            
            
            foods.append(food_dict)
        
        if randomize and len(foods) > top_k:
            best_threshold = max(top_k, int(len(foods) * 0.3))
            best_foods = foods[:best_threshold]
            random.shuffle(best_foods)
            return best_foods[:top_k]
        
        return foods[:top_k]
    
    def search_by_goal_and_calories(
        self,
        goal: str,
        target_calories: int,
        meal_type: str,
        food_category: str = None,  # ✅ NEW: 'protein' | 'carbs' | 'veggie'
        comparison: str = 'around',
        top_k: int = 10
    ):
        """
        ✅ ENHANCED: Tìm món theo goal + calories + meal_type + food_category
        
        Args:
            goal: 'lose_weight' | 'gain_muscle' | 'gain_weight' | 'maintain_weight'
            target_calories: Mức calo mục tiêu
            meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack'
            food_category: 'protein' | 'carbs' | 'veggie' (optional)
            comparison: 'under' | 'around' | 'above'
            top_k: Số món trả về
        """
        
        print(f"🍽️  Goal={goal}, Calo={target_calories}, Meal={meal_type}, Category={food_category}")
        
        # 1. Build query
        query = self._build_smart_query(goal, meal_type, target_calories, food_category)
        
        # 2. Search
        all_foods = self.search_foods(query, top_k=top_k * 10, randomize=False)
        
        if not all_foods:
            query_fallback = f"maintain_weight {meal_type} {food_category or 'meal'}"
            all_foods = self.search_foods(query_fallback, top_k=top_k * 10, randomize=False)
        
        # 3. Filter theo meal_type
        filtered_by_meal = self._filter_by_meal_type(all_foods, meal_type)
        
        # 4. ✅ NEW: Filter theo food_category (protein/carbs/veggie)
        if food_category:
            filtered_by_meal = self._filter_by_food_category(filtered_by_meal, food_category)
        
        # 5. Filter theo calories
        filtered_foods = self._filter_by_calories(filtered_by_meal, target_calories, comparison)
        
        # 6. Sort & Random
        filtered_foods = self._sort_and_randomize(filtered_foods, target_calories, comparison, top_k)
        
        print(f"✅ Found {len(filtered_foods)} foods")
        return filtered_foods
    
    def _build_smart_query(self, goal, meal_type, target_calories, food_category=None):
        """Build query với food_category - ENHANCED VERSION"""
        
        # Base query
        if goal == 'lose_weight':
            base = f"high protein low calorie"
        elif goal == 'gain_muscle':
            base = f"high protein"
        elif goal == 'gain_weight':
            base = f"high calorie nutritious"
        else:
            base = f"maintain_weight"
        
        # breakfast queries
        if meal_type == 'breakfast':
            base = "healthy breakfast eggs omelette scrambled pancake bacon yogurt"
        else:
            # Add meal type
            base += f" {meal_type}"
        
        # ✅ ENHANCED: Specific keywords cho từng category
        if food_category == 'protein':
            base += " grilled chicken breast beef fish salmon steak turkey meat"
        elif food_category == 'carbs':
            base += " rice white brown bread pasta noodles potato sweet potato quinoa"
        elif food_category == 'veggie':
            # ✅ CRITICAL: Chỉ tìm món rau THUẦN TÚY
            base += " fresh salad steamed vegetables roasted vegetables mixed greens garden salad"
        
        base += f" around {target_calories} calories"
        
        return base
    
    def _filter_by_meal_type(self, foods, meal_type):
        """Filter theo meal_type (breakfast/lunch/dinner/snack)"""
        
        MEAL_KEYWORDS = {
            'breakfast': {
                'include': ['egg', 'omelette', 'scrambled', 'milk', 'yogurt', 
                           'cereal', 'oatmeal', 'pancake', 'waffle', 'toast',
                           'bacon', 'sausage', 'fruit', 'breakfast', 'muffin',
                           'bagel', 'croissant', 'hash brown'],
                'exclude': ['lunch', 'dinner', 'pizza', 'burger', 'steak', 'ready-to-eat'],
                # ✅ Prefer: Món nấu > Món khô
                'prefer': ['egg', 'omelette', 'scrambled', 'pancake', 'waffle', 
                          'bacon', 'sausage', 'hash brown']
            },
            'lunch': {
                'include': ['sandwich', 'wrap', 'burger', 'salad', 'soup', 
                           'chicken', 'rice', 'noodles', 'pasta', 'lunch'],
                'exclude': ['breakfast', 'cereal', 'oatmeal', 'ready-to-eat']
            },
            'dinner': {
                'include': ['steak', 'roast', 'grilled', 'baked', 'chicken', 
                           'beef', 'fish', 'rice', 'potato', 'pasta', 'dinner'],
                'exclude': ['breakfast', 'cereal', 'ready-to-eat']
            },
            'snack': {
                'include': ['chips', 'crackers', 'cookie', 'candy', 'nuts', 
                           'fruit', 'yogurt', 'bar', 'snack'],
                'exclude': []
            }
        }
        
        if meal_type not in MEAL_KEYWORDS:
            return foods
        
        keywords = MEAL_KEYWORDS[meal_type]
        filtered = []
        preferred = []  # ✅ Món được ưu tiên
        
        for food in foods:
            name_lower = food.get('name', '').lower()
            
            # Check exclude
            if any(ex in name_lower for ex in keywords['exclude']):
                continue
            
            # Check include
            if any(inc in name_lower for inc in keywords['include']):
                # ✅ Check if preferred (for breakfast)
                if meal_type == 'breakfast' and 'prefer' in keywords:
                    if any(pref in name_lower for pref in keywords['prefer']):
                        preferred.append(food)
                    else:
                        filtered.append(food)
                else:
                    filtered.append(food)
        
        # ✅ Prioritize preferred items for breakfast
        if meal_type == 'breakfast' and preferred:
            print(f"✅ Found {len(preferred)} preferred breakfast items")
            return preferred + filtered  # Preferred first
        
        # Loại bỏ snacks cho lunch/dinner
        if meal_type in ['lunch', 'dinner']:
            snack_words = ['chip', 'candy', 'cookie', 'brownie', 'cake']
            filtered = [f for f in filtered 
                       if not any(sw in f.get('name', '').lower() for sw in snack_words)]
        
        return filtered if filtered else foods
    
    def _filter_by_food_category(self, foods, food_category):
        
        if not food_category:
            return foods
        
        filtered = []

        for food in foods:
            name_lower = food['name'].lower()
            detected_category = food.get('category', self._detect_food_category(food['name']))
            
            # ✅ STRICT FILTER cho veggie - KHÔNG cho phép mixed
            
            if food_category =='veggie':
                if detected_category != 'veggie':
                    continue
                if any(kw in name_lower for kw in self.FALSE_VEGGIE_KEYWORDS): 
                    continue

                filtered.append(food)



            # ✅ STRICT FILTER cho protein - Ưu tiên món protein thuần
            elif food_category == 'protein':
                if detected_category == 'protein':
                    filtered.append(food)
                elif detected_category == 'mixed' and len(filtered) < 3:
                    # Chỉ cho phép mixed nếu không đủ món protein thuần
                    filtered.append(food)
            
            # ✅ STRICT FILTER cho carbs
            elif food_category == 'carbs':
                if detected_category == 'carbs':
                    filtered.append(food)
                elif detected_category == 'mixed' and len(filtered) < 3:
                    filtered.append(food)
            
            else:
                # Other categories
                if detected_category == food_category or detected_category == 'mixed':
                    filtered.append(food)
        
        if not filtered:
            print(f"⚠️  No {food_category} foods found, returning all")
            return foods
        
        print(f"✅ Category filter: {len(foods)} → {len(filtered)} ({food_category})")
        return filtered
    
    def _filter_by_calories(self, foods, target_calories, comparison):
        """Filter theo calo với tolerance linh hoạt"""
        
        # ✅ Tăng tolerance cho món rau (thường ít calo)
        if target_calories < 150:
            tolerance = 150  # Rất linh hoạt cho món rau
        elif comparison == 'around':
            tolerance = 100
        else:
            tolerance = 50
        
        filtered = []
        
        for food in foods:
            cal = food['calories']
            if comparison == 'under' and cal <= target_calories + tolerance:
                filtered.append(food)
            elif comparison == 'above' and cal >= target_calories - tolerance:
                filtered.append(food)
            elif comparison == 'around' and abs(cal - target_calories) <= tolerance:
                filtered.append(food)
        
        return filtered if filtered else foods
    
    def _sort_and_randomize(self, foods, target_calories, comparison, top_k):
        """Sort và random"""
        
        if comparison == 'around':
            foods.sort(key=lambda x: abs(x['calories'] - target_calories))
        elif comparison == 'under':
            foods.sort(key=lambda x: x['calories'], reverse=True)
        else:
            foods.sort(key=lambda x: x['calories'])
        
        if len(foods) > top_k:
            best_count = max(top_k, min(20, int(len(foods) * 0.4)))
            best_foods = foods[:best_count]
            random.shuffle(best_foods)
            return best_foods[:top_k]
        
        return foods[:top_k]