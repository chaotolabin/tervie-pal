# Users routes - thin layer for user profile operations
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.schemas.users import UserMeResponse, Profile as ProfileSchema, UserPublic
from app.models.auth import User


router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserMeResponse,
    status_code=200,
    responses={401: {"description": "Not authenticated"}}
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> UserMeResponse:
    """Get current user profile and info"""
    try:
        # Refresh user from DB to ensure latest data
        db.refresh(current_user)
        
        # Get profile
        profile = current_user.profile
        profile_schema = ProfileSchema(
            user_id=profile.user_id,
            full_name=profile.full_name,
            gender=profile.gender,
            date_of_birth=str(profile.date_of_birth) if profile.date_of_birth else None,
            height_cm_default=profile.height_cm_default
        ) if profile else ProfileSchema(user_id=current_user.id)
        
        return UserMeResponse(
            user=UserPublic(
                id=current_user.id,
                username=current_user.username,
                email=current_user.email,
                role=current_user.role
            ),
            profile=profile_schema
        )
    except Exception as e:
        print(f"Get user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error"
        )