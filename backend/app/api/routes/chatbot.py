# chatbot.py

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.database import get_db
from app.services.nutri_chatbot.chatbot_service import ChatbotService


router = APIRouter(prefix="/api/chatbot", tags=["chatbot"])


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
    user_id: str = Header(None, alias="X-User-ID")  # ✅ Lấy từ header
):
  
    chatbot = ChatbotService(db, user_id=user_id)
    result = chatbot.chat(request.message)
    return result


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "chatbot"}