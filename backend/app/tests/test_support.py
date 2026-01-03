"""
Unit Tests cho Support Tickets
Test business logic: Create, List, Filter, Update tickets
"""
import pytest
import uuid
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi import HTTPException

from app.models.base import Base
from app.models.auth import User
from app.models.support import SupportTicket, TicketStatus, TicketCategory
from app.schemas.support_schema import (
    SupportTicketCreateRequest,
    AdminTicketPatchRequest
)
from app.services.support_service import SupportTicketService


# ==================== FIXTURES ====================

@pytest.fixture(scope="function")
def db_session():
    """Tạo in-memory SQLite database cho testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()


@pytest.fixture
def test_user(db_session: Session):
    """Tạo test user"""
    user = User(
        id=uuid.uuid4(),
        email="user@example.com",
        username="testuser",
        full_name="Test User"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session: Session):
    """Tạo test admin"""
    admin = User(
        id=uuid.uuid4(),
        email="admin@example.com",
        username="testadmin",
        full_name="Test Admin",
        role="admin"
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


# ==================== SUPPORT TICKET TESTS ====================

class TestSupportTicketService:
    """Test cases cho SupportTicketService"""

    def test_create_ticket_success(self, db_session, test_user):
        """Test tạo ticket thành công"""
        # Arrange
        data = SupportTicketCreateRequest(
            subject="Không thể đăng nhập",
            message="Tôi quên mật khẩu và không nhận được email reset",
            category=TicketCategory.BUG
        )
        
        # Act
        ticket = SupportTicketService.create_ticket(
            db=db_session,
            user_id=test_user.id,
            data=data
        )
        
        # Assert
        assert ticket is not None
        assert ticket.user_id == test_user.id
        assert ticket.subject == "Không thể đăng nhập"
        assert ticket.status == TicketStatus.OPEN  # Default status
        assert ticket.category == TicketCategory.BUG

    def test_create_ticket_without_category(self, db_session, test_user):
        """Test tạo ticket không có category (optional)"""
        # Arrange
        data = SupportTicketCreateRequest(
            subject="Câu hỏi về tính năng",
            message="Làm sao để xuất dữ liệu ra Excel?"
        )
        
        # Act
        ticket = SupportTicketService.create_ticket(
            db=db_session,
            user_id=test_user.id,
            data=data
        )
        
        # Assert
        assert ticket.category is None
        assert ticket.status == TicketStatus.OPEN

    def test_get_user_tickets(self, db_session, test_user):
        """Test lấy danh sách tickets của user"""
        # Arrange - Tạo 3 tickets
        for i in range(3):
            data = SupportTicketCreateRequest(
                subject=f"Ticket {i+1}",
                message=f"Message {i+1}",
                category=TicketCategory.QUESTION
            )
            SupportTicketService.create_ticket(db_session, test_user.id, data)
        
        # Act
        tickets, next_cursor = SupportTicketService.get_user_tickets(
            db=db_session,
            user_id=test_user.id,
            limit=10
        )
        
        # Assert
        assert len(tickets) == 3
        assert all(t.user_id == test_user.id for t in tickets)

    def test_get_user_tickets_with_status_filter(self, db_session, test_user):
        """Test filter tickets theo status"""
        # Arrange - Tạo tickets với status khác nhau
        ticket1_data = SupportTicketCreateRequest(
            subject="Open ticket",
            message="This is open"
        )
        ticket1 = SupportTicketService.create_ticket(db_session, test_user.id, ticket1_data)
        
        # Manually update status for testing
        ticket1.status = TicketStatus.RESOLVED
        db_session.commit()
        
        ticket2_data = SupportTicketCreateRequest(
            subject="Another open",
            message="Still open"
        )
        SupportTicketService.create_ticket(db_session, test_user.id, ticket2_data)
        
        # Act - Filter OPEN only
        tickets, _ = SupportTicketService.get_user_tickets(
            db=db_session,
            user_id=test_user.id,
            status_filter=TicketStatus.OPEN
        )
        
        # Assert
        assert len(tickets) == 1
        assert tickets[0].status == TicketStatus.OPEN

    def test_get_user_tickets_pagination(self, db_session, test_user):
        """Test phân trang"""
        # Arrange - Tạo 5 tickets
        for i in range(5):
            data = SupportTicketCreateRequest(
                subject=f"Ticket {i}",
                message="Message"
            )
            SupportTicketService.create_ticket(db_session, test_user.id, data)
        
        # Act - Lấy trang 1 (limit 2)
        page1_tickets, cursor1 = SupportTicketService.get_user_tickets(
            db=db_session,
            user_id=test_user.id,
            limit=2
        )
        
        # Assert page 1
        assert len(page1_tickets) == 2
        assert cursor1 is not None  # Có next page
        
        # Act - Lấy trang 2
        page2_tickets, cursor2 = SupportTicketService.get_user_tickets(
            db=db_session,
            user_id=test_user.id,
            limit=2,
            cursor=cursor1
        )
        
        # Assert page 2
        assert len(page2_tickets) == 2
        assert cursor2 is not None
        
        # Verify không trùng tickets
        page1_ids = {t.id for t in page1_tickets}
        page2_ids = {t.id for t in page2_tickets}
        assert page1_ids.isdisjoint(page2_ids)

    def test_get_all_tickets_admin(self, db_session, test_user):
        """Test admin lấy tất cả tickets"""
        # Arrange - Tạo tickets từ nhiều users
        user2 = User(
            id=uuid.uuid4(),
            email="user2@example.com",
            username="user2"
        )
        db_session.add(user2)
        db_session.commit()
        
        # User 1 tạo 2 tickets
        for i in range(2):
            data = SupportTicketCreateRequest(subject=f"User1 Ticket {i}", message="msg")
            SupportTicketService.create_ticket(db_session, test_user.id, data)
        
        # User 2 tạo 1 ticket
        data = SupportTicketCreateRequest(subject="User2 Ticket", message="msg")
        SupportTicketService.create_ticket(db_session, user2.id, data)
        
        # Act - Admin lấy tất cả
        tickets, _ = SupportTicketService.get_all_tickets(
            db=db_session,
            limit=50
        )
        
        # Assert
        assert len(tickets) == 3  # Cả 2 users

    def test_get_ticket_by_id_success(self, db_session, test_user):
        """Test lấy ticket theo ID"""
        # Arrange
        data = SupportTicketCreateRequest(
            subject="Test ticket",
            message="Message"
        )
        created_ticket = SupportTicketService.create_ticket(db_session, test_user.id, data)
        
        # Act
        ticket = SupportTicketService.get_ticket_by_id(db_session, created_ticket.id)
        
        # Assert
        assert ticket.id == created_ticket.id
        assert ticket.subject == "Test ticket"

    def test_get_ticket_by_id_not_found(self, db_session):
        """Test lỗi khi ticket không tồn tại"""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            SupportTicketService.get_ticket_by_id(db_session, 9999)
        
        assert exc_info.value.status_code == 404

    def test_update_ticket_status(self, db_session, test_user):
        """Test admin cập nhật status"""
        # Arrange
        data = SupportTicketCreateRequest(subject="Test", message="Msg")
        ticket = SupportTicketService.create_ticket(db_session, test_user.id, data)
        
        # Act - Update status
        update_data = AdminTicketPatchRequest(status=TicketStatus.IN_PROGRESS)
        updated_ticket = SupportTicketService.update_ticket(
            db=db_session,
            ticket_id=ticket.id,
            data=update_data
        )
        
        # Assert
        assert updated_ticket.status == TicketStatus.IN_PROGRESS
        assert updated_ticket.subject == "Test"  # Không thay đổi

    def test_update_ticket_category(self, db_session, test_user):
        """Test admin cập nhật category"""
        # Arrange
        data = SupportTicketCreateRequest(
            subject="Test",
            message="Msg",
            category=TicketCategory.QUESTION
        )
        ticket = SupportTicketService.create_ticket(db_session, test_user.id, data)
        
        # Act
        update_data = AdminTicketPatchRequest(category=TicketCategory.BUG)
        updated_ticket = SupportTicketService.update_ticket(
            db=db_session,
            ticket_id=ticket.id,
            data=update_data
        )
        
        # Assert
        assert updated_ticket.category == TicketCategory.BUG

    def test_update_ticket_partial(self, db_session, test_user):
        """Test partial update (chỉ update 1 field)"""
        # Arrange
        data = SupportTicketCreateRequest(
            subject="Test",
            message="Msg",
            category=TicketCategory.QUESTION
        )
        ticket = SupportTicketService.create_ticket(db_session, test_user.id, data)
        
        # Act - Chỉ update status
        update_data = AdminTicketPatchRequest(status=TicketStatus.RESOLVED)
        updated_ticket = SupportTicketService.update_ticket(
            db=db_session,
            ticket_id=ticket.id,
            data=update_data
        )
        
        # Assert
        assert updated_ticket.status == TicketStatus.RESOLVED
        assert updated_ticket.category == TicketCategory.QUESTION  # Không đổi


# ==================== RUN TESTS ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
