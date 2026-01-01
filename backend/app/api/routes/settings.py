# Settings routes - thin layer: request → service → response
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.schemas import ChangePasswordRequest, ErrorResponse
from app.api.deps import get_current_user
from app.services import PasswordService


router = APIRouter(prefix="/settings", tags=["Settings"])


@router.patch(
    "/password",
    status_code=204,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid current password"},
        400: {"model": ErrorResponse, "description": "New password same as current"},
        422: {"description": "Validation Error"},
    }
)
async def change_password(
    req: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> None:
    """Change password for authenticated user"""
    try:
        PasswordService.change_password(
            db=db,
            user=current_user,
            current_password=req.current_password,
            new_password=req.new_password
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        print(f"Change password error: {e}")
        raise HTTPException(status_code=500, detail="Internal error")
