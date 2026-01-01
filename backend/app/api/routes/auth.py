# Authentication routes - thin layer: request → service → response
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.schemas import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    RefreshResponse,
    AuthTokensResponse,
    ErrorResponse,
    LogoutRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    GenericMessageResponse,
    UserPublic,
)
from app.api.deps import get_current_user
from app.services import AuthService, PasswordService


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=AuthTokensResponse,
    status_code=200,
    responses={
        409: {"model": ErrorResponse, "description": "Username or email already exists"},
        422: {"description": "Validation Error"},
    }
)
async def register(
    req: RegisterRequest,
    db: Session = Depends(get_db),
    request: Request = None
) -> AuthTokensResponse:
    """Register new user"""
    try:
        # Create user via AuthService (which orchestrates all repositories)
        user, access_token, refresh_token = AuthService.register(
            db=db,
            username=req.username,
            email=req.email,
            password=req.password,
            full_name=req.full_name,
            gender=req.gender,
            date_of_birth=req.date_of_birth,
            height_cm=req.height_cm,
            weight_kg=req.weight_kg,
            baseline_activity=req.baseline_activity,
            goal_type=req.goal_type,
            weekly_goal=req.weekly_goal,
            goal_weight_kg=req.goal_weight_kg,
            weekly_exercise_min=req.weekly_exercise_min,
            device_label="Web Registration",
            user_agent=request.headers.get("user-agent") if request else "Unknown",
            ip_address=request.client.host if request and request.client else "0.0.0.0"
        )
        
        return AuthTokensResponse(
            user=UserPublic(id=user.id, username=user.username, email=user.email, role=user.role),
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer"
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Register error: {e}")
        raise HTTPException(status_code=500, detail="Internal error")


@router.post(
    "/login",
    response_model=AuthTokensResponse,
    status_code=200,
    responses={401: {"model": ErrorResponse, "description": "Invalid credentials"}}
)
async def login(
    req: LoginRequest,
    db: Session = Depends(get_db),
    request: Request = None
) -> AuthTokensResponse:
    """Login user"""
    try:
        user, access_token, refresh_token = AuthService.login(
            db=db,
            email_or_username=req.email_or_username,
            password=req.password,
            device_label=req.device_label,
            user_agent=request.headers.get("user-agent") if request else None,
            ip=request.client.host if request and request.client else None
        )
        
        return AuthTokensResponse(
            user=UserPublic(id=user.id, username=user.username, email=user.email, role=user.role),
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal error")


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    status_code=200,
    responses={401: {"model": ErrorResponse, "description": "Invalid refresh token"}}
)
async def refresh(req: RefreshRequest, db: Session = Depends(get_db)) -> RefreshResponse:
    """Refresh access token"""
    try:
        access_token, refresh_token = AuthService.refresh_access_token(
            db=db,
            refresh_token=req.refresh_token
        )
        return RefreshResponse(access_token=access_token, refresh_token=refresh_token)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Refresh error: {e}")
        raise HTTPException(status_code=500, detail="Internal error")


@router.post(
    "/logout",
    status_code=204,
    responses={401: {"model": ErrorResponse, "description": "Invalid refresh token"}}
)
async def logout(req: LogoutRequest, db: Session = Depends(get_db)) -> None:
    """Logout user"""
    try:
        AuthService.logout(db=db, refresh_token=req.refresh_token)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Logout error: {e}")
        raise HTTPException(status_code=500, detail="Internal error")


@router.post(
    "/forgot-password",
    response_model=GenericMessageResponse,
    status_code=200,
)
async def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)) -> GenericMessageResponse:
    """Request password reset token"""
    try:
        token_record, jwt_token = PasswordService.request_password_reset(db=db, email=req.email)
        
        if jwt_token:
            print(f"[DEV MODE] Password reset token for {req.email}: {jwt_token}")
        
        return GenericMessageResponse(message="If email exists, password reset link has been sent")
    except Exception as e:
        print(f"Forgot password error: {e}")
        return GenericMessageResponse(message="If email exists, password reset link has been sent")


@router.post(
    "/reset-password",
    status_code=204,
    responses={400: {"model": ErrorResponse, "description": "Invalid or expired token"}}
)
async def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)) -> None:
    """Reset password using token"""
    try:
        PasswordService.reset_password(db=db, token=req.token, new_password=req.new_password)
    except HTTPException:
        raise
    except Exception as e:
        print(f"Reset password error: {e}")
        raise HTTPException(status_code=400, detail="Invalid or expired token")
