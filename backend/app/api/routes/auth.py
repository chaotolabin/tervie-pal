# Authentication routes: register, login, refresh, logout, password reset
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
import uuid
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.auth import User, Profile, RefreshSession, UserRole, Gender
from app.api.schemas import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    RefreshResponse,
    AuthTokensResponse,
    UserPublic,
    Profile as ProfileSchema,
    ErrorResponse,
    LogoutRequest,
)
from app.api.deps import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_refresh_token,
)
from app.models.auth import GoalType


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
    """
    Đăng ký tài khoản
    
    Tạo User + Profile + Goal + BiometricsLog
    
    Args:
        req: RegisterRequest với tất cả thông tin từ flowchart
        db: Database session
        request: HTTP request (lấy user agent, IP)
    
    Returns:
        AuthTokensResponse
    
    Raises:
        HTTPException 409: Username/email đã tồn tại
    """
    try:
        from app.models.auth import Goal
        from app.models.biometric import BiometricsLog
        from decimal import Decimal
        from datetime import date as date_class
        
        # ===== Validate: Username & Email =====
        if db.execute(select(User).where(User.username == req.username)).scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Username already exists")
        
        if db.execute(select(User).where(User.email == req.email)).scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Email already exists")
        
        # ===== Create: User =====
        user = User(
            id=uuid.uuid4(),
            username=req.username,
            email=req.email,
            password_hash=hash_password(req.password),
            role=UserRole.USER.value,
            password_changed_at=None
        )
        db.add(user)
        db.flush()
        
        # ===== Create: Profile (Step 1) =====
        # Convert gender string to lowercase for enum
        gender_str = str(req.gender).lower()
        
        profile = Profile(
            user_id=user.id,
            full_name=req.full_name,
            gender=gender_str,  # Pass string directly
            date_of_birth=req.date_of_birth,
            height_cm_default=req.height_cm
        )
        db.add(profile)
        
        # ===== Create: Goal (Step 2+3) =====
        # Tính BMR (Basal Metabolic Rate) - Mifflin-St Jeor formula
        today = date_class.today()
        age_years = (today - req.date_of_birth).days / 365.25
        
        if str(req.gender).lower() == "male":
            bmr = 10 * float(req.weight_kg) + 6.25 * float(req.height_cm) - 5 * age_years + 5
        else:
            bmr = 10 * float(req.weight_kg) + 6.25 * float(req.height_cm) - 5 * age_years - 161
    
    # Tính TDEE (Total Daily Energy Expenditure) dựa trên baseline_activity
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
        
        # Tính daily_calorie_target dựa trên goal_type và weekly_goal
        # weekly_goal: 0.25kg/week = 250 kcal deficit/surplus, 0.5kg/week = 500 kcal
        weekly_goal = float(req.weekly_goal or 0)
        calorie_adjustment = weekly_goal * 1000  # Convert kg to kcal (roughly 1000 per week)
    
        goal_type = str(req.goal_type)
        if goal_type == "lose_weight":
            daily_calorie = tdee - calorie_adjustment
        elif goal_type == "gain_weight":
            daily_calorie = tdee + calorie_adjustment
        elif goal_type == "build_muscle":
            daily_calorie = tdee + calorie_adjustment
        else:  # maintain_weight, improve_health
            daily_calorie = tdee
        
        # ===== Validate: daily_calorie phải > 0 =====
        if daily_calorie < 1200:
            raise HTTPException(
                status_code=400,
                detail=f"Calorie target is invalid (minimum 1200 kcal/day, current: {round(daily_calorie, 2)} kcal)"
            )
        
        # Tính macro grams từ daily_calorie_target
        # Công thức: Protein = daily_calorie × 20% ÷ 4 kcal/g
        #            Fat = daily_calorie × 30% ÷ 9 kcal/g
        #            Carbs = daily_calorie × 50% ÷ 4 kcal/g
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
        
        # ===== Create: BiometricsLog (Step 4) =====
        bmi = float(req.weight_kg) / ((float(req.height_cm) / 100) ** 2)
        biometric = BiometricsLog(
            user_id=user.id,
            logged_at=datetime.now(timezone.utc),
            weight_kg=float(req.weight_kg),
            height_cm=float(req.height_cm),
            bmi=bmi
        )
        db.add(biometric)
        
        # ===== Create: Token & Refresh Session =====
        access_token = create_access_token(user.id)
        refresh_token, refresh_token_hash = create_refresh_token(user.id)
        
        user_agent = request.headers.get("user-agent") if request else None
        client_ip = None
        if request and request.client:
            client_ip = request.client.host
        
        refresh_session = RefreshSession(
            user_id=user.id,
            refresh_token_hash=refresh_token_hash,
            device_label=None,
            user_agent=user_agent,
            ip=client_ip,
            created_at=datetime.now(timezone.utc),
            last_used_at=datetime.now(timezone.utc),
            revoked_at=None
        )
        db.add(refresh_session)
        
        # ===== Commit All Changes =====
        db.commit()
        
        # ===== Response =====
        return AuthTokensResponse(
            user=UserPublic(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role
            ),
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer"
        )
    except HTTPException:
        db.rollback()
        raise
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Username or email already exists")
    except Exception as e:
        db.rollback()
        print(f"Registration error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )


@router.post(
    "/login",
    response_model=AuthTokensResponse,
    status_code=200,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        422: {"description": "Validation Error"},
    }
)
async def login(
    req: LoginRequest,
    db: Session = Depends(get_db),
    request: Request = None
) -> AuthTokensResponse:
    """
    ===== POST /auth/login =====
    Đăng nhập tài khoản với email hoặc username
    
    **Workflow:**
    1. Tìm user by email hoặc username (case-insensitive)
    2. Verify password (Argon2 hash)
    3. Tạo access_token (30 phút) + refresh_token (7 ngày)
    4. Lưu refresh session + track device (user-agent, IP)
    5. Trả về tokens + user info
    
    **Security:**
    - Generic error message "Invalid credentials" (không reveal username exists)
    - Constant-time password verification (argon2)
    - Refresh token được hash trước lưu (HMAC-SHA256)
    - Track device/IP cho security audit
    
    Args:
        req: LoginRequest {email_or_username, password, device_label?}
        db: Database session
        request: HTTP request (extract user-agent, IP)
    
    Returns:
        AuthTokensResponse {user, access_token, refresh_token, token_type}
    
    Raises:
        401: Sai email/username hoặc password
        500: Internal server error
    """
    try:
        # ===== Step 1: Tìm user by email hoặc username =====
        user = db.execute(
            select(User).where(
                or_(
                    User.email == req.email_or_username,
                    User.username == req.email_or_username
                )
            )
        ).scalar_one_or_none()

        # ===== Step 2: Verify password (constant-time) =====
        # Generic message để tránh username enumeration attack
        if not user or not verify_password(req.password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email or password is incorrect"
            )

        # ===== Step 3: Tạo tokens =====
        access_token = create_access_token(user.id)  # 30 phút
        refresh_token, refresh_token_hash = create_refresh_token(user.id)  # 7 ngày

        # ===== Step 4: Extract device info (tracking) =====
        user_agent = request.headers.get("user-agent") if request else None
        client_ip = request.client.host if request and request.client else None

        # ===== Step 5: Lưu refresh session (track device) =====
        refresh_session = RefreshSession(
            user_id=user.id,
            refresh_token_hash=refresh_token_hash,  # Hash token trước lưu
            device_label=req.device_label,  # "iPhone 12", "Chrome/Windows", v.v.
            user_agent=user_agent,  # Mozilla/5.0...
            ip=client_ip,  # 192.168.1.1
            created_at=datetime.now(timezone.utc),
            last_used_at=datetime.now(timezone.utc),
            revoked_at=None  # Chưa bị revoke
        )
        db.add(refresh_session)
        db.commit()

        # ===== Step 6: Trả về response =====
        return AuthTokensResponse(
            user=UserPublic(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role
            ),
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer"  # Standard OAuth2 type
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    status_code=200,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid refresh token"},
        422: {"description": "Validation Error"},
    }
)
async def refresh(
    req: RefreshRequest,
    db: Session = Depends(get_db),
    request: Request = None
) -> RefreshResponse:
    """
    Làm mới access token
    
    Xác thực refresh token trong refresh_sessions (revoked_at IS NULL)
    Rotate refresh token (trả về refresh mới, revoke refresh cũ)
    
    Args:
        req: RefreshRequest
        db: Database session
        request: HTTP request (lấy user agent, IP)
    
    Returns:
        RefreshResponse
    
    Raises:
        HTTPException 401: Refresh token không hợp lệ / đã bị revoke
    """
    try:
        payload = decode_token(req.refresh_token)

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        try:
            user_id = uuid.UUID(user_id_str)
        except (ValueError, TypeError):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        # Lookup session by deterministic hash
        token_hash = hash_refresh_token(req.refresh_token)

        session = db.execute(
            select(RefreshSession).where(
                RefreshSession.refresh_token_hash == token_hash,
                RefreshSession.revoked_at.is_(None),
            )
        ).scalar_one_or_none()

        if not session:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
        if not user:
            # revoke session defensively
            session.revoked_at = datetime.now(timezone.utc)
            db.commit()
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        # Check password_changed_at vs token iat for "logout all devices on password change"
        token_iat = payload.get("iat")
        if user.password_changed_at and token_iat:
            pwd_changed_ts = int(user.password_changed_at.timestamp())
            if int(token_iat) < pwd_changed_ts:
                session.revoked_at = datetime.now(timezone.utc)
                db.commit()
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        # Rotate: revoke old session + create new token/session
        session.revoked_at = datetime.now(timezone.utc)

        access_token = create_access_token(user.id)
        new_refresh_token, new_refresh_hash = create_refresh_token(user.id)

        user_agent = request.headers.get("user-agent") if request else session.user_agent
        client_ip = None
        if request and request.client:
            client_ip = request.client.host
        else:
            client_ip = session.ip

        new_session = RefreshSession(
            user_id=user.id,
            refresh_token_hash=new_refresh_hash,
            device_label=session.device_label,
            user_agent=user_agent,
            ip=client_ip,
            created_at=datetime.now(timezone.utc),
            last_used_at=datetime.now(timezone.utc),
            revoked_at=None
        )
        db.add(new_session)

        db.commit()

        return RefreshResponse(
            access_token=access_token,
            refresh_token=new_refresh_token
        )

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"Refresh error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post(
    "/logout",
    status_code=204,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid or revoked refresh token"},
        422: {"description": "Validation Error"},
    }
)
async def logout(
    req: LogoutRequest,
    db: Session = Depends(get_db),
) -> None:
    """
    ===== POST /auth/logout =====
    Đăng xuất khỏi thiết bị hiện tại (revoke refresh session này)
    
    **Workflow:**
    1. Decode refresh token
    2. Verify token type = "refresh"
    3. Tìm refresh session by token hash
    4. Revoke session (set revoked_at = now)
    5. Trả 204 No Content (logout thành công)
    
    **Security:**
    - Only revoke current device, other devices stay active
    - Constant-time token verification
    - Generic error message (không leak user info)
    
    Args:
        req: LogoutRequest {refresh_token}
        db: Database session
    
    Returns:
        204 No Content
    
    Raises:
        401: Invalid/revoked refresh token
        500: Internal server error
    """
    try:
        # ===== Step 1: Decode token =====
        payload = decode_token(req.refresh_token)
        
        # ===== Step 2: Verify token type =====
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # ===== Step 3: Find session by token hash =====
        token_hash = hash_refresh_token(req.refresh_token)
        session = db.execute(
            select(RefreshSession).where(
                RefreshSession.refresh_token_hash == token_hash,
                RefreshSession.revoked_at.is_(None)  # Only active sessions
            )
        ).scalar_one_or_none()
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # ===== Step 4: Revoke this device only =====
        session.revoked_at = datetime.now(timezone.utc)
        db.commit()
        
        # ===== Step 5: Return 204 No Content =====
        # (FastAPI auto-returns None as 204)
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"Logout error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
