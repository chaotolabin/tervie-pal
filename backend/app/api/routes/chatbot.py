from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# ===== Schema =====
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str


# ===== Simple rule-based chatbot =====
def simple_chatbot_logic(message: str) -> str:
    msg = message.lower()

    if any(word in msg for word in ["hello", "hi", "chào"]):
        return "Xin chào! Tôi có thể hỗ trợ dinh dưỡng và tập luyện cho bạn."

    if "calo" in msg or "calories" in msg:
        return "Lượng calo phụ thuộc vào mục tiêu và thể trạng của bạn. Bạn muốn giảm hay tăng cân?"

    if "bài tập" in msg or "exercise" in msg:
        return "Bạn có thể đi bộ, chạy bộ hoặc tập gym. Bạn muốn tập trong bao lâu?"

    return "Xin lỗi, tôi chưa hiểu rõ câu hỏi. Bạn có thể hỏi lại rõ hơn không?"


# ===== API Endpoint =====
@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    reply = simple_chatbot_logic(req.message)
    return ChatResponse(reply=reply)
