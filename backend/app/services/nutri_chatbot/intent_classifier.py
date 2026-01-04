import google.generativeai as genai
import json
import re

from app.core.settings import settings
from app.services.nutri_chatbot.translate_service import TranslateService


class IntentClassifier:
    """
    Phân loại ý định của user thành 5 loại:
    1. SOCIAL: Chào hỏi, cảm ơn
    2. FOOD_NUTRITION_INQUIRY: Hỏi thông tin món ăn cụ thể
    3. CALORIE_BASED_RECOMMENDATION: Gợi ý theo khoảng calo
    4. GOAL_BASED_RECOMMENDATION: Gợi ý theo mục tiêu (giảm cân, tăng cơ...)
    5. MEAL_PLAN_REQUEST: Yêu cầu thực đơn cho ngày/tuần
    """
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.5-flash')  
        self.translator = TranslateService()  # dịch message trước khi classify
    
    def classify(self, message):
        """
        Phân loại intent và trích xuất entities
        
        Args:
            message (str): Tin nhắn từ user (tiếng Việt hoặc tiếng Anh)
        
        Returns:
            dict: {
                "intent": "FOOD_NUTRITION_INQUIRY",
                "entities": {
                    "food_name": "egg",  # ✅ LUÔN LÀ ENGLISH
                    "nutrient": "calories"
                }
            }
        """
        
        # ✅ DỊCH NGAY TỪ ĐẦU - Đây là thay đổi quan trọng nhất
        english_message = self.translator.translate_to_english(message)
        
        if english_message != message:
            print(f"🌏 Translated for intent: '{message}' → '{english_message}'")
        
        prompt = f"""
Bạn là một chuyên gia phân loại ý định (intent classification) trong hệ thống chatbot dinh dưỡng thông minh.
Nhiệm vụ của bạn là phân tích câu hỏi/yêu cầu của người dùng, xác định chính xác ý định và trích xuất các thông tin quan trọng (entities).
Đầu ra mong muốn là một **object JSON hợp lệ**, không chứa giải thích hoặc text nào khác.


**I. ĐỊNH NGHĨA CÁC INTENT (5 LOẠI):**


1. **SOCIAL** - Tương tác xã hội
   - **Định nghĩa:** Các câu giao tiếp cơ bản, không liên quan đến dinh dưỡng
   - **Đặc điểm nhận dạng:**
     * Lời chào: "xin chào", "hello", "hi", "chào bạn", "hey"
     * Cảm ơn: "cảm ơn", "thanks", "thank you", "cảm ơn bạn"
     * Tạm biệt: "tạm biệt", "bye", "goodbye", "hẹn gặp lại"
     * Hỏi thăm: "bạn là ai?", "bạn tên gì?", "bạn khỏe không?"
     * Khen ngợi/phàn nàn về bot: "bạn giỏi quá", "bạn dở quá"
   - **Entities:** {{}} (luôn trống)
   - **Ví dụ:**
     * Input: "Hello"
       Output: {{"intent": "SOCIAL", "entities": {{}}}}
     * Input: "Thank you"
       Output: {{"intent": "SOCIAL", "entities": {{}}}}


2. **FOOD_NUTRITION_INQUIRY** - Hỏi thông tin dinh dưỡng của món ăn cụ thể
   - **Định nghĩa:** Câu hỏi về thông tin dinh dưỡng của MỘT món ăn CỤ THỂ
   - **Đặc điểm nhận dạng:**
     * Có tên món ăn cụ thể: "egg", "rice", "pho", "bread", "chicken"
     * Hỏi về thông tin: "how many", "how much", "nutrition info", "nutritional value"
     * Hỏi về chất dinh dưỡng: "calories", "protein", "carbs", "fat"
   - **Entities:**
     * `food_name` (string, BẮT BUỘC): Tên món ăn được hỏi (PHẢI LÀ ENGLISH)
       - Chuẩn hóa: viết thường
       - VD: "Egg" → "egg", "Chicken Breast" → "chicken breast"
     * `nutrient` (string, TÙY CHỌN): Chất dinh dưỡng cụ thể
       - Các giá trị hợp lệ: "calories", "protein", "carbs", "fat"
       - Nếu không nói rõ → null hoặc không có field này
   - **Ví dụ:**
     * Input: "How many calories in egg?"
       Output: {{"intent": "FOOD_NUTRITION_INQUIRY", "entities": {{"food_name": "egg", "nutrient": "calories"}}}}
     * Input: "Tell me nutrition info for beef pho"
       Output: {{"intent": "FOOD_NUTRITION_INQUIRY", "entities": {{"food_name": "beef pho"}}}}
     * Input: "Does bread have protein?"
       Output: {{"intent": "FOOD_NUTRITION_INQUIRY", "entities": {{"food_name": "bread", "nutrient": "protein"}}}}


3. **CALORIE_BASED_RECOMMENDATION** - Gợi ý món ăn theo khoảng calo
   - **Định nghĩa:** Yêu cầu gợi ý món ăn dựa trên MỨC CALO cụ thể
   - **Đặc điểm nhận dạng:**
     * Có từ khóa gợi ý: "suggest", "recommend", "give me", "find foods"
     * Có đề cập đến calo: "calories", "kcal", "cal"
     * Có mức độ: "under", "above", "around", "low", "high", "moderate"
   - **Entities:**
     * `target_calories` (number, BẮT BUỘC): Mức calo mục tiêu
       - Phải là số nguyên dương
       - Nếu không nói rõ số → áp dụng quy tắc mặc định (xem phần II.2)
     * `comparison` (string, BẮT BUỘC): Cách so sánh
       - "under": dưới/thấp hơn mức calo
       - "around": khoảng/tầm mức calo
       - "above": trên/cao hơn mức calo
   - **Ví dụ:**
     * Input: "Suggest foods under 300 calories"
       Output: {{"intent": "CALORIE_BASED_RECOMMENDATION", "entities": {{"target_calories": 300, "comparison": "under"}}}}
     * Input: "Find foods around 500 kcal"
       Output: {{"intent": "CALORIE_BASED_RECOMMENDATION", "entities": {{"target_calories": 500, "comparison": "around"}}}}
     * Input: "Low calorie foods" (mơ hồ)
       Output: {{"intent": "CALORIE_BASED_RECOMMENDATION", "entities": {{"target_calories": 200, "comparison": "under"}}}}


4. **GOAL_BASED_RECOMMENDATION** - Gợi ý món ăn theo mục tiêu sức khỏe
   - **Định nghĩa:** Yêu cầu gợi ý món ăn dựa trên MỤC TIÊU sức khỏe/thể hình
   - **Đặc điểm nhận dạng:**
     * Có từ khóa gợi ý: "suggest", "recommend", "what should I eat", "foods for"
     * Có mục tiêu: "weight loss", "muscle gain", "weight gain", "maintain_weight", "diet"
     * Có ngữ cảnh: "for...", "to...", "help..."
   - **Entities:**
     * `goal` (string, BẮT BUỘC): Mục tiêu sức khỏe
       - "lose_weight": weight loss, lose weight, diet, fat loss
       - "gain_muscle": muscle gain, bodybuilding, gym, build muscle
       - "gain_weight": weight gain, gain weight, bulk up
       - "maintain_weight": healthy, balanced, nutritious, wellness
   - **Ví dụ:**
     * Input: "What should I eat for weight loss?"
       Output: {{"intent": "GOAL_BASED_RECOMMENDATION", "entities": {{"goal": "lose_weight"}}}}
     * Input: "Suggest foods for gym people"
       Output: {{"intent": "GOAL_BASED_RECOMMENDATION", "entities": {{"goal": "gain_muscle"}}}}
     * Input: "Suggest foods" (mơ hồ)
       Output: {{"intent": "GOAL_BASED_RECOMMENDATION", "entities": {{"goal": "maintain_weight"}}}}


5. **MEAL_PLAN_REQUEST** - Yêu cầu thực đơn cho ngày/tuần
   - **Định nghĩa:** Yêu cầu lập thực đơn hoàn chỉnh cho nhiều bữa ăn
   - **Đặc điểm nhận dạng:**
     * Có từ khóa: "meal plan", "menu", "eating plan", "diet plan"
     * Đề cập nhiều bữa: "breakfast lunch dinner", "3 meals", "daily menu"
     * Ngữ cảnh thời gian: "today", "this week", "daily"
   - **Entities:**
     * `duration` (string, TÙY CHỌN): Thời gian
       - "daily": hôm nay, ngày, daily
       - "weekly": tuần, week, weekly
     * `goal` (string, TÙY CHỌN): Mục tiêu (nếu có)
       - "lose_weight", "gain_muscle", "gain_weight", "maintain_weight"
   - **Ví dụ:**
     * Input: "Suggest a meal plan for today"
       Output: {{"intent": "MEAL_PLAN_REQUEST", "entities": {{"duration": "daily"}}}}
     * Input: "Give me a menu for muscle building"
       Output: {{"intent": "MEAL_PLAN_REQUEST", "entities": {{"duration": "daily", "goal": "gain_muscle"}}}}
     * Input: "What should I eat for breakfast lunch and dinner?"
       Output: {{"intent": "MEAL_PLAN_REQUEST", "entities": {{"duration": "daily"}}}}


**II. QUY TẮC XỬ LÝ ĐẶC BIỆT:**


1. **Xử lý câu hỏi mơ hồ:**
   - Nếu người dùng chỉ nói "suggest foods" mà không nói rõ mục tiêu hoặc calo:
     → Phân loại là GOAL_BASED_RECOMMENDATION với goal: "maintain_weight"
   
   - Nếu hỏi "what's good?", "what to eat now?", "any good food?":
     → Phân loại là GOAL_BASED_RECOMMENDATION với goal: "maintain_weight"
   
   - Nếu hỏi "what's good for health?", "healthy food?":
     → Phân loại là GOAL_BASED_RECOMMENDATION với goal: "maintain_weight"


2. **Xử lý định lượng không rõ ràng:**
   Khi người dùng nói "low calorie", "high calorie", "moderate" mà không nói số cụ thể:
   
   - "Low calorie", "low cal", "diet food":
     → target_calories: 200, comparison: "under"
   
   - "Moderate calorie", "medium cal", "moderate":
     → target_calories: 400, comparison: "around"
   
   - "High calorie", "high cal", "calorie dense":
     → target_calories: 600, comparison: "above"


3. **Xử lý mục tiêu không rõ ràng:**
   - "What's good?", "good food", "healthy food":
     → goal: "maintain_weight"
   
   - "What to eat to be healthy?", "boost immunity":
     → goal: "maintain_weight"
   
   - "What to eat to lose weight?", "lose fat":
     → goal: "lose_weight"


4. **Ưu tiên xử lý:**
   Nếu một câu có CẢ calo VÀ mục tiêu:
   - Ưu tiên CALORIE_BASED_RECOMMENDATION nếu calo được nhắc đến CỤ THỂ
   - VD: "Suggest foods under 300 calories for weight loss"
     → CALORIE_BASED_RECOMMENDATION (vì có số calo cụ thể)


5. **Phân biệt MEAL_PLAN vs RECOMMENDATION:**
   - Nếu đề cập "meal plan", "menu", "breakfast lunch dinner" → MEAL_PLAN_REQUEST
   - Nếu chỉ hỏi "what to eat" mà không đề cập thực đơn → GOAL_BASED_RECOMMENDATION


6. **Xử lý nhiễu:**
   - Bỏ qua các từ không mang ý nghĩa: "please", "can you", "I want"
   - Bỏ qua emoji, biểu tượng cảm xúc
   - Chuẩn hóa về chữ thường khi xử lý


**III. ĐỊNH DẠNG ĐẦU VÀO:**


Bạn sẽ nhận được một câu văn từ người dùng. Câu văn có thể:
- Chứa lỗi chính tả, ngữ pháp
- Có từ viết tắt, từ lóng
- Có emoji, biểu tượng
- Mơ hồ, không rõ ràng


**IV. ĐỊNH DẠNG ĐẦU RA:**


Kết quả phải là một object JSON hợp lệ với cấu trúc:
```json
{{
  "intent": "<TÊN_INTENT>",
  "entities": {{
    "<key>": "<value>",
    ...
  }}
}}
```

**QUAN TRỌNG:**
- CHỈ trả về JSON, KHÔNG có bất kỳ text, giải thích, markdown nào khác
- KHÔNG thêm ```json hoặc ``` vào đầu/cuối
- KHÔNG giải thích lý do phân loại
- KHÔNG thêm bất kỳ comment nào
- Đảm bảo JSON hợp lệ 100%
- Tất cả entities phải là TIẾNG ANH


**V. VÍ DỤ CHI TIẾT:**


Input: "Hello"
Output: {{"intent": "SOCIAL", "entities": {{}}}}

Input: "Thank you so much!"
Output: {{"intent": "SOCIAL", "entities": {{}}}}

Input: "How many calories in egg?"
Output: {{"intent": "FOOD_NUTRITION_INQUIRY", "entities": {{"food_name": "egg", "nutrient": "calories"}}}}

Input: "Tell me nutrition info for beef pho"
Output: {{"intent": "FOOD_NUTRITION_INQUIRY", "entities": {{"food_name": "beef pho"}}}}

Input: "Does fried rice have protein?"
Output: {{"intent": "FOOD_NUTRITION_INQUIRY", "entities": {{"food_name": "fried rice", "nutrient": "protein"}}}}

Input: "Suggest foods under 300 calories"
Output: {{"intent": "CALORIE_BASED_RECOMMENDATION", "entities": {{"target_calories": 300, "comparison": "under"}}}}

Input: "Find foods around 500 kcal"
Output: {{"intent": "CALORIE_BASED_RECOMMENDATION", "entities": {{"target_calories": 500, "comparison": "around"}}}}

Input: "Low calorie foods" (không nói rõ số)
Output: {{"intent": "CALORIE_BASED_RECOMMENDATION", "entities": {{"target_calories": 200, "comparison": "under"}}}}

Input: "What should I eat for weight loss?"
Output: {{"intent": "GOAL_BASED_RECOMMENDATION", "entities": {{"goal": "lose_weight"}}}}

Input: "Suggest foods for gym people"
Output: {{"intent": "GOAL_BASED_RECOMMENDATION", "entities": {{"goal": "gain_muscle"}}}}

Input: "What to eat to gain weight?"
Output: {{"intent": "GOAL_BASED_RECOMMENDATION", "entities": {{"goal": "gain_weight"}}}}

Input: "Suggest foods" (mơ hồ, không nói rõ)
Output: {{"intent": "GOAL_BASED_RECOMMENDATION", "entities": {{"goal": "maintain_weight"}}}}

Input: "What's good food?" (mơ hồ)
Output: {{"intent": "GOAL_BASED_RECOMMENDATION", "entities": {{"goal": "maintain_weight"}}}}

Input: "Suggest a meal plan for today"
Output: {{"intent": "MEAL_PLAN_REQUEST", "entities": {{"duration": "daily"}}}}

Input: "Give me a menu for muscle building"
Output: {{"intent": "MEAL_PLAN_REQUEST", "entities": {{"duration": "daily", "goal": "gain_muscle"}}}}

Input: "What should I eat for breakfast lunch and dinner?"
Output: {{"intent": "MEAL_PLAN_REQUEST", "entities": {{"duration": "daily"}}}}

Input: "Create a daily meal plan for weight loss"
Output: {{"intent": "MEAL_PLAN_REQUEST", "entities": {{"duration": "daily", "goal": "lose_weight"}}}}


**VI. CÂU CẦN PHÂN LOẠI:**

"{english_message}"


**BẮT ĐẦU PHÂN TÍCH VÀ TRẢ VỀ JSON:**
"""
        
        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Remove markdown code blocks
            text = re.sub(r'```json\s*', '', text)
            text = re.sub(r'```\s*', '', text)
            text = text.strip()
            
            # Parse JSON
            result = json.loads(text)
            
            # Validate
            if 'intent' not in result:
                result['intent'] = 'SOCIAL'
            if 'entities' not in result:
                result['entities'] = {}
            
            return result
        
        except Exception as e:
            print(f"⚠️  Intent classification error: {e}")
            print(f"   Raw response: {response.text if 'response' in locals() else 'N/A'}")
            
            # Fallback
            return {
                "intent": "SOCIAL",
                "entities": {}
            }