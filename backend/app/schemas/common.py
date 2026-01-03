# Common schemas used across API
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Error response"""
    detail: str


class GenericMessageResponse(BaseModel):
    """Generic success message"""
    message: str
