"""
Router cho Biometrics Module - API Endpoints
Xử lý HTTP requests/responses, gọi Service layer cho business logic
"""
import uuid
from datetime import date
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.auth import User
from app.services.biometric_service import BiometricService
from app.schemas.biometric_schema import (
    BiometricsCreateRequest,
    BiometricsPatchRequest,
    BiometricsLogResponse,
    BiometricsListResponse
)


# Tạo router với prefix và tags
router = APIRouter(
    prefix="/biometrics",
    tags=["Biometrics"]
)


@router.post(
    "",
    response_model=BiometricsLogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create biometrics log",
    description="Tạo một log mới về cân nặng và chiều cao. BMI sẽ tự động được tính."
)
def create_biometrics_log(
    data: BiometricsCreateRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> BiometricsLogResponse:
    """
    POST /biometrics - Tạo biometrics log mới
    
    Args:
        data: Request body với logged_at, weight_kg, height_cm
        db: Database session (auto-injected)
        current_user: User hiện tại (auto-injected từ JWT)
    
    Returns:
        BiometricsLogResponse: Log vừa tạo, bao gồm BMI đã tính
    
    Raises:
        401 Unauthorized: Nếu chưa login
        422 Validation Error: Nếu dữ liệu không hợp lệ
    """
    db_log = BiometricService.create_biometrics_log(db, current_user.id, data)
    return BiometricsLogResponse.model_validate(db_log)


@router.get(
    "",
    response_model=BiometricsListResponse,
    summary="List biometrics logs",
    description="Lấy danh sách logs trong khoảng thời gian. Sắp xếp theo logged_at DESC."
)
def list_biometrics_logs(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    from_date: Annotated[Optional[date], Query(
        alias="from",
        description="Ngày bắt đầu (YYYY-MM-DD)"
    )] = None,
    to_date: Annotated[Optional[date], Query(
        alias="to",
        description="Ngày kết thúc (YYYY-MM-DD)"
    )] = None,
    limit: Annotated[int, Query(
        ge=1,
        le=365,
        description="Số lượng records tối đa"
    )] = 100
) -> BiometricsListResponse:
    """
    GET /biometrics?from=2025-12-01&to=2025-12-31&limit=100
    
    Args:
        db: Database session
        current_user: User hiện tại
        from_date: Ngày bắt đầu (optional, inclusive)
        to_date: Ngày kết thúc (optional, inclusive)
        limit: Số records tối đa (default 100, max 365)
    
    Returns:
        BiometricsListResponse: Danh sách logs
    
    Example:
        GET /biometrics?from=2025-12-01&to=2025-12-31
        GET /biometrics?limit=30  # Lấy 30 records gần nhất
    """
    logs = BiometricService.get_biometrics_logs(
        db=db,
        user_id=current_user.id,
        from_date=from_date,
        to_date=to_date,
        limit=limit
    )
    
    return BiometricsListResponse(
        items=[BiometricsLogResponse.model_validate(log) for log in logs]
    )


@router.get(
    "/latest",
    response_model=BiometricsLogResponse,
    summary="Get latest biometrics record",
    description="Lấy biometrics log mới nhất của user"
)
def get_latest_biometrics(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> BiometricsLogResponse:
    """
    GET /biometrics/latest
    
    Args:
        db: Database session
        current_user: User hiện tại
    
    Returns:
        BiometricsLogResponse: Log mới nhất
    
    Raises:
        404 Not Found: Nếu user chưa có log nào
    """
    from fastapi import HTTPException
    
    db_log = BiometricService.get_latest_biometrics(db, current_user.id)
    
    if not db_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No biometrics logs found for this user"
        )
    
    return BiometricsLogResponse.model_validate(db_log)


@router.patch(
    "/{biometric_id}",
    response_model=BiometricsLogResponse,
    summary="Update a biometrics record",
    description="Cập nhật một log hiện có. BMI sẽ tự động tính lại nếu weight/height thay đổi."
)
def update_biometrics_log(
    biometric_id: int,
    data: BiometricsPatchRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> BiometricsLogResponse:
    """
    PATCH /biometrics/{biometric_id}
    
    Args:
        biometric_id: ID của log cần update
        data: Dữ liệu cần update (partial - chỉ gửi fields cần thay đổi)
        db: Database session
        current_user: User hiện tại
    
    Returns:
        BiometricsLogResponse: Log sau khi update
    
    Raises:
        404 Not Found: Nếu log không tồn tại hoặc không thuộc về user
        422 Validation Error: Nếu dữ liệu không hợp lệ
    
    Example:
        PATCH /biometrics/123
        {
            "weight_kg": 76.0  // Chỉ update cân nặng
        }
    """
    db_log = BiometricService.update_biometrics_log(
        db=db,
        biometric_id=biometric_id,
        user_id=current_user.id,
        data=data
    )
    
    return BiometricsLogResponse.model_validate(db_log)


@router.delete(
    "/{biometric_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a biometrics record",
    description="Xóa vĩnh viễn một log (hard delete)"
)
def delete_biometrics_log(
    biometric_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
) -> None:
    """
    DELETE /biometrics/{biometric_id}
    
    Args:
        biometric_id: ID của log cần xóa
        db: Database session
        current_user: User hiện tại
    
    Returns:
        None: Status 204 No Content (không có response body)
    
    Raises:
        404 Not Found: Nếu log không tồn tại hoặc không thuộc về user
    
    Note:
        Đây là hard delete (xóa vĩnh viễn), không phải soft delete.
        Cân nhắc thêm soft delete nếu cần lưu trữ lịch sử.
    """
    BiometricService.delete_biometrics_log(
        db=db,
        biometric_id=biometric_id,
        user_id=current_user.id
    )
    # FastAPI tự động trả về 204 No Content

@router.get(
    "/summary",
    summary="Biometrics summary",
)
def biometrics_summary(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    from_date: Annotated[date, Query(alias="from")],
    to_date: Annotated[date, Query(alias="to")],
):
    return BiometricService.get_summary(
        db=db,
        user_id=current_user.id,
        from_date=from_date,
        to_date=to_date
    )