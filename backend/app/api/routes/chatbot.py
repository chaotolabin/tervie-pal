from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.api.deps import get_current_user  # ✅ Import authentication
from app.models.auth import User  # ✅ Import User model
from app.services.nutri_chatbot.chatbot_service import ChatbotService


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