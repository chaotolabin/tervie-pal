# Quan ly tat ca cac cau hinh cua web tu file .env
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    # Project Information
    PROJECT_NAME: str
    PROJECT_VERSION: str
    
    # Database Configuration
    DATABASE_URL: str  # URL ket noi den PostgreSQL database
    
    # ImageKit Configuration (optional)
    IMAGEKIT_PRIVATE_KEY: Optional[str] = None
    IMAGEKIT_PUBLIC_KEY: Optional[str] = None
    IMAGEKIT_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()