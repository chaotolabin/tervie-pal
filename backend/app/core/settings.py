# Quan ly tat ca cac cau hinh cua web tu file .env
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str
    PROJECT_VERSION: str

    class Config:
        env_file = ".env"

settings = Settings()