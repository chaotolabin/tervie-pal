from fastapi import APIRouter, Depends
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
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """Chatbot endpoint"""
    chatbot = ChatbotService(db)
    result = chatbot.chat(request.message)
    return result


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "chatbot"}
