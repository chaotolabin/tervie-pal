"""
Service Layer cho Support Tickets
Business logic: CRUD operations, filtering, pagination
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc
from fastapi import HTTPException, status

from app.models.support import SupportTicket, TicketStatus, TicketCategory
from app.schemas.support_schema import (
    SupportTicketCreateRequest,
    AdminTicketPatchRequest
)


class SupportTicketService:
    """Service xử lý nghiệp vụ Support Tickets"""

    @staticmethod
    def create_ticket(
        db: Session,
        user_id: uuid.UUID,
        data: SupportTicketCreateRequest
    ) -> SupportTicket:
        """
        Tạo ticket mới
        
        Args:
            db: Database session
            user_id: UUID của user đang đăng nhập
            data: Dữ liệu ticket từ request
        
        Returns:
            SupportTicket: Ticket vừa tạo
        """
        ticket = SupportTicket(
            user_id=user_id,
            subject=data.subject,
            message=data.message,
            category=data.category,
            status=TicketStatus.OPEN.value  # Mặc định OPEN
        )
        
        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        
        return ticket

    @staticmethod
    def get_user_tickets(
        db: Session,
        user_id: uuid.UUID,
        status_filter: Optional[TicketStatus] = None,
        category_filter: Optional[TicketCategory] = None,
        limit: int = 20,
        cursor: Optional[str] = None
    ) -> Tuple[List[SupportTicket], Optional[str]]:
        """
        Lấy danh sách tickets của user (có filter và phân trang)
        
        Args:
            db: Database session
            user_id: UUID của user
            status_filter: Filter theo status (optional)
            category_filter: Filter theo category (optional)
            limit: Số lượng items mỗi trang
            cursor: Cursor cho phân trang (ID của ticket cuối cùng trang trước)
        
        Returns:
            Tuple[List[SupportTicket], Optional[str]]: 
                - Danh sách tickets
                - Next cursor (ID của ticket cuối cùng)
        """
        # Build query
        conditions = [SupportTicket.user_id == user_id]
        
        # Apply filters
        if status_filter:
            conditions.append(SupportTicket.status == status_filter)
        
        if category_filter:
            conditions.append(SupportTicket.category == category_filter)
        
        # Apply cursor pagination
        if cursor:
            try:
                cursor_id = int(cursor)
                conditions.append(SupportTicket.id < cursor_id)
            except ValueError:
                pass  # Invalid cursor, ignore
        
        # Execute query
        stmt = (
            select(SupportTicket)
            .where(and_(*conditions))
            .order_by(desc(SupportTicket.id))
            .limit(limit + 1)  # Lấy thêm 1 để check có trang tiếp theo không
        )
        
        result = db.execute(stmt)
        tickets = list(result.scalars().all())
        
        # Calculate next cursor
        next_cursor = None
        if len(tickets) > limit:
            next_cursor = str(tickets[limit - 1].id)
            tickets = tickets[:limit]  # Chỉ trả về đúng limit items
        
        return tickets, next_cursor

    @staticmethod
    def get_all_tickets(
        db: Session,
        status_filter: Optional[TicketStatus] = None,
        category_filter: Optional[TicketCategory] = None,
        limit: int = 50,
        cursor: Optional[str] = None
    ) -> Tuple[List[SupportTicket], Optional[str]]:
        """
        Lấy tất cả tickets (Admin only) - có filter và phân trang
        
        Args:
            db: Database session
            status_filter: Filter theo status (optional)
            category_filter: Filter theo category (optional)
            limit: Số lượng items mỗi trang
            cursor: Cursor cho phân trang
        
        Returns:
            Tuple[List[SupportTicket], Optional[str]]:
                - Danh sách tickets
                - Next cursor
        """
        conditions = []
        
        # Apply filters
        if status_filter:
            conditions.append(SupportTicket.status == status_filter)
        
        if category_filter:
            conditions.append(SupportTicket.category == category_filter)
        
        # Apply cursor pagination
        if cursor:
            try:
                cursor_id = int(cursor)
                conditions.append(SupportTicket.id < cursor_id)
            except ValueError:
                pass
        
        # Execute query
        stmt = (
            select(SupportTicket)
            .where(and_(*conditions)) if conditions else select(SupportTicket)
        )
        stmt = stmt.order_by(desc(SupportTicket.id)).limit(limit + 1)
        
        result = db.execute(stmt)
        tickets = list(result.scalars().all())
        
        # Calculate next cursor
        next_cursor = None
        if len(tickets) > limit:
            next_cursor = str(tickets[limit - 1].id)
            tickets = tickets[:limit]
        
        return tickets, next_cursor

    @staticmethod
    def get_ticket_by_id(
        db: Session,
        ticket_id: int
    ) -> SupportTicket:
        """
        Lấy ticket theo ID
        
        Args:
            db: Database session
            ticket_id: ID của ticket
        
        Returns:
            SupportTicket: Ticket detail
        
        Raises:
            404: Nếu không tìm thấy
        """
        ticket = db.query(SupportTicket).filter(
            SupportTicket.id == ticket_id
        ).first()
        
        if not ticket:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )
        
        return ticket

    @staticmethod
    def update_ticket(
        db: Session,
        ticket_id: int,
        data: AdminTicketPatchRequest
    ) -> SupportTicket:
        """
        Cập nhật ticket (Admin only)
        
        Args:
            db: Database session
            ticket_id: ID của ticket
            data: Dữ liệu cần update
        
        Returns:
            SupportTicket: Ticket sau khi update
        
        Raises:
            404: Nếu không tìm thấy
        """
        # Get ticket
        ticket = SupportTicketService.get_ticket_by_id(db, ticket_id)
        
        if not data.model_dump(exclude_unset=True):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        # Update fields (chỉ update field không None)
        if data.status is not None:
            ticket.status = data.status
        
        if data.category is not None:
            ticket.category = data.category
        
        # Cap nhat updated_at tu dong
        ticket.updated_at = datetime.now(timezone.utc)

        db.commit()
        db.refresh(ticket)
        
        return ticket