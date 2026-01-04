from langdetect import detect, LangDetectException
from deep_translator import GoogleTranslator

class TranslateService:
    """
    Dịch query Việt → Anh
    
    ✅ THAY ĐỔI:
    - Dùng langdetect để detect ngôn ngữ (NHANH, CHÍNH XÁC)
    - Dùng deep_translator (Google Translate FREE API)
    - KHÔNG tốn Gemini quota
    - Cache để tránh dịch lại
    """
    
    def __init__(self):
        self.translator = GoogleTranslator(source='vi', target='en')
        self.cache = {}
    
    def is_vietnamese(self, text):
        """
        Kiểm tra có phải Tiếng Việt không bằng langdetect
        
        Args:
            text (str): Text cần kiểm tra
        
        Returns:
            bool: True nếu là tiếng Việt
        """
        try:
            # Detect language
            lang = detect(text)
            return lang == 'vi'
        except LangDetectException:
            # Nếu không detect được → coi như English
            return False
    
    def translate_to_english(self, text):
        """
        Dịch Việt → Anh với cache
        
        Args:
            text (str): Text cần dịch
        
        Returns:
            str: Text đã dịch (hoặc giữ nguyên nếu đã là English)
        
        Examples:
            >>> translate_to_english("trứng gà")
            "chicken egg"
            
            >>> translate_to_english("egg")
            "egg"
        """
        
        # Không phải tiếng Việt → trả về nguyên
        if not self.is_vietnamese(text):
            return text
        
        # Check cache
        if text in self.cache:
            return self.cache[text]
        
        try:
            # Dịch bằng Google Translate
            english = self.translator.translate(text)
            
            # Cache
            self.cache[text] = english
            
            print(f"🌏 Translated: '{text}' → '{english}'")
            
            return english
        
        except Exception as e:
            print(f"⚠️ Translation error: {e}")
            # Fallback: trả về text gốc
            return text