"""
Blog Service - Business logic cho Blog module.
Orchestrates repository operations, validation, authorization.
"""
import uuid
from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.blog_repository import BlogRepository
from app.models.blog import Post
from app.schemas.blog import (
    PostCreateRequest,
    PostPatchRequest,
    PostDetail,
    PostMediaOut,
    FeedItem,
    FeedResponse,
    HashtagOut,
    HashtagSearchResponse,
)


class BlogService:
    """Service cho Blog - business logic layer"""
    
    # ==================== POST CRUD ====================
    @staticmethod
    def create_post(
        db: Session,
        user_id: uuid.UUID,
        request: PostCreateRequest
    ) -> PostDetail:
        """
        Tạo bài viết mới.
        Flow: create post → add media → create/link hashtags → return detail
        """
        # 1. Create post
        post = BlogRepository.create_post(
            db=db,
            user_id=user_id,
            content_text=request.content_text,
            title=request.title
        )
        
        # 2. Add media (nếu có)
        if request.media:
            media_dicts = [m.model_dump() for m in request.media]
            BlogRepository.add_media_to_post(db, post.id, media_dicts)
        
        # 3. Handle hashtags (nếu có)
        if request.hashtags:
            hashtags = BlogRepository.get_or_create_hashtags(db, request.hashtags)
            hashtag_ids = [h.id for h in hashtags]
            BlogRepository.set_post_hashtags(db, post.id, hashtag_ids)
        
        db.commit()
        
        # Refetch để lấy relationships
        post = BlogRepository.get_post_by_id(db, post.id)
        return BlogService._to_post_detail(post, is_liked=False, is_saved=False)
    
    @staticmethod
    def get_post(
        db: Session,
        post_id: int,
        current_user_id: uuid.UUID
    ) -> PostDetail:
        """Lấy chi tiết bài viết"""
        post = BlogRepository.get_post_by_id(db, post_id)
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Check user interactions
        is_liked = BlogRepository.is_liked(db, current_user_id, post_id)
        is_saved = BlogRepository.is_saved(db, current_user_id, post_id)
        
        return BlogService._to_post_detail(post, is_liked, is_saved)
    
    @staticmethod
    def update_post(
        db: Session,
        post_id: int,
        current_user_id: uuid.UUID,
        request: PostPatchRequest
    ) -> PostDetail:
        """
        Cập nhật bài viết (chỉ tác giả).
        PATCH semantics: chỉ update fields được gửi.
        """
        post = BlogRepository.get_post_by_id(db, post_id)
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Authorization: chỉ tác giả mới được sửa
        if post.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to edit this post"
            )
        
        # Update title and content_text
        if request.title is not None or request.content_text is not None:
            BlogRepository.update_post(
                db, post,
                title=request.title,
                content_text=request.content_text
            )
        
        # Update media (thay thế toàn bộ nếu gửi)
        if request.media is not None:
            BlogRepository.delete_all_media_of_post(db, post_id)
            if request.media:
                media_dicts = [m.model_dump() for m in request.media]
                BlogRepository.add_media_to_post(db, post_id, media_dicts)
        
        # Update hashtags (thay thế toàn bộ nếu gửi)
        if request.hashtags is not None:
            if request.hashtags:
                hashtags = BlogRepository.get_or_create_hashtags(db, request.hashtags)
                hashtag_ids = [h.id for h in hashtags]
                BlogRepository.set_post_hashtags(db, post_id, hashtag_ids)
            else:
                BlogRepository.set_post_hashtags(db, post_id, [])
        
        db.commit()
        
        # Refetch
        post = BlogRepository.get_post_by_id(db, post_id)
        is_liked = BlogRepository.is_liked(db, current_user_id, post_id)
        is_saved = BlogRepository.is_saved(db, current_user_id, post_id)
        
        return BlogService._to_post_detail(post, is_liked, is_saved)
    
    @staticmethod
    def delete_post(
        db: Session,
        post_id: int,
        current_user_id: uuid.UUID
    ) -> None:
        """Soft delete bài viết (chỉ tác giả)"""
        post = BlogRepository.get_post_by_id(db, post_id)
        
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # Authorization
        if post.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not allowed to delete this post"
            )
        
        BlogRepository.soft_delete_post(db, post)
        db.commit()
    
    # ==================== LIKE / UNLIKE ====================
    @staticmethod
    def like_post(
        db: Session,
        post_id: int,
        user_id: uuid.UUID
    ) -> None:
        """Like bài viết"""
        # Check post exists
        post = BlogRepository.get_post_by_id(db, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        BlogRepository.add_like(db, user_id, post_id)
        db.commit()
    
    @staticmethod
    def unlike_post(
        db: Session,
        post_id: int,
        user_id: uuid.UUID
    ) -> None:
        """Unlike bài viết"""
        post = BlogRepository.get_post_by_id(db, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        BlogRepository.remove_like(db, user_id, post_id)
        db.commit()
    
    # ==================== SAVE / UNSAVE ====================
    @staticmethod
    def save_post(
        db: Session,
        post_id: int,
        user_id: uuid.UUID
    ) -> None:
        """Save bài viết"""
        post = BlogRepository.get_post_by_id(db, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        BlogRepository.add_save(db, user_id, post_id)
        db.commit()
    
    @staticmethod
    def unsave_post(
        db: Session,
        post_id: int,
        user_id: uuid.UUID
    ) -> None:
        """Unsave bài viết"""
        post = BlogRepository.get_post_by_id(db, post_id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        BlogRepository.remove_save(db, user_id, post_id)
        db.commit()
    
    # ==================== FEED ====================
    @staticmethod
    def get_feed(
        db: Session,
        user_id: uuid.UUID,
        sort: str = "recent",
        hashtag: Optional[str] = None,
        author_id: Optional[uuid.UUID] = None,
        saved_only: bool = False,
        limit: int = 15,
        page: int = 1
    ) -> FeedResponse:
        """
        Lấy feed với các filters.
        Offset/Limit pagination cho infinite scroll hoặc load more.
        """
        posts, total_count = BlogRepository.get_feed(
            db=db,
            user_id=user_id,
            sort=sort,
            hashtag=hashtag,
            author_id=author_id,
            saved_only=saved_only,
            limit=limit,
            page=page
        )
        
        # Lấy user interactions cho batch posts
        post_ids = [p.id for p in posts]
        liked_ids, saved_ids = BlogRepository.get_user_interactions(
            db, user_id, post_ids
        )
        
        # Convert to response
        items = [
            BlogService._to_post_detail(
                p,
                is_liked=(p.id in liked_ids),
                is_saved=(p.id in saved_ids)
            )
            for p in posts
        ]
        
        # Tính pagination info
        total_pages = (total_count + limit - 1) // limit  # ceil division
        has_next = page < total_pages
        
        return FeedResponse(
            items=items,
            page=page,
            limit=limit,
            total_count=total_count,
            total_pages=total_pages,
            has_next=has_next
        )
    
    # ==================== HASHTAGS ====================
    @staticmethod
    def search_hashtags(
        db: Session,
        query: str,
        limit: int = 20
    ) -> HashtagSearchResponse:
        """Tìm kiếm hashtags theo prefix"""
        hashtags = BlogRepository.search_hashtags(db, query, limit)
        items = [HashtagOut(id=h.id, name=h.name) for h in hashtags]
        return HashtagSearchResponse(items=items)
    
    @staticmethod
    def get_posts_by_hashtag(
        db: Session,
        user_id: uuid.UUID,
        hashtag_name: str,
        limit: int = 20,
        cursor: Optional[str] = None
    ) -> FeedResponse:
        """Lấy posts theo hashtag"""
        # Verify hashtag exists
        hashtag = BlogRepository.get_hashtag_by_name(db, hashtag_name)
        if not hashtag:
            # Trả về empty response thay vì 404
            return FeedResponse(items=[], next_cursor=None)
        
        return BlogService.get_feed(
            db=db,
            user_id=user_id,
            sort="recent",
            hashtag=hashtag_name,
            limit=limit,
            cursor=cursor
        )
    
    # ==================== HELPERS ====================
    @staticmethod
    def _to_post_detail(
        post: Post,
        is_liked: bool = False,
        is_saved: bool = False
    ) -> PostDetail:
        """Convert Post model to PostDetail schema"""
        return PostDetail(
            id=post.id,
            user_id=post.user_id,
            title=post.title,
            content_text=post.content_text,
            like_count=post.like_count,
            save_count=post.save_count,
            created_at=post.created_at,
            updated_at=post.updated_at,
            media=[
                PostMediaOut(
                    id=m.id,
                    url=m.url,
                    media_type=m.media_type,
                    mime_type=m.mime_type,
                    width=m.width,
                    height=m.height,
                    size_bytes=m.size_bytes,
                    sort_order=m.sort_order
                )
                for m in sorted(post.media, key=lambda x: x.sort_order)
            ],
            hashtags=[h.name for h in post.hashtags],
            is_liked=is_liked,
            is_saved=is_saved
        )