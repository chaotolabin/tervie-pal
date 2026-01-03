"""
Blog Routes - API Endpoints cho Blog module.
Tuân theo OpenAPI spec: /feed, /posts, /posts/{id}, /posts/{id}/like, /posts/{id}/save, /hashtags

Endpoints:
- POST /media/upload: Upload single file lên ImageKit
- POST /media/upload-multiple: Upload nhiều files lên ImageKit
- GET /feed: Feed (recent/trending/hashtag/author/saved)
- POST /posts: Tạo bài viết
- GET /posts/{post_id}: Chi tiết bài viết
- PATCH /posts/{post_id}: Cập nhật bài viết (author only)
- DELETE /posts/{post_id}: Xóa bài viết (author only)
- POST /posts/{post_id}/like: Like bài viết
- DELETE /posts/{post_id}/like: Unlike bài viết
- POST /posts/{post_id}/save: Save bài viết
- DELETE /posts/{post_id}/save: Unsave bài viết
- GET /hashtags/search: Tìm hashtags
- GET /hashtags/{name}/posts: Bài viết theo hashtag
"""
import uuid
from typing import Optional, List

from fastapi import APIRouter, Depends, status, Query, File, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.auth import User
from app.services.blog_service import BlogService
from app.services.media_service import MediaService
from app.schemas.blog import (
    PostCreateRequest,
    PostPatchRequest,
    PostDetail,
    FeedResponse,
    HashtagSearchResponse,
    FeedSort,
    MediaUploadResponse,
    MultipleMediaUploadResponse,
)
from app.schemas.common import ErrorResponse


# ==================== Router Setup ====================
router = APIRouter(tags=["Blog"])


# ==================== MEDIA UPLOAD ====================
@router.post(
    "/media/upload",
    response_model=MediaUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload single file to ImageKit",
    description="""
    Upload một file (ảnh/video) lên ImageKit.
    
    **Supported formats:**
    - Images: JPEG, PNG, GIF, WebP (max 10MB)
    - Videos: MP4, MOV, AVI, WebM (max 100MB)
    
    **Response:** URL và metadata của file đã upload.
    Sử dụng URL này trong media array khi tạo/cập nhật post.
    """,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file type"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        413: {"model": ErrorResponse, "description": "File too large (image max 10MB, video max 100MB)"},
        503: {"model": ErrorResponse, "description": "ImageKit not configured"}
    }
)
async def upload_media(
    file: UploadFile = File(..., description="File ảnh hoặc video cần upload"),
    current_user: User = Depends(get_current_user)
) -> MediaUploadResponse:
    """
    Upload file lên ImageKit để lấy URL.
    
    Flow:
    1. Client chọn file → gọi API này
    2. Nhận về URL từ ImageKit
    3. Dùng URL này trong request tạo/cập nhật post
    """
    result = await MediaService.upload_file(
        file=file,
        user_id=current_user.id,
        folder="blog"
    )
    return MediaUploadResponse(**result)


@router.post(
    "/media/upload-multiple",
    response_model=MultipleMediaUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload multiple files to ImageKit",
    description="""
    Upload nhiều files (tối đa 10) lên ImageKit cùng lúc.
    
    **Supported formats:**
    - Images: JPEG, PNG, GIF, WebP (max 10MB mỗi file)
    - Videos: MP4, MOV, AVI, WebM (max 100MB mỗi file)
    
    **Response:** Danh sách URLs và metadata của các files đã upload.
    """,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid file type or too many files (max 10)"},
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        413: {"model": ErrorResponse, "description": "File too large (image max 10MB, video max 100MB)"},
        503: {"model": ErrorResponse, "description": "ImageKit not configured"}
    }
)
async def upload_multiple_media(
    files: List[UploadFile] = File(..., description="Danh sách files cần upload (tối đa 10)"),
    current_user: User = Depends(get_current_user)
) -> MultipleMediaUploadResponse:
    """
    Upload nhiều files lên ImageKit.
    
    Mỗi file sẽ có sort_order tự động theo thứ tự upload.
    """
    results = await MediaService.upload_multiple_files(
        files=files,
        user_id=current_user.id,
        folder="blog"
    )
    return MultipleMediaUploadResponse(
        items=[MediaUploadResponse(**r) for r in results]
    )


