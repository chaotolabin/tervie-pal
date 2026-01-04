from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.core.settings import settings
from app.api.deps import get_current_user  # ✅ Import authentication
from app.models.auth import User  # ✅ Import User model
# Lazy import để tránh lỗi khi không có google-generativeai package
# ChatbotService = None  # Sẽ được import khi cần


router = APIRouter(prefix="/chatbot", tags=["chatbot"])


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    intent: str
    data: dict | list | None = None


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)  # ✅ Require authentication
):
    """
    Chatbot endpoint - Requires authentication
    
    - Automatically gets user profile from database
    - Personalizes responses based on user's goals and biometrics
    - Requires: Authorization: Bearer <access_token>
    """
    # Kiểm tra GEMINI_API_KEY trước khi sử dụng
    if not settings.GEMINI_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Chatbot service is not available. GEMINI_API_KEY is not configured. Please set GEMINI_API_KEY in your .env file."
        )
    
    # Lazy import ChatbotService để tránh lỗi khi không có google-generativeai
    try:
        from app.services.nutri_chatbot.chatbot_service import ChatbotService
    except ImportError as e:
        if "google" in str(e).lower() or "generativeai" in str(e).lower():
            raise HTTPException(
                status_code=503,
                detail="Chatbot service is not available. Please install google-generativeai package: pip install google-generativeai"
            )
        raise
    
    try:
        # ✅ Pass user_id to ChatbotService
        chatbot = ChatbotService(db=db, user_id=current_user.id)
        result = chatbot.chat(request.message)
        return result
    except Exception as e:
        print(f"❌ Chatbot error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "chatbot"}