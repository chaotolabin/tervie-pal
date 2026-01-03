# Settings related schemas
from pydantic import BaseModel, Field


class ChangePasswordRequest(BaseModel):
    """Request body for change password"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
