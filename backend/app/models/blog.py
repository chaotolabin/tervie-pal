# Models cho Blog/Social Feed
import enum
import uuid
from datetime import datetime, timezone
from typing import Optional, List

from sqlalchemy import String, Text, BigInteger, Integer, Index, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SQLEnum

from app.models.base import Base, TimestampMixin


# Enum cho media type
class MediaType(str, enum.Enum):
    IMAGE = "image"
    VIDEO = "video"


class Post(Base, TimestampMixin):
    """Bảng posts - Bài viết của người dùng"""
    __tablename__ = "posts"
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="ID bài viết"
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="FK tới users.id"
    )
    
    title: Mapped[Optional[str]] = mapped_column(
        String(200),
        nullable=True,
        comment="Tiêu đề bài viết (tối đa 200 ký tự)"
    )
    
    content_text: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=False,
        comment="Nội dung text của bài viết"
    )

    like_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="Số lượt thích"
    )

    save_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
        comment="Số lượt lưu"
    )
    
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Soft delete timestamp" # Khoi phuc bai viet neu can
    )
    
    # Relationships
    media: Mapped[List["PostMedia"]] = relationship(
        "PostMedia",
        back_populates="post",
        cascade="all, delete-orphan"
    )

    hashtags: Mapped[List["Hashtag"]] = relationship(
        "Hashtag",
        secondary="post_hashtags",
        back_populates="posts",
        lazy="selectin"
    )
    
    # Index
    __table_args__ = (
        # Feed ca nhan, theo tac gia
        Index("ix_posts_user_id_created_at", "user_id", "created_at"),
        
        # Feed global (theo thoi gian tao)
        Index("ix_posts_created_at", "created_at"),

        # Feed theo trending - gan day: gioi han trong bao nhieu ngay
        Index("ix_posts_like_count_save_count_created_at", "like_count", "save_count", "created_at"),
    )

    # Vi du query:
    # SELECT *
    # FROM posts
    # WHERE user_id = '...'
    # ORDER BY created_at DESC;

    # SELECT *
    # FROM posts
    # WHERE deleted_at IS NULL
    # ORDER BY (like_count + save_count) DESC
    # LIMIT 20;

class PostMedia(Base):
    """Bảng post_media - Ảnh/video đính kèm bài viết"""
    __tablename__ = "post_media"
    
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="ID media"
    )
    
    post_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        comment="FK tới posts.id"
    )
    
    url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="URL ảnh/video"
    )
    
    media_type: Mapped[MediaType] = mapped_column(
        String(20),
        nullable=False,
        comment="Loại media: image"
    )
    
    mime_type: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="MIME type (vd: image/jpeg)"
    )
    
    width: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Chiều rộng (pixels)"
    )
    
    height: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment="Chiều cao (pixels)"
    )
    
    size_bytes: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        nullable=True,
        comment="Kích thước file (bytes)"
    )
    
    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Thứ tự sắp xếp"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Thời điểm upload"
    )
    
    # Relationship
    post: Mapped["Post"] = relationship(
        "Post",
        back_populates="media"
    )
    
    # Index
    __table_args__ = (
        Index("ix_post_media_post_id_sort_order", "post_id", "sort_order"),
    )


class PostLike(Base):
    """Bảng post_likes - Lượt thích bài viết"""
    __tablename__ = "post_likes"
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        comment="FK tới users.id"
    )
    
    post_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True,
        comment="FK tới posts.id"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Thời điểm like"
    )

    __table_args__ = (
        Index("ix_post_likes_user_created", "user_id", "created_at"),
    )


class PostSave(Base):
    """Bảng post_saves - Bài viết được lưu"""
    __tablename__ = "post_saves"
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        comment="FK tới users.id"
    )
    
    post_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True,
        comment="FK tới posts.id"
    )
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Thời điểm save"
    )

    __table_args__ = (
        Index("ix_post_saves_user_created", "user_id", "created_at"),
    )


class Hashtag(Base):
    __tablename__ = "hashtags"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="ID hashtag"
    )

    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        unique=True,
        comment="Tên hashtag (vd: eatclean, workout)"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    posts: Mapped[List["Post"]] = relationship(
        "Post",
        secondary="post_hashtags",
        back_populates="hashtags",
        lazy="selectin"
    )

    __table_args__ = (
        Index("ix_hashtags_name", "name"),
    )

class PostHashtag(Base):
    __tablename__ = "post_hashtags"

    post_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("posts.id", ondelete="CASCADE"),
        primary_key=True
    )

    hashtag_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("hashtags.id", ondelete="CASCADE"),
        primary_key=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    __table_args__ = (
        Index("ix_post_hashtags_post_id", "post_id"),
        Index("ix_post_hashtags_hashtag_id", "hashtag_id"),
    )