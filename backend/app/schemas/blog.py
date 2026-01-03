"""
Blog Schemas - Pydantic models cho Blog/Feed API
Tuân theo OpenAPI spec: PostCreateRequest, PostPatchRequest, PostDetail, FeedResponse, etc.
"""
import uuid
import enum
from datetime import datetime
from decimal import Decimal
from typing import Optional, List

from pydantic import BaseModel, Field


# ==================== Enums ====================
class MediaType(str, enum.Enum):
    """Loại media: image hoặc video"""
    IMAGE = "image"
    VIDEO = "video"


class FeedSort(str, enum.Enum):
    """Loại sắp xếp feed"""
    RECENT = "recent"
    TRENDING = "trending"


# ==================== Media Schemas ====================
class PostMediaIn(BaseModel):
    """
    Schema cho media input khi tạo/cập nhật post.
    URL từ ImageKit đã upload sẵn.
    """
    url: str = Field(..., description="URL ảnh/video từ ImageKit")
    media_type: MediaType = Field(..., description="Loại media: image hoặc video")
    mime_type: Optional[str] = Field(None, description="MIME type (vd: image/jpeg)")
    width: Optional[int] = Field(None, ge=0, description="Chiều rộng (pixels)")
    height: Optional[int] = Field(None, ge=0, description="Chiều cao (pixels)")
    size_bytes: Optional[int] = Field(None, ge=0, description="Kích thước file (bytes)")
    sort_order: int = Field(0, ge=0, description="Thứ tự sắp xếp")


class PostMediaOut(BaseModel):
    """Schema cho media output"""
    id: int = Field(..., description="ID media")
    url: str = Field(..., description="URL ảnh/video")
    media_type: MediaType = Field(..., description="Loại media")
    mime_type: Optional[str] = Field(None, description="MIME type")
    width: Optional[int] = Field(None, description="Chiều rộng (pixels)")
    height: Optional[int] = Field(None, description="Chiều cao (pixels)")
    size_bytes: Optional[int] = Field(None, description="Kích thước file (bytes)")
    sort_order: int = Field(..., description="Thứ tự sắp xếp")

    model_config = {"from_attributes": True}


# ==================== Post Schemas ====================
class PostCreateRequest(BaseModel):
    """
    Request body cho POST /posts - Tạo bài viết mới.
    Media URLs đã được upload lên ImageKit trước khi gọi API này.
    """
    title: str = Field(
        ...,
        min_length=15,
        max_length=50,
        description="Tiêu đề bài viết (15-50 ký tự)"
    )
    content_text: str = Field(
        ..., 
        min_length=100,
        max_length=10000,
        description="Nội dung text của bài viết (100-10000 ký tự)"
    )
    media: List[PostMediaIn] = Field(
        default=[],
        max_length=10,
        description="Danh sách media đính kèm (tối đa 10)"
    )
    hashtags: List[str] = Field(
        default=[],
        max_length=20,
        description="Danh sách hashtags (không có #, tối đa 20)"
    )


class PostPatchRequest(BaseModel):
    """
    Request body cho PATCH /posts/{post_id} - Cập nhật bài viết.
    Chỉ gửi fields cần cập nhật.
    """
    title: Optional[str] = Field(
        None,
        min_length=15,
        max_length=50,
        description="Tiêu đề mới (15-50 ký tự)"
    )
    content_text: Optional[str] = Field(
        None,
        min_length=100,
        max_length=10000,
        description="Nội dung text mới (100-10000 ký tự)"
    )
    media: Optional[List[PostMediaIn]] = Field(
        None,
        max_length=10,
        description="Danh sách media mới (thay thế toàn bộ)"
    )
    hashtags: Optional[List[str]] = Field(
        None,
        max_length=20,
        description="Danh sách hashtags mới (thay thế toàn bộ)"
    )


class PostDetail(BaseModel):
    """
    Response schema cho chi tiết bài viết.
    Bao gồm: metadata, counters, media list, hashtags.
    """
    id: int = Field(..., description="ID bài viết")
    user_id: uuid.UUID = Field(..., description="UUID tác giả")
    title: Optional[str] = Field(None, description="Tiêu đề bài viết")
    content_text: str = Field(..., description="Nội dung text")
    like_count: int = Field(..., ge=0, description="Số lượt thích")
    save_count: int = Field(..., ge=0, description="Số lượt lưu")
    created_at: datetime = Field(..., description="Thời điểm tạo")
    updated_at: Optional[datetime] = Field(None, description="Thời điểm cập nhật")
    media: List[PostMediaOut] = Field(..., description="Danh sách media")
    hashtags: List[str] = Field(..., description="Danh sách hashtag names")
    
    # User interaction flags (populated dynamically)
    is_liked: bool = Field(False, description="User hiện tại đã like?")
    is_saved: bool = Field(False, description="User hiện tại đã save?")

    model_config = {"from_attributes": True}


# ==================== Feed Schemas ====================
class FeedItem(PostDetail):
    """Item trong feed - kế thừa từ PostDetail"""
    pass


class FeedResponse(BaseModel):
    """
    Response cho GET /feed - Cursor-based pagination.
    next_cursor = None khi hết data.
    """
    items: List[FeedItem] = Field(..., description="Danh sách bài viết")
    next_cursor: Optional[str] = Field(None, description="Cursor cho trang tiếp theo")


# ==================== Hashtag Schemas ====================
class HashtagOut(BaseModel):
    """Schema cho hashtag output"""
    id: int = Field(..., description="ID hashtag")
    name: str = Field(..., description="Tên hashtag")

    model_config = {"from_attributes": True}


class HashtagSearchResponse(BaseModel):
    """Response cho GET /hashtags/search"""
    items: List[HashtagOut] = Field(..., description="Danh sách hashtags")


# ==================== Query Params ====================
class FeedQueryParams(BaseModel):
    """Query params cho GET /feed"""
    sort: FeedSort = Field(FeedSort.RECENT, description="Sắp xếp: recent hoặc trending")
    hashtag: Optional[str] = Field(None, description="Lọc theo hashtag")
    author_id: Optional[uuid.UUID] = Field(None, description="Lọc theo tác giả")
    saved: Optional[bool] = Field(None, description="Chỉ lấy bài đã lưu")
    limit: int = Field(20, ge=1, le=100, description="Số lượng items")
    cursor: Optional[str] = Field(None, description="Cursor pagination")


# ==================== Media Upload Schemas ====================
class MediaUploadResponse(BaseModel):
    """Response sau khi upload file lên ImageKit"""
    url: str = Field(..., description="URL của file trên ImageKit")
    file_id: str = Field(..., description="ImageKit file ID (dùng để xóa)")
    file_name: str = Field(..., description="Tên file trên ImageKit")
    media_type: MediaType = Field(..., description="Loại media: image hoặc video")
    mime_type: Optional[str] = Field(None, description="MIME type của file")
    width: Optional[int] = Field(None, description="Chiều rộng (pixels) - chỉ có với ảnh")
    height: Optional[int] = Field(None, description="Chiều cao (pixels) - chỉ có với ảnh")
    size_bytes: int = Field(..., description="Kích thước file (bytes)")
    sort_order: int = Field(0, description="Thứ tự sắp xếp (khi upload nhiều file)")


class MultipleMediaUploadResponse(BaseModel):
    """Response khi upload nhiều files"""
    items: List[MediaUploadResponse] = Field(..., description="Danh sách files đã upload")
