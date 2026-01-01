# Schemas initialization - export all schemas for convenient importing
from .auth import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    LogoutRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserPublic,
    AuthTokensResponse,
    RefreshResponse,
)
from .users import (
    Profile,
    ProfilePatchRequest,
    UserMeResponse,
    Session,
    SessionsListResponse,
    UserRolePatchRequest,
)
from .settings import ChangePasswordRequest
from .common import ErrorResponse, GenericMessageResponse

__all__ = [
    # Auth schemas
    "RegisterRequest",
    "LoginRequest",
    "RefreshRequest",
    "LogoutRequest",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "UserPublic",
    "AuthTokensResponse",
    "RefreshResponse",
    # User schemas
    "Profile",
    "ProfilePatchRequest",
    "UserMeResponse",
    "Session",
    "SessionsListResponse",
    "UserRolePatchRequest",
    # Settings schemas
    "ChangePasswordRequest",
    # Common schemas
    "ErrorResponse",
    "GenericMessageResponse",
]
