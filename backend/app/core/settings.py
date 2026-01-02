# Quan ly tat ca cac cau hinh cua web tu file .env
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    # Project Information
    PROJECT_NAME: str
    PROJECT_VERSION: str
    
    # Database Configuration
    DATABASE_URL: str  # URL ket noi den PostgreSQL database
    
    # imagekit.io Configuration
    IMAGEKIT_PRIVATE_KEY: str
    IMAGEKIT_PUBLIC_KEY: str
    IMAGEKIT_URL: str

    SMTP_ENABLED: bool = True
    SMTP_SERVER: Optional[str] = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None  # your-email@gmail.com
    SMTP_PASSWORD: Optional[str] = None  # App Password (16 chars)

    class Config:
        env_file = ".env"

settings = Settings()