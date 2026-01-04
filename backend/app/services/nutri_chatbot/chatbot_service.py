import google.generativeai as genai
from sqlalchemy.orm import Session
import json
import re

from app.core.settings import settings
from app.services.nutri_chatbot.intent_classifier import IntentClassifier
from app.services.nutri_chatbot.rag_service import RAGService
from app.services.nutri_chatbot.translate_service import TranslateService


class ChatbotService:
    """
    Chatbot chính - orchestrate toàn bộ logic
    
    ✅ BẮT BUỘC: Lấy thông tin từ database, KHÔNG tự sinh
    
    Workflow:
    1. Nhận message từ user
    2. Classify intent bằng IntentClassifier
    3. Route đến handler tương ứng
    4. Gọi RAG Service nếu cần
    5. Generate response bằng Gemini
    6. Trả về response
    """
    
    def __init__(self, db: Session, user_id=None):
        self.db = db
        self.user_id = user_id
        
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        self.intent_classifier = IntentClassifier()
        self.rag_service = RAGService(db)
    
    def chat(self, message):
        """
        Xử lý message từ user
        
        Args:
            message (str): Tin nhắn từ user
        
        Returns:
            dict: {
                "response": "Câu trả lời...",
                "intent": "FOOD_NUTRITION_INQUIRY",
                "data": [...] (kết quả RAG nếu có)
            }
        """
        
        print(f"\n📝 User: {message}")
        
        # Step 1: Classify intent
        intent_result = self.intent_classifier.classify(message)
        intent = intent_result['intent']
        entities = intent_result['entities']
        
        print(f"🎯 Intent: {intent}")
        print(f"📦 Entities: {entities}")
        
        # Step 2: Route to appropriate handler
        if intent == 'SOCIAL':
            return self._handle_social(message)
        
        elif intent == 'FOOD_NUTRITION_INQUIRY':
            return self._handle_food_nutrition_inquiry(message, entities)
        
        elif intent == 'CALORIE_BASED_RECOMMENDATION':
            return self._handle_calorie_based_recommendation(message, entities)
        
        elif intent == 'GOAL_BASED_RECOMMENDATION':
            return self._handle_goal_based_recommendation(message, entities)
        
        elif intent == 'MEAL_PLAN_REQUEST':
            return self._handle_meal_plan_request(message, entities)
        
        else:
            # Fallback
            return self._handle_social(message)
    
    # ========== HELPER METHODS ==========
    
    def _get_user_profile(self):
        """
        ✅ FIXED: Lấy FULL thông tin user từ database
        
        Lấy từ 4 bảng:
        - users: username, email
        - profiles: full_name, gender, date_of_birth, height_cm_default
        - goals: goal_type, daily_calorie_target, baseline_activity, weekly_goal, macros
        - biometrics_logs: weight_kg, bmi (record mới nhất) - QUERY TRỰC TIẾP
        
        Returns:
            dict: {
                'user_id': uuid,
                'username': str,
                'email': str,
                'full_name': str,
                'gender': str,
                'age': int,
                'height_cm': float,
                'weight_kg': float,
                'bmi': float,
                'goal_type': str,
                'daily_calorie_target': float,
                'baseline_activity': str,
                'weekly_goal': float,
                'protein_grams': float,
                'fat_grams': float,
                'carb_grams': float
            } hoặc None
        """
        if not self.user_id:
            return None
        
        try:
            from app.models.auth import User
            from app.models.biometrics import BiometricsLog  # ✅ FIX: Import model biometrics
            
            # Lấy user
            user = self.db.query(User).filter(User.id == self.user_id).first()
            if not user:
                return None
            
            # Lấy profile (dùng relationship - đã có sẵn trong User model)
            profile = None
            if hasattr(user, 'profile') and user.profile:
                profile = user.profile
            
            # Lấy goals (dùng relationship - đã có sẵn trong User model)
            goals = None
            if hasattr(user, 'goal') and user.goal:
                goals = user.goal
            
            # ✅ FIX: Query biometrics_logs trực tiếp từ database
            # KHÔNG dùng relationship vì User model không có biometrics_logs
            biometrics = (
                self.db.query(BiometricsLog)
                .filter(BiometricsLog.user_id == self.user_id)
                .order_by(BiometricsLog.logged_at.desc())
                .first()
            )
            
            # Tính tuổi từ date_of_birth
            age = None
            if profile and hasattr(profile, 'date_of_birth') and profile.date_of_birth:
                from datetime import date
                today = date.today()
                dob = profile.date_of_birth
                age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            
            # Build result dictionary
            return {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': profile.full_name if profile and hasattr(profile, 'full_name') else None,
                'gender': profile.gender if profile and hasattr(profile, 'gender') else None,
                'age': age,
                'height_cm': float(profile.height_cm_default) if profile and hasattr(profile, 'height_cm_default') and profile.height_cm_default else None,
                'weight_kg': float(biometrics.weight_kg) if biometrics and hasattr(biometrics, 'weight_kg') and biometrics.weight_kg else None,
                'bmi': float(biometrics.bmi) if biometrics and hasattr(biometrics, 'bmi') and biometrics.bmi else None,
                'goal_type': goals.goal_type if goals and hasattr(goals, 'goal_type') else None,
                'daily_calorie_target': float(goals.daily_calorie_target) if goals and hasattr(goals, 'daily_calorie_target') else None,
                'baseline_activity': goals.baseline_activity if goals and hasattr(goals, 'baseline_activity') else None,
                'weekly_goal': float(goals.weekly_goal) if goals and hasattr(goals, 'weekly_goal') and goals.weekly_goal else None,
                'protein_grams': float(goals.protein_grams) if goals and hasattr(goals, 'protein_grams') and goals.protein_grams else None,
                'fat_grams': float(goals.fat_grams) if goals and hasattr(goals, 'fat_grams') and goals.fat_grams else None,
                'carb_grams': float(goals.carb_grams) if goals and hasattr(goals, 'carb_grams') and goals.carb_grams else None,
            }
            
        except Exception as e:
            print(f"⚠️ Error getting user profile: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _goal_to_vietnamese(self, goal_type):
        """
        ✅ FIXED: Convert goal_type đúng với database
        
        Args:
            goal_type (str): 'lose_weight', 'gain_muscle', 'maintain_weight', 'gain_weight'
        
        Returns:
            str: Goal bằng tiếng Việt
        """
        mapping = {
            'lose_weight': 'giảm cân',
            'gain_muscle': 'tăng cơ',
            'gain_weight': 'tăng cân',
            'maintain_weight': 'duy trì cân nặng',
        }
        return mapping.get(goal_type, 'lành mạnh')
    
    def _format_foods(self, foods):
        """
        Helper: Format danh sách món ăn
        
        Args:
            foods (list): Danh sách food dictionaries
        
        Returns:
            str: Danh sách formatted
        """
        if not foods:
            return "(Không có món phù hợp)"
        
        result = ""
        for i, food in enumerate(foods, 1):
            result += f"{i}. {food['name']}: {food['calories']}cal, {food['protein']}g protein\n"
        return result.strip()
    
    def _format_foods_with_macros(self, foods):
        """
        ✅ NEW: Helper format foods với đầy đủ macros
        
        Args:
            foods (list): Danh sách food dictionaries
        
        Returns:
            str: Danh sách formatted với macros đầy đủ
        """
        if not foods:
            return "(Không có món phù hợp)"
        
        result = ""
        for i, food in enumerate(foods, 1):
            result += f"{i}. {food['name']}\n"
            result += f"   📊 {food['calories']}cal | {food['protein']}g protein | {food['carbs']}g carbs | {food['fat']}g fat\n\n"
        return result.strip()
    
    # ========== HANDLER: SOCIAL ==========
    
    def _handle_social(self, message):
        """
        Handler cho SOCIAL intent
        
        Xử lý: Chào hỏi, cảm ơn, tạm biệt, hỏi "bạn là ai?"
        
        Args:
            message (str): Tin nhắn từ user
        
        Returns:
            dict: Response với intent SOCIAL
        """
        
        prompt = f"""
Bạn là NutriBot - chatbot tư vấn dinh dưỡng thông minh, thân thiện và chuyên nghiệp.
Nhiệm vụ của bạn là phản hồi các câu giao tiếp xã hội của người dùng một cách tự nhiên và ấm áp.
Đầu ra mong muốn là một **câu trả lời ngắn gọn, thân thiện**, không chứa thông tin dinh dưỡng phức tạp.

**TIN NHẮN TỪ NGƯỜI DÙNG:**
"{message}"

**QUY TẮC TRẢ LỜI:**
1. Nhận diện loại tin nhắn:
   - Lời chào: "Chào bạn! Mình là NutriBot..."
   - Cảm ơn: "Không có gì! Luôn sẵn sàng..."
   - Tạm biệt: "Tạm biệt! Hẹn gặp lại..."
   - Hỏi về bot: Giới thiệu khả năng

2. Nguyên tắc văn phong:
   - Thân thiện, gần gũi như bạn bè
   - Sử dụng "mình" (bot) và "bạn" (user)
   - Có thể dùng emoji nhẹ (😊, 💚, 👋)
   - Ngắn gọn (1-2 câu)
   - KHÔNG dùng markdown (**, ##, -)

3. Những điều TUYỆT ĐỐI KHÔNG LÀM:
   - KHÔNG đưa ra thông tin dinh dưỡng cụ thể
   - KHÔNG gợi ý món ăn cụ thể
   - KHÔNG trả lời dài dòng

**BẮT ĐẦU TRẢ LỜI (chỉ câu trả lời, không giải thích):**
"""
        
        response = self.model.generate_content(prompt)
        
        return {
            "response": response.text.strip(),
            "intent": "SOCIAL",
            "data": []
        }
    
    # ========== HANDLER: FOOD_NUTRITION_INQUIRY ==========
    
    def _handle_food_nutrition_inquiry(self, message, entities):
        """
        Handler cho FOOD_NUTRITION_INQUIRY intent
        
        Xử lý: Hỏi thông tin dinh dưỡng món ăn cụ thể
        VD: "Trứng có bao nhiêu calo?", "Thịt gà có bao nhiêu protein?"
        
        Args:
            message (str): Tin nhắn từ user
            entities (dict): {
                'food_name': 'egg',
                'nutrient': 'calories'
            }
        
        Returns:
            dict: Response với danh sách món ăn tìm được
        """
        
        food_name = entities.get('food_name', '')
        nutrient = entities.get('nutrient', 'all')
        
        if not food_name:
            return {
                "response": "Xin gửi thông tin tới bạn nhé nhé! 😊",
                "intent": "FOOD_NUTRITION_INQUIRY",
                "data": []
            }
        
        # Search món ăn trong database qua RAG Service
        print(f"🔍 Searching: {food_name}")
        foods = self.rag_service.search_foods(food_name, top_k=5)
        
        if not foods:
            return {
                "response": f"Mình không tìm thấy thông tin về '{food_name}'. Bạn có thể thử tên khác hoặc mô tả rõ hơn nhé!",
                "intent": "FOOD_NUTRITION_INQUIRY",
                "data": []
            }
        
        # Build response - Liệt kê từng món tìm được
        response_text = f"Mình tìm thấy {len(foods)} món liên quan đến '{food_name}':\n\n"
        
        for i, food in enumerate(foods, 1):
            response_text += f"{i}. **{food['name']}**\n   "
            
            # Hiển thị chất dinh dưỡng theo yêu cầu
            if nutrient == 'calories':
                response_text += f" {food['calories']} kcal"
            elif nutrient == 'protein':
                response_text += f" {food['protein']}g protein"
            elif nutrient == 'carbs':
                response_text += f" {food['carbs']}g carbs"
            elif nutrient == 'fat':
                response_text += f" {food['fat']}g fat"
            else:  # all - hiển thị đầy đủ
                response_text += f" {food['calories']} kcal | "
                response_text += f" {food['protein']}g protein | "
                response_text += f" {food['carbs']}g carbs | "
                response_text += f" {food['fat']}g fat"
            
            response_text += "\n\n"
        
        response_text += "Xin gửi thông tin tới bạn nhé?"
        
        return {
            "response": response_text,
            "intent": "FOOD_NUTRITION_INQUIRY",
            "data": foods
        }
    
    # ========== HANDLER: CALORIE_BASED_RECOMMENDATION ==========
    
    def _handle_calorie_based_recommendation(self, message, entities):
        """
        ✅ ENHANCED: Hiển thị đầy đủ macros
        
        Handler cho CALORIE_BASED_RECOMMENDATION intent
        
        Xử lý: Gợi ý món ăn theo khoảng calo
        VD: "Gợi ý món dưới 300 calo", "Món ăn khoảng 500 calo"
        
        Args:
            message (str): Tin nhắn từ user
            entities (dict): {
                'target_calories': 300,
                'comparison': 'under' / 'around' / 'above'
            }
        
        Returns:
            dict: Response với danh sách món được gợi ý
        """
        
        target_calories = entities.get('target_calories', 300)
        comparison = entities.get('comparison', 'around')
        
        # Search món ăn theo calo
        foods = self.rag_service.search_by_calories(
            target_calories=target_calories,
            comparison=comparison,
            top_k=10
        )
        
        if not foods:
            return {
                "response": f"Mình không tìm được món phù hợp với {target_calories} calo. Bạn thử khoảng khác nhé!",
                "intent": "CALORIE_BASED_RECOMMENDATION",
                "data": []
            }
        
        # Build context cho Gemini - ENHANCED với đầy đủ macros
        comparison_text = {'under': 'dưới', 'around': 'khoảng', 'above': 'trên'}
        
        context = f"Các món {comparison_text[comparison]} {target_calories} calo:\n\n"
        for i, food in enumerate(foods[:8], 1):
            context += f"{i}. {food['name']}\n"
            context += f"   📊 {food['calories']}cal | {food['protein']}g protein | {food['carbs']}g carbs | {food['fat']}g fat\n\n"
        
        # Generate response bằng Gemini - ✅ PROMPT ENHANCED
        prompt = f"""
Bạn là chuyên gia dinh dưỡng. Gợi ý món ăn phù hợp.

YÊU CẦU: "{message}"
MỤC TIÊU: {comparison_text[comparison]} {target_calories} calo

CÁC MÓN KHẢ DỤNG:
{context}

QUY TẮC QUAN TRỌNG:
1. Chọn 3-4 món từ NHÓM KHÁC NHAU
2. ƯU TIÊN: Thịt, Cá, Trứng, Rau, Ngũ cốc
3. TRÁNH: KHÔNG chọn 2 món cùng là "Snacks"
4. Format BẮT BUỘC:

**1. [Tên món]**
📊 Calo: X kcal | Protein: Xg | Carbs: Xg | Fat: Xg
✅ Lý do phù hợp: [1 câu ngắn]

**2. [Tên món]**
📊 Calo: X kcal | Protein: Xg | Carbs: Xg | Fat: Xg
✅ Lý do phù hợp: [1 câu ngắn]

QUY TẮC:
- BẮT BUỘC hiển thị đầy đủ: Calo + Protein + Carbs + Fat
- Giải thích ngắn gọn tại sao phù hợp
- KHÔNG dài dòng

TRẢ LỜI:
"""
        
        response = self.model.generate_content(prompt)
        
        return {
            "response": response.text.strip(),
            "intent": "CALORIE_BASED_RECOMMENDATION",
            "data": foods
        }
    
    # ========== HANDLER: GOAL_BASED_RECOMMENDATION ==========
    
    def _handle_goal_based_recommendation(self, message, entities):
        """
        ✅ COMPLETELY REWRITTEN: Gợi ý theo CATEGORY, KHÔNG phải món cụ thể
        
        Handler cho GOAL_BASED_RECOMMENDATION intent
        
        Xử lý: Gợi ý NHÓM món ăn theo mục tiêu sức khỏe
        VD: "Tôi muốn giảm cân?", "Tôi muốn tăng cân, nên ăn gì?"
        
        Response format:
        - Giới thiệu nhóm protein: Gà, cá, trứng...
        - Giới thiệu nhóm carbs: Cơm, mì, khoai...
        - Giới thiệu nhóm rau: Salad, súp lơ, cải...
        
        Args:
            message (str): Tin nhắn từ user
            entities (dict): {
                'goal': 'lose_weight' / 'gain_muscle' / 'gain_weight' / 'maintain_weight'
            }
        
        Returns:
            dict: Response với danh sách món được gợi ý theo category
        """
        
        goal = entities.get('goal')
        
        # ✅ Nếu user không nói goal → Lấy từ database
        if not goal:
            user_profile = self._get_user_profile()
            if user_profile and user_profile.get('goal_type'):
                goal = user_profile['goal_type']
                print(f"✅ Using goal from database: {goal}")
            else:
                goal = 'maintain_weight'
        
        print(f"🎯 Goal-based recommendation for: {goal}")
        
        # ✅ Search theo 3 CATEGORY: Protein + Carbs + Veggie
        # Mỗi category search với calorie estimate phù hợp
        
        # 1. PROTEIN - Luôn quan trọng cho mọi goal
        protein_cal = 200 if goal == 'lose_weight' else 300
        protein_foods = self.rag_service.search_by_goal_and_calories(
            goal=goal,
            target_calories=protein_cal,
            meal_type='lunch',
            food_category='protein',
            comparison='around',
            top_k=8
        )
        
        # 2. CARBS - Điều chỉnh theo goal
        carbs_cal = 150 if goal == 'lose_weight' else 250
        carbs_foods = self.rag_service.search_by_goal_and_calories(
            goal=goal,
            target_calories=carbs_cal,
            meal_type='lunch',
            food_category='carbs',
            comparison='around',
            top_k=8
        )
        
        # 3. VEGGIE - Ít calo, nhiều chất xơ
        veggie_foods = self.rag_service.search_by_goal_and_calories(
            goal=goal,
            target_calories=80,
            meal_type='lunch',
            food_category='veggie',
            comparison='around',
            top_k=6
        )
        
        print(f"📊 Found: Protein={len(protein_foods)}, Carbs={len(carbs_foods)}, Veggie={len(veggie_foods)}")
        
        if not (protein_foods or carbs_foods or veggie_foods):
            return {
                "response": "Mình không tìm được món phù hợp. Bạn mô tả cụ thể hơn được không?",
                "intent": "GOAL_BASED_RECOMMENDATION",
                "data": []
            }
        
        goal_viet = self._goal_to_vietnamese(goal)
        
        # ✅ Build context với 3 CATEGORY riêng biệt
        context = f"""
**NHÓM 1: PROTEIN** (Thịt, Cá, Trứng - Xây dựng cơ bắp)
{self._format_foods_with_macros(protein_foods[:5])}

**NHÓM 2: CARBS** (Cơm, Mì, Khoai - Cung cấp năng lượng)
{self._format_foods_with_macros(carbs_foods[:5])}

**NHÓM 3: RAUCU** (Rau xanh, Salad - Vitamin & Chất xơ)
{self._format_foods_with_macros(veggie_foods[:4])}
"""
        
        # ✅ NEW PROMPT: Gợi ý theo CATEGORY, KHÔNG gợi ý món cụ thể
        prompt = f"""
Bạn là chuyên gia dinh dưỡng. Tư vấn NHÓM món ăn phù hợp với mục tiêu.

YÊU CẦU: "{message}"
MỤC TIÊU: {goal_viet}

CÁC NHÓM MÓN ĂN:
{context}

QUY TẮC BẮT BUỘC:
1. Giới thiệu 3 NHÓM món ăn (Protein, Carbs, Rau)
2. MỖI NHÓM:
   - Giải thích TẠI SAO quan trọng với {goal_viet}
   - Liệt kê 3-5 món TIÊU BIỂU với đầy đủ macros
   - 1 câu khuyên cách ăn

3. Format BẮT BUỘC:

💪 **NHÓM PROTEIN** (Xây dựng cơ bắp, no lâu)
Để {goal_viet}, bạn nên tập trung vào protein vì [lý do ngắn].

Một số món gợi ý:
• **[Tên món]** - X kcal | Xg protein | Xg carbs | Xg fat
• **[Tên món]** - X kcal | Xg protein | Xg carbs | Xg fat
• **[Tên món]** - X kcal | Xg protein | Xg carbs | Xg fat

💡 Lưu ý: [1 câu khuyên]

🍚 **NHÓM CARBS** (Năng lượng cho hoạt động)
[Giải thích tại sao quan trọng với {goal_viet}]

Một số món gợi ý:
• **[Tên món]** - X kcal | Xg protein | Xg carbs | Xg fat
• **[Tên món]** - X kcal | Xg protein | Xg carbs | Xg fat

💡 Lưu ý: [1 câu khuyên]

🥗 **NHÓM RAU CỦ** (Vitamin, chất xơ, ít calo)
[Giải thích tại sao quan trọng với {goal_viet}]

Một số món gợi ý:
• **[Tên món]** - X kcal | Xg protein | Xg carbs | Xg fat
• **[Tên món]** - X kcal | Xg protein | Xg carbs | Xg fat

💡 Lưu ý: [1 câu khuyên]

QUY TẮC:
- BẮT BUỘC hiển thị đầy đủ: Calo + Protein + Carbs + Fat
- Giải thích TẠI SAO nhóm này quan trọng với {goal_viet}
- Ngắn gọn, dễ hiểu
- CHỈ CHỌN TỪ DANH SÁCH ĐÃ CHO

TRẢ LỜI:
"""
        
        response = self.model.generate_content(prompt)
        
        return {
            "response": response.text.strip(),
            "intent": "GOAL_BASED_RECOMMENDATION",
            "data": {
                "protein": protein_foods[:5],
                "carbs": carbs_foods[:5],
                "veggie": veggie_foods[:4]
            }
        }
    
    # ========== HANDLER: MEAL_PLAN_REQUEST ==========
    
    def _handle_meal_plan_request(self, message, entities):
        """
        ✅ FIXED: BẮT BUỘC dùng database hoặc user input - KHÔNG tự bịa
        
        Handler cho MEAL_PLAN_REQUEST intent
        
        Xử lý: Tạo thực đơn cho cả ngày
        VD: "Tạo thực đơn 2000 calo để giảm cân"
        
        LUỒNG MỚI (BẮT BUỘC):
        1. Parse message → lấy goal_type + calorie_target
        2. Lấy user_profile từ database
        3. CÓ 2 CASE DUY NHẤT:
           a) User nói số calo cụ thể → Dùng số đó
           b) Lấy từ database (daily_calorie_target)
        4. KHÔNG CÒN CASE TỰ BỊA hoặc HỎI USER
        
        Args:
            message (str): Tin nhắn từ user
            entities (dict): {
                'goal': 'lose_weight' / etc.,
                (optional) 'calorie_target': 2000
            }
        
        Returns:
            dict: Response với thực đơn hoặc thông báo lỗi
        """
        
        # Step 1: Parse message để lấy goal_type và calorie_target
        analysis_prompt = f"""
Phân tích yêu cầu thực đơn và trích xuất thông tin.

YÊU CẦU: "{message}"

Trả về JSON (không có markdown):
{{
    "goal_type": "lose_weight|gain_muscle|maintain_weight|gain_weight|null",
    "calorie_target": <số_calo_hoặc_null>
}}

MAPPING MỤC TIÊU:
- "giảm cân" → "lose_weight"
- "tăng cơ" → "gain_muscle"
- "tăng cân" → "gain_weight"
- "duy trì" / "maintain" → "maintain_weight"

QUY TẮC:
- Nếu user KHÔNG nói rõ số calo → calorie_target: null
- Nếu user NÓI số calo cụ thể (VD: 1500, 2000) → calorie_target: <số>
- Nếu user không nói mục tiêu → goal_type: null

CHỈ TRẢ JSON, KHÔNG GIẢI THÍCH:
"""
        
        try:
            analysis = self.model.generate_content(analysis_prompt)
            analysis_text = analysis.text.strip()
            # Remove markdown if present
            analysis_text = re.sub(r'```json|```', '', analysis_text).strip()
            result = json.loads(analysis_text)
            print(f"📊 Analysis result: {result}")
        except Exception as e:
            print(f"⚠️ Analysis error: {e}")
            result = {"goal_type": None, "calorie_target": None}
        
        goal_type = result.get('goal_type')
        calorie_target = result.get('calorie_target')
        
        # Step 2: Lấy user profile từ database
        user_profile = self._get_user_profile()
        
        # ============ CASE 1: User nói số calo cụ thể → Ưu tiên số đó ============
        if calorie_target:
            # Lấy goal từ user hoặc database
            final_goal = goal_type or (user_profile.get('goal_type') if user_profile else 'maintain_weight')
            
            print(f"✅ User specified calories: {calorie_target}, goal: {final_goal}")
            
            return self._create_full_day_meal(final_goal, calorie_target, message)
        
        # ============ CASE 2: Dùng database (BẮT BUỘC) ============
        if user_profile and user_profile.get('daily_calorie_target'):
            db_goal_type = user_profile.get('goal_type', 'maintain_weight')
            db_calorie_target = user_profile['daily_calorie_target']
            
            # Nếu user nói goal mới → Dùng goal mới
            # Nếu không → Dùng goal từ database
            final_goal = goal_type if goal_type else db_goal_type
            final_calorie = int(db_calorie_target)
            
            print(f"✅ Using database: Goal={final_goal}, Calories={final_calorie}")
            
            # Tạo thực đơn
            result = self._create_full_day_meal(final_goal, final_calorie, message)
            
            # Thêm prefix giải thích
            goal_viet = self._goal_to_vietnamese(final_goal)
            prefix = f"""✅ **Dựa trên mục tiêu của bạn:**
- Mục tiêu: {goal_viet}
- Nên ăn: **{final_calorie} calo/ngày**

---

"""
            result['response'] = prefix + result['response']
            return result
        
        # ============ CASE 3: KHÔNG CÓ THÔNG TIN → BẮT BUỘC USER SETUP TRƯỚC ============
        return {
            "response": """❌ **Chưa thể tạo thực đơn**

Mình cần bạn hoàn thành **Profile** và **Goal** trong app trước khi tạo thực đơn nhé!

📋 **Cần làm gì?**
1. Vào phần **Profile** → Điền chiều cao, cân nặng, tuổi
2. Vào phần **Goal** → Chọn mục tiêu (giảm cân, tăng cơ...)

Sau đó bạn quay lại đây, mình sẽ tạo thực đơn phù hợp ngay! 💪

💡 **Hoặc** bạn có thể nói rõ số calo:
📝 Ví dụ: "Tạo thực đơn 1500 calo để giảm cân"
""",
            "intent": "MEAL_PLAN_REQUEST",
            "data": [],
            "needs_setup": True  # ✅ Flag để frontend biết cần setup
        }
    
    def _create_full_day_meal(self, goal, total_calories, message):
        """
        ✅ ENHANCED: Tạo thực đơn 4 bữa - CHỈ SỬA PROMPT (in thêm macros)
        
        Cấu trúc:
        - SÁNG (25%): 1-2 món
        - TRƯA (35%): 3 món (1 protein + 1 carbs + 1 rau)
        - SNACK (10%): 1 món
        - TỐI (30%): 3 món (1 protein + 1 carbs + 1 rau)
        
        Args:
            goal (str): Mục tiêu sức khỏe ('lose_weight', 'gain_muscle', etc.)
            total_calories (int): Tổng calo trong ngày
            message (str): Tin nhắn gốc từ user
        
        Returns:
            dict: Response với thực đơn đầy đủ
        """
        
        # Phân bổ calo cho từng bữa
        breakfast_cal = int(total_calories * 0.25)  # 25%
        lunch_cal = int(total_calories * 0.35)      # 35%
        snack_cal = int(total_calories * 0.10)      # 10%
        dinner_cal = int(total_calories * 0.30)     # 30%
        
        print(f"📊 Calorie distribution:")
        print(f"   Sáng: {breakfast_cal} cal (25%) - 1-2 món")
        print(f"   Trưa: {lunch_cal} cal (35%) - 3 món (protein + carbs + rau)")
        print(f"   Snack: {snack_cal} cal (10%) - 1 món")
        print(f"   Tối: {dinner_cal} cal (30%) - 3 món (protein + carbs + rau)")
        
        # ===== BỮA SÁNG: 1-2 món =====
        breakfast_foods = self.rag_service.search_by_goal_and_calories(
            goal=goal or 'maintain_weight',
            target_calories=breakfast_cal,
            meal_type='breakfast',
            comparison='around',
            top_k=10
        )
        
        # ===== BỮA TRƯA: 3 món (Protein + Carbs + Rau) =====
        # 45% protein, 35% carbs, 20% veggie 
        lunch_protein_cal = int(lunch_cal * 0.45)
        lunch_carbs_cal = int(lunch_cal * 0.35)
        lunch_veggie_cal = int(lunch_cal * 0.20)
        
        lunch_protein = self.rag_service.search_by_goal_and_calories(
            goal=goal or 'maintain_weight',
            target_calories=lunch_protein_cal,
            meal_type='lunch',
            food_category='protein',  
            comparison='around',
            top_k=8
        )
        
        lunch_carbs = self.rag_service.search_by_goal_and_calories(
            goal=goal or 'maintain_weight',
            target_calories=lunch_carbs_cal,
            meal_type='lunch',
            food_category='carbs',    
            comparison='around',
            top_k=8
        )
        
        lunch_veggie = self.rag_service.search_by_goal_and_calories(
            goal=goal or 'maintain_weight',
            target_calories=lunch_veggie_cal,
            meal_type='lunch',
            food_category='veggie',  
            comparison='around',
            top_k=8
        )
        
        # ===== SNACK: 1 món =====
        snack_foods = self.rag_service.search_by_goal_and_calories(
            goal=goal or 'maintain_weight',
            target_calories=snack_cal,
            meal_type='snack',
            comparison='around',
            top_k=10
        )
        
        # ===== BỮA TỐI: 3 món (Protein + Carbs + Rau) =====
        dinner_protein_cal = int(dinner_cal * 0.45)
        dinner_carbs_cal = int(dinner_cal * 0.35)
        dinner_veggie_cal = int(dinner_cal * 0.20)
        
        dinner_protein = self.rag_service.search_by_goal_and_calories(
            goal=goal or 'maintain_weight',
            target_calories=dinner_protein_cal,
            meal_type='dinner',
            food_category='protein',  
            comparison='around',
            top_k=8
        )
        
        dinner_carbs = self.rag_service.search_by_goal_and_calories(
            goal=goal or 'maintain_weight',
            target_calories=dinner_carbs_cal,
            meal_type='dinner',
            food_category='carbs',   
            comparison='around',
            top_k=8
        )
        
        dinner_veggie = self.rag_service.search_by_goal_and_calories(
            goal=goal or 'maintain_weight',
            target_calories=dinner_veggie_cal,
            meal_type='dinner',
            food_category='veggie',   
            comparison='around',
            top_k=8
        )
        
        print(f"📊 Search results:")
        print(f"   Breakfast: {len(breakfast_foods)} items")
        print(f"   Lunch: Protein={len(lunch_protein)}, Carbs={len(lunch_carbs)}, Veggie={len(lunch_veggie)}")
        print(f"   Snack: {len(snack_foods)} items")
        print(f"   Dinner: Protein={len(dinner_protein)}, Carbs={len(dinner_carbs)}, Veggie={len(dinner_veggie)}")
        
        if not (breakfast_foods and lunch_protein and dinner_protein):
            return {
                "response": "Mình không thể tạo thực đơn được. Bạn thử lại với mức calo khác nhé!",
                "intent": "MEAL_PLAN_REQUEST",
                "data": []
            }
        
        # ✅ Build context với đầy đủ macros
        context = f"""
🌅 MÓN SÁNG (~{breakfast_cal} calo - CHỌN 1-2 MÓN):
{self._format_foods_with_macros(breakfast_foods[:8])}

🍽️ BỮA TRƯA (~{lunch_cal} calo - CHỌN 3 MÓN):

**1. MÓN PROTEIN (~{lunch_protein_cal} cal - CHỌN 1):**
{self._format_foods_with_macros(lunch_protein[:5])}

**2. MÓN CARBS/TINH BỘT (~{lunch_carbs_cal} cal - CHỌN 1):**
{self._format_foods_with_macros(lunch_carbs[:5])}

**3. MÓN RAU (~{lunch_veggie_cal} cal - CHỌN 1):**
{self._format_foods_with_macros(lunch_veggie[:5])}

🍎 SNACK (~{snack_cal} calo - CHỌN 1 MÓN):
{self._format_foods_with_macros(snack_foods[:8])}

🌙 BỮA TỐI (~{dinner_cal} calo - CHỌN 3 MÓN):

**1. MÓN PROTEIN (~{dinner_protein_cal} cal - CHỌN 1):**
{self._format_foods_with_macros(dinner_protein[:5])}

**2. MÓN CARBS/TINH BỘT (~{dinner_carbs_cal} cal - CHỌN 1):**
{self._format_foods_with_macros(dinner_carbs[:5])}

**3. MÓN RAU (~{dinner_veggie_cal} cal - CHỌN 1):**
{self._format_foods_with_macros(dinner_veggie[:5])}
"""
        
        goal_viet = self._goal_to_vietnamese(goal) if goal else 'lành mạnh'
        
        # ✅ ENHANCED PROMPT: Hiển thị đầy đủ macros
        prompt = f"""
Bạn là chuyên gia dinh dưỡng chuyên nghiệp. Tạo thực đơn cả ngày.

YÊU CẦU: "{message}"
MỤC TIÊU: {goal_viet}
TỔNG CALO: {total_calories} calo

CÁC MÓN GỢI Ý:
{context}

QUY TẮC BẮT BUỘC:
1. **BỮA SÁNG:** Chọn 1-2 món từ danh sách Sáng
2. **BỮA TRƯA:** Chọn ĐÚNG 3 món:
   - 1 món PROTEIN (từ danh sách Protein)
   - 1 món CARBS/TINH BỘT (từ danh sách Carbs)
   - 1 món RAU (từ danh sách Rau)
3. **SNACK:** Chọn 1 món từ danh sách Snack
4. **BỮA TỐI:** Chọn ĐÚNG 3 món:
   - 1 món PROTEIN (từ danh sách Protein)
   - 1 món CARBS/TINH BỘT (từ danh sách Carbs)
   - 1 món RAU (từ danh sách Rau)
5. CHỈ CHỌN TỪ DANH SÁCH ĐÃ CHO
6. Format BẮT BUỘC (có đầy đủ macros):

🌅 **BỮA SÁNG** (~{breakfast_cal} cal)
**[Tên món]**
📊 X kcal | Xg protein | Xg carbs | Xg fat
✅ Lý do ngắn gọn (1 câu).

🍽️ **BỮA TRƯA** (~{lunch_cal} cal)
1. **PROTEIN: [Tên món]**
   📊 X kcal | Xg protein | Xg carbs | Xg fat
   ✅ Lý do ngắn.
   
2. **CARBS: [Tên món]**
   📊 X kcal | Xg protein | Xg carbs | Xg fat
   ✅ Lý do ngắn.
   
3. **RAU: [Tên món]**
   📊 X kcal | Xg protein | Xg carbs | Xg fat
   ✅ Lý do ngắn.

🍎 **SNACK** (~{snack_cal} cal)
**[Tên món]**
📊 X kcal | Xg protein | Xg carbs | Xg fat
✅ Lý do ngắn.

🌙 **BỮA TỐI** (~{dinner_cal} cal)
1. **PROTEIN: [Tên món]**
   📊 X kcal | Xg protein | Xg carbs | Xg fat
   ✅ Lý do ngắn.
   
2. **CARBS: [Tên món]**
   📊 X kcal | Xg protein | Xg carbs | Xg fat
   ✅ Lý do ngắn.
   
3. **RAU: [Tên món]**
   📊 X kcal | Xg protein | Xg carbs | Xg fat
   ✅ Lý do ngắn.

📊 **TỔNG CỘNG:** ~{total_calories} cal | [Tổng protein]g protein | [Tổng carbs]g carbs | [Tổng fat]g fat

QUY TẮC:
- BẮT BUỘC hiển thị: Calo + Protein + Carbs + Fat cho MỖI món
- Tính TỔNG CỘNG cuối cùng (tổng các macros)
- Giải thích ngắn gọn tại sao phù hợp
- KHÔNG dài dòng

TRẢ LỜI:
"""
        
        response = self.model.generate_content(prompt)
        
        return {
            "response": response.text.strip(),
            "intent": "MEAL_PLAN_REQUEST",
            "data": {
                "breakfast": breakfast_foods[:8],
                "lunch": {
                    "protein": lunch_protein[:5],
                    "carbs": lunch_carbs[:5],
                    "veggie": lunch_veggie[:5]
                },
                "snack": snack_foods[:8] if snack_foods else [],
                "dinner": {
                    "protein": dinner_protein[:5],
                    "carbs": dinner_carbs[:5],
                    "veggie": dinner_veggie[:5]
                }
            }
        }