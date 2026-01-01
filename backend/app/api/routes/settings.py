# Settings routes: change password, manage sessions
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, update
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.auth import User, RefreshSession
from app.api.schemas import (
    ChangePasswordRequest,
    ErrorResponse,
)
from app.api.deps import (
    hash_password,
    verify_password,
    get_current_user,
    update_user_password_and_revoke_sessions,
)


router = APIRouter(prefix="/settings", tags=["Settings"])


@router.patch(
    "/password",
    status_code=204,
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated or invalid current password"},
        400: {"model": ErrorResponse, "description": "New password same as current"},
        422: {"description": "Validation Error"},
    }
)
async def change_password(
    req: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> None:
    """
    ===== PATCH /settings/password =====
    Đổi mật khẩu (đăng xuất khỏi TẤT CẢ thiết bị)
    
    **Workflow:**
    1. Get current user từ access token (HTTPBearer)
    2. Verify current password trước khi thay đổi
    3. Validate new password != current password
    4. Update password_hash + password_changed_at
    5. Revoke ALL refresh sessions (logout all devices)
    6. Trả 204 No Content
    
    **Security:**
    - Verify current password trước (prevent account takeover)
    - Constant-time password verification
    - Update password_changed_at để revoke all tokens
    - All refresh tokens tự động invalid (iat < password_changed_at)
    
    Args:
        req: ChangePasswordRequest {current_password, new_password}
        db: Database session
        current_user: Current authenticated user (from access token)
    
    Returns:
        204 No Content
    
    Raises:
        401: Not authenticated or invalid current password
        400: New password same as current
        500: Internal server error
    """
    try:
        user = current_user
        
        # ===== Step 1: Verify current password =====
        if not verify_password(req.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Current password is incorrect"
            )
        
        # ===== Step 2: Validate new password != current =====
        if verify_password(req.new_password, user.password_hash):
            raise HTTPException(
                status_code=400,
                detail="New password must be different from current password"
            )
        
        # ===== Step 3: Update password + revoke sessions =====
        # Uses shared helper: update password_hash + revoke ALL refresh sessions
        update_user_password_and_revoke_sessions(user, req.new_password, db)
        db.commit()
        
        # ===== Step 4: Return 204 No Content =====
        
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"Change password error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal Server Error")
