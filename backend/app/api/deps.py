"""
Dependencies cho API routes
- get_current_user_id: Mock dependency trả về UUID của user hiện tại
  (Sẽ thay bằng JWT authentication thực sau)
"""
import uuid
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.auth import User, UserRole

TEST_USER_ID = uuid.UUID("128283af-efdd-4359-90d4-a071754fdfff")

# TODO: Thay thế bằng JWT authentication thực
# Hiện tại mock để test biometrics endpoints
def get_current_user_id(db: Session = Depends(get_db)) -> uuid.UUID:
    """
    Mock dependency - Giả định user đã login
    
    Trong thực tế:
    1. Decode JWT token từ header Authorization
    2. Verify signature
    3. Extract user_id từ token payload
    4. Kiểm tra token chưa hết hạn, chưa bị revoke
    5. Return user_id
    
    Returns:
        uuid.UUID: ID của user hiện tại
    
    Raises:
        HTTPException 401: Nếu token invalid hoặc hết hạn
    """
    # Mock: Trả về một UUID cố định để test
    # Sau này sẽ decode từ JWT token
    existing_user = db.query(User).filter(User.id == TEST_USER_ID).first()
    
    if not existing_user:
        # Tạo test user mới
        test_user = User(
            id=TEST_USER_ID,
            username="testuser",
            email="testuser@example.com",
            password_hash="$2b$12$dummy_hash_for_testing",
            role=UserRole.USER
        )
        db.add(test_user)
        db.commit()
        print(f"Created test user: {TEST_USER_ID}")
    
    return TEST_USER_ID

# Type alias để dùng trong route parameters
CurrentUserID = Annotated[uuid.UUID, Depends(get_current_user_id)]