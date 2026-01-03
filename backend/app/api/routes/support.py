"""
API Routes cho Support Tickets (User endpoints)
Endpoints: POST/GET /support/tickets
"""
from typing import Optional
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.auth import User
from app.models.support import TicketStatus, TicketCategory
from app.schemas.support import (
    SupportTicketCreateRequest,
    SupportTicketResponse,
    SupportTicketListResponse
)
from app.services.support_service import SupportTicketService


router = APIRouter(tags=["Support"])


# ==================== USER ENDPOINTS ====================

@router.post(
    "/tickets",
    response_model=SupportTicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo ticket hỗ trợ mới",
    description="""
    Tạo yêu cầu hỗ trợ mới.
    
    **Business Logic:**
    - User phải đăng nhập
    - Status mặc định là OPEN
    - Tự động gán user_id của người đăng nhập
    
    **Validation:**
    - subject: max 200 ký tự
    - message: max 5000 ký tự
    - category: optional (bug, feature_request, question, other)
    """
)
def create_ticket(
    data: SupportTicketCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Tạo ticket hỗ trợ mới"""
    ticket = SupportTicketService.create_ticket(
        db=db,
        user_id=current_user.id,
        data=data
    )
    return SupportTicketResponse.model_validate(ticket)


@router.get(
    "/tickets",
    response_model=SupportTicketListResponse,
    summary="Xem danh sách tickets của tôi",
    description="""
    Lấy danh sách tất cả tickets mà user đã tạo.
    
    **Filtering:**
    - status: filter theo trạng thái (open, in_progress, resolved, closed)
    - category: filter theo loại (bug, feature_request, question, other)
    
    **Pagination:**
    - limit: số lượng items mỗi trang (default: 20, max: 100)
    - cursor: ID của ticket cuối cùng trang trước (để load trang tiếp)
    
    **Sorting:**
    - Sắp xếp theo created_at DESC (mới nhất trước)
    """
)
def list_my_tickets(
    status: Optional[TicketStatus] = Query(None, description="Filter theo status"),
    category: Optional[TicketCategory] = Query(None, description="Filter theo category"),
    limit: int = Query(20, ge=1, le=100, description="Số lượng items"),
    cursor: Optional[str] = Query(None, description="Cursor phân trang"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Lấy danh sách tickets của user đang đăng nhập"""
    tickets, next_cursor = SupportTicketService.get_user_tickets(
        db=db,
        user_id=current_user.id,
        status_filter=status,
        category_filter=category,
        limit=limit,
        cursor=cursor
    )
    
    return SupportTicketListResponse(
        items=[SupportTicketResponse.model_validate(ticket) for ticket in tickets],
        next_cursor=next_cursor
    )