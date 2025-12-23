from fastapi import APIRouter
from app.api.routes.chatbot import router as chatbot_router

router = APIRouter()

router.include_router(
    chatbot_router,
    prefix="/chatbot",
    tags=["chatbot"]
)

@router.get("/ping")
def ping():
    return {"msg": "api routes working"}
