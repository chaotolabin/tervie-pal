# Password Reset Token Model
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Index, Text, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class PasswordResetToken(Base):
    """
    Bảng password_reset_tokens - Quản lý password reset tokens (one-time use)
    
    Security:
    - Token hash lưu trong DB (không lưu token plaintext)
    - One-time use: used_at IS NOT NULL sau khi sử dụng
    - Revocation support: revoked_at for admin revoke
    - Auto-expiry: expires_at (15 minutes)
    """
    __tablename__ = "password_reset_tokens"
    
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="ID reset token record"
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="FK tới users.id"
    )
    
    token_hash: Mapped[str] = mapped_column(
        Text,
        unique=True,
        nullable=False,
        comment="Hash của reset token (SHA256 HMAC)"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Thời điểm tạo token"
    )
    
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Thời điểm hết hạn (15 phút từ lúc tạo)"
    )
    
    used_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Thời điểm sử dụng token (one-time use)"
    )
    
    revoked_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Thời điểm revoke token"
    )
    
    # Indexes
    __table_args__ = (
        Index(
            "ix_password_reset_tokens_user_id_active",
            "user_id",
            postgresql_where=text("used_at IS NULL AND revoked_at IS NULL")
        ),
        Index("ix_password_reset_tokens_token_hash", "token_hash", unique=True),
        Index("ix_password_reset_tokens_expires_at", "expires_at"),
    )

    def is_valid(self) -> bool:
        """
        Check if token is still valid
        
        Token is valid if:
        - Not expired (expires_at > now)
        - Not used (used_at IS NULL)
        - Not revoked (revoked_at IS NULL)
        
        Returns:
            True if token is valid, False otherwise
        """
        now = datetime.now(timezone.utc)
        return (
            self.expires_at > now
            and self.used_at is None
            and self.revoked_at is None
        )