# ==================== FEED ====================
@router.get(
    "/feed",
    response_model=FeedResponse,
    summary="Get feed (recent/trending/hashtag/author/saved)",
    description="""
    Lấy feed với các filter:
    - sort: recent (mới nhất) hoặc trending (nhiều like/save)
    - hashtag: Lọc theo hashtag
    - author_id: Lọc theo tác giả
    - saved: true để chỉ lấy bài đã lưu
    
    Cursor-based pagination cho infinite scroll.
    """
)
async def get_feed(
    sort: FeedSort = Query(FeedSort.RECENT, description="Sắp xếp"),
    hashtag: Optional[str] = Query(None, description="Lọc theo hashtag"),
    author_id: Optional[uuid.UUID] = Query(None, description="Lọc theo tác giả"),
    saved: Optional[bool] = Query(None, description="Chỉ bài đã lưu"),
    limit: int = Query(20, ge=1, le=100, description="Số lượng items"),
    cursor: Optional[str] = Query(None, description="Cursor pagination"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FeedResponse:
    return BlogService.get_feed(
        db=db,
        user_id=current_user.id,
        sort=sort.value,
        hashtag=hashtag,
        author_id=author_id,
        saved_only=saved or False,
        limit=limit,
        cursor=cursor
    )


# ==================== POSTS CRUD ====================
@router.post(
    "/posts",
    response_model=PostDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new post",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        422: {"description": "Validation Error"}
    }
)
async def create_post(
    request: PostCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> PostDetail:
    """
    Tạo bài viết mới.
    
    Media URLs phải được upload lên ImageKit trước, sau đó gửi URLs trong request.
    Hashtags không cần ký tự #.
    """
    return BlogService.create_post(
        db=db,
        user_id=current_user.id,
        request=request
    )


@router.get(
    "/posts/{post_id}",
    response_model=PostDetail,
    summary="Get post detail",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Post not found"}
    }
)
async def get_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> PostDetail:
    """Lấy chi tiết bài viết theo ID"""
    return BlogService.get_post(
        db=db,
        post_id=post_id,
        current_user_id=current_user.id
    )


@router.patch(
    "/posts/{post_id}",
    response_model=PostDetail,
    summary="Update post (author only)",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Not allowed (not author)"},
        404: {"model": ErrorResponse, "description": "Post not found"},
        422: {"description": "Validation Error"}
    }
)
async def update_post(
    post_id: int,
    request: PostPatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> PostDetail:
    """
    Cập nhật bài viết (chỉ tác giả).
    
    PATCH semantics: chỉ gửi fields cần cập nhật.
    Media và hashtags sẽ được thay thế toàn bộ nếu gửi.
    """
    return BlogService.update_post(
        db=db,
        post_id=post_id,
        current_user_id=current_user.id,
        request=request
    )


@router.delete(
    "/posts/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete post (author only)",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        403: {"model": ErrorResponse, "description": "Not allowed (not author)"},
        404: {"model": ErrorResponse, "description": "Post not found"}
    }
)
async def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """Xóa bài viết (soft delete, chỉ tác giả)"""
    BlogService.delete_post(
        db=db,
        post_id=post_id,
        current_user_id=current_user.id
    )


# ==================== LIKE / UNLIKE ====================
@router.post(
    "/posts/{post_id}/like",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Like a post",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Post not found"}
    }
)
async def like_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """Like bài viết (idempotent - like lại không lỗi)"""
    BlogService.like_post(db=db, post_id=post_id, user_id=current_user.id)


@router.delete(
    "/posts/{post_id}/like",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unlike a post",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Post not found"}
    }
)
async def unlike_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """Unlike bài viết (idempotent)"""
    BlogService.unlike_post(db=db, post_id=post_id, user_id=current_user.id)


# ==================== SAVE / UNSAVE ====================
@router.post(
    "/posts/{post_id}/save",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Save a post",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Post not found"}
    }
)
async def save_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """Lưu bài viết để đọc sau (idempotent)"""
    BlogService.save_post(db=db, post_id=post_id, user_id=current_user.id)


@router.delete(
    "/posts/{post_id}/save",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unsave a post",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"},
        404: {"model": ErrorResponse, "description": "Post not found"}
    }
)
async def unsave_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> None:
    """Bỏ lưu bài viết (idempotent)"""
    BlogService.unsave_post(db=db, post_id=post_id, user_id=current_user.id)


# ==================== HASHTAGS ====================
@router.get(
    "/hashtags/search",
    response_model=HashtagSearchResponse,
    summary="Search hashtags",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"}
    }
)
async def search_hashtags(
    q: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(20, ge=1, le=100, description="Số lượng kết quả"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> HashtagSearchResponse:
    """Tìm kiếm hashtags theo prefix"""
    return BlogService.search_hashtags(db=db, query=q, limit=limit)


@router.get(
    "/hashtags/{name}/posts",
    response_model=FeedResponse,
    summary="Get posts by hashtag",
    responses={
        401: {"model": ErrorResponse, "description": "Not authenticated"}
    }
)
async def get_posts_by_hashtag(
    name: str,
    limit: int = Query(20, ge=1, le=100, description="Số lượng items"),
    cursor: Optional[str] = Query(None, description="Cursor pagination"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> FeedResponse:
    """Lấy bài viết theo hashtag"""
    return BlogService.get_posts_by_hashtag(
        db=db,
        user_id=current_user.id,
        hashtag_name=name,
        limit=limit,
        cursor=cursor
    )
