# Quan ly tat ca cac cau hinh cua web tu file .env
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Project Information
    PROJECT_NAME: str
    PROJECT_VERSION: str
    
    # Database Configuration
    DATABASE_URL: str  # URL ket noi den PostgreSQL database

    # Gemini AI Configuration (Optional - chỉ cần khi sử dụng chatbot)
    GEMINI_API_KEY: Optional[str] = None

    # ChromaDB Configuration
    CHROMA_DB_PATH: str = "./chroma_db"
    
    # Can cap nhat gia tri nay de phu hop voi frontend
    FRONTEND_URL: Optional[str] = "http://testUrl.com"  # URL frontend
    
    # ImageKit Configuration (optional)
    # imagekit.io Configuration (optional)
    IMAGEKIT_PRIVATE_KEY: Optional[str] = None
    IMAGEKIT_PUBLIC_KEY: Optional[str] = None
    IMAGEKIT_URL: Optional[str] = None

    SMTP_ENABLED: bool = True
    SMTP_SERVER: Optional[str] = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None  # your-email@gmail.com
    SMTP_PASSWORD: Optional[str] = None  # App Password (16 chars)
    class Config:
        env_file = ".env"

settings = Settings()
