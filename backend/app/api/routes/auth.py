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
from app.models.auth import User, Goal, Profile
from app.models.biometric import BiometricsLog
from datetime import datetime, timezone, date
from decimal import Decimal


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
        # Create user via AuthService
        user, access_token, refresh_token = AuthService.register(
            db=db,
            username=req.username,
            email=req.email,
            password=req.password,
            role="user"
        )
        
        # Create Profile
        profile = Profile(
            user_id=user.id,
            full_name=req.full_name,
            gender=str(req.gender).lower(),
            date_of_birth=req.date_of_birth,
            height_cm_default=float(req.height_cm)
        )
        db.add(profile)
        
        # Calculate BMR & TDEE
        today = date.today()
        age_years = (today - req.date_of_birth).days / 365.25
        
        if str(req.gender).lower() == "male":
            bmr = 10 * float(req.weight_kg) + 6.25 * float(req.height_cm) - 5 * age_years + 5
        else:
            bmr = 10 * float(req.weight_kg) + 6.25 * float(req.height_cm) - 5 * age_years - 161
        
        activity_multipliers = {
            "sedentary": 1.2,
            "low_active": 1.375,
            "moderately_active": 1.55,
            "very_active": 1.725,
            "extremely_active": 1.9,
        }
        baseline_activity = str(req.baseline_activity).lower() if req.baseline_activity else "low_active"
        activity_multiplier = activity_multipliers.get(baseline_activity, 1.375)
        tdee = bmr * activity_multiplier
        
        # Calculate daily calorie
        weekly_goal = float(req.weekly_goal or 0)
        calorie_adjustment = weekly_goal * 1000
        
        goal_type = str(req.goal_type)
        if goal_type == "lose_weight":
            daily_calorie = tdee - calorie_adjustment
        elif goal_type == "gain_weight":
            daily_calorie = tdee + calorie_adjustment
        elif goal_type == "build_muscle":
            daily_calorie = tdee + calorie_adjustment
        else:
            daily_calorie = tdee
        
        if daily_calorie < 1200:
            raise HTTPException(status_code=400, detail="Calorie target too low")
        
        # Calculate macros in grams
        protein_grams = float(daily_calorie) * 0.20 / 4
        fat_grams = float(daily_calorie) * 0.30 / 9
        carb_grams = float(daily_calorie) * 0.50 / 4
        
        goal = Goal(
            user_id=user.id,
            goal_type=req.goal_type,
            target_weight_kg=req.goal_weight_kg,
            daily_calorie_target=Decimal(str(round(daily_calorie, 2))),
            protein_grams=Decimal(str(round(protein_grams, 2))),
            fat_grams=Decimal(str(round(fat_grams, 2))),
            carb_grams=Decimal(str(round(carb_grams, 2))),
            weekly_exercise_min=req.weekly_exercise_min or 150
        )
        db.add(goal)
        
        # Create biometrics log
        bmi = float(req.weight_kg) / ((float(req.height_cm) / 100) ** 2)
        biometric = BiometricsLog(
            user_id=user.id,
            logged_at=datetime.now(timezone.utc),
            weight_kg=float(req.weight_kg),
            height_cm=float(req.height_cm),
            bmi=bmi
        )
        db.add(biometric)
        db.commit()
        
        return AuthTokensResponse(
            user=UserPublic(id=user.id, username=user.username, email=user.email, role=user.role),
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer"
        )
    except HTTPException:
        db.rollback()
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
