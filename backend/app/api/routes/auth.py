# Authentication routes: register, login, refresh, logout, password reset
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import select
import uuid
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.auth import User, Profile, RefreshSession, UserRole
from app.api.schemas import (
    RegisterRequest,
    LoginRequest,
    AuthTokensResponse,
    UserPublic,
    Profile as ProfileSchema,
    ErrorResponse,
)
from app.api.deps import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)


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
    Đăng ký tài khoản mới
    
    - Kiểm tra username và email đã tồn tại chưa
    - Tạo User với role mặc định là "user"
    - Tạo Profile rỗng (người dùng có thể cập nhật sau)
    - Tạo access token và refresh token
    - Lưu refresh session vào DB
    
    Args:
        req: RegisterRequest với username, email, password
        db: Database session
        request: HTTP request (lấy user agent, IP)
    
    Returns:
        AuthTokensResponse với user info, access_token, refresh_token
    
    Raises:
        HTTPException 409: Username hoặc email đã tồn tại
    """
    # 1. Kiểm tra username đã tồn tại
    stmt = select(User).where(User.username == req.username)
    existing_user = db.execute(stmt).scalar_one_or_none()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )
    
    # 2. Kiểm tra email đã tồn tại
    stmt = select(User).where(User.email == req.email)
    existing_email = db.execute(stmt).scalar_one_or_none()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )
    
    # 3. Tạo User mới
    user = User(
        id=uuid.uuid4(),
        username=req.username,
        email=req.email,
        password_hash=hash_password(req.password),
        role=UserRole.USER.value,  # Use .value to get the string 'user'
        password_changed_at=None
    )
    
    # 4. Tạo Profile rỗng cho user
    profile = Profile(
        user_id=user.id,
        full_name=None,
        gender=None,
        date_of_birth=None,
        height_cm_default=None
    )
    
    db.add(user)
    db.add(profile)
    db.flush()  # Đảm bảo user được insert trước khi tạo refresh session
    
    # 5. Tạo access token
    access_token = create_access_token(user.id)
    
    # 6. Tạo refresh token và lưu vào DB
    refresh_token, refresh_token_hash = create_refresh_token()
    
    user_agent = request.headers.get("user-agent") if request else None
    client_ip = request.client.host if request else None
    
    refresh_session = RefreshSession(
        user_id=user.id,
        refresh_token_hash=refresh_token_hash,
        device_label=None,
        user_agent=user_agent,
        ip=client_ip,
        created_at=datetime.now(timezone.utc),
        last_used_at=None,
        revoked_at=None
    )
    
    db.add(refresh_session)
    db.commit()
    
    # 7. Trả về response
    return AuthTokensResponse(
        user=UserPublic(
            id=user.id,
            username=user.username,
            email=user.email,
            role=user.role  # Already a string now
        ),
        access_token=access_token,
        refresh_token=refresh_token
    )