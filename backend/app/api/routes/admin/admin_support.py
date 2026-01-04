"""
API Routes cho Admin (Support Tickets Management)
Endpoints: GET/PATCH /admin/support/tickets
"""
from typing import Optional
from fastapi import APIRouter, Depends, status, Query, Path
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_admin_user
from app.models.support import TicketStatus, TicketCategory
from app.schemas.support import (
    AdminTicketPatchRequest,
    SupportTicketResponse,
    SupportTicketListResponse
)
from app.services.support_service import SupportTicketService


router = APIRouter()


# ==================== ADMIN SUPPORT ENDPOINTS ====================

@router.get(
    "/tickets",
    response_model=SupportTicketListResponse,
    summary="Admin - Xem tất cả tickets",
    description="""
    Admin xem tất cả tickets trong hệ thống.
    
    **Authorization:** Chỉ admin mới có quyền truy cập
    
    **Filtering:**
    - status: filter theo trạng thái
    - category: filter theo loại
    
    **Pagination:**
    - limit: số lượng items (default: 50, max: 200)
    - cursor: ID ticket cuối cùng trang trước
    
    **Use cases:**
    - Xem ai đang cần hỗ trợ
    - Filter tickets đang OPEN để xử lý
    - Theo dõi tickets đã RESOLVED/CLOSED
    """
)
def admin_list_all_tickets(
    status: Optional[TicketStatus] = Query(None, description="Filter theo status"),
    category: Optional[TicketCategory] = Query(None, description="Filter theo category"),
    limit: int = Query(50, ge=1, le=200, description="Số lượng items"),
    cursor: Optional[str] = Query(None, description="Cursor phân trang"),
    db: Session = Depends(get_db),
    _admin = Depends(get_current_admin_user)  # Check admin permission
):
    """Admin xem tất cả tickets"""
    tickets, next_cursor = SupportTicketService.get_all_tickets(
        db=db,
        status_filter=status,
        category_filter=category,
        limit=limit,
        cursor=cursor
    )
    
    # Convert tickets to response models (username đã được gán trong service)
    ticket_responses = []
    for ticket in tickets:
        # Tạo dict từ ticket attributes và thêm username
        ticket_dict = {
            "id": ticket.id,
            "user_id": ticket.user_id,
            "username": getattr(ticket, 'username', None),  # Lấy username đã được gán
            "subject": ticket.subject,
            "message": ticket.message,
            "category": ticket.category,
            "status": ticket.status,
            "created_at": ticket.created_at,
            "updated_at": ticket.updated_at
        }
        ticket_responses.append(SupportTicketResponse(**ticket_dict))
    
    return SupportTicketListResponse(
        items=ticket_responses,
        next_cursor=next_cursor
    )


@router.patch(
    "/tickets/{ticket_id}",
    response_model=SupportTicketResponse,
    summary="Admin - Cập nhật ticket",
    description="""
    Admin cập nhật trạng thái hoặc category của ticket.
    
    **Authorization:** Chỉ admin mới có quyền
    
    **Updatable fields:**
    - status: OPEN → IN_PROGRESS → RESOLVED → CLOSED
    - category: bug, feature_request, question, other
    
    **Business Logic:**
    - Chỉ cho phép update status và category
    - Không cho phép update subject/message
    - Tự động cập nhật updated_at
    
    **Use cases:**
    - Đánh dấu ticket đang xử lý (IN_PROGRESS)
    - Đánh dấu đã giải quyết (RESOLVED)
    - Đóng ticket (CLOSED)
    - Phân loại lại category
    """
)
def admin_update_ticket(
    ticket_id: int = Path(..., description="ID của ticket", ge=1),
    data: AdminTicketPatchRequest = ...,
    db: Session = Depends(get_db),
    _admin = Depends(get_current_admin_user)
):
    """Admin cập nhật status/category của ticket"""
    ticket = SupportTicketService.update_ticket(
        db=db,
        ticket_id=ticket_id,
        data=data
    )
    return SupportTicketResponse.model_validate(ticket)