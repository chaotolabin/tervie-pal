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

    class Config:
        env_file = ".env"

settings = Settings()