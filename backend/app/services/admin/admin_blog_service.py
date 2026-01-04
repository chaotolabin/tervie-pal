"""
Admin Service - Business Logic cho Admin Panel
Bao gồm: Dashboard Stats, User Management, Blog Management
"""
from datetime import datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException
import uuid

from app.models.auth import User
from app.models.blog import Post

class AdminBlogService:
    """Service xử lý Blog Management"""
    
    @staticmethod
    def get_posts_list(
        db: Session,
        page: int = 1,
        page_size: int = 50,
        include_deleted: bool = False
    ) -> Tuple[List[dict], int]:
        """Lấy danh sách posts (admin view)"""
        query = db.query(
            Post,
            User.username
        ).join(User, Post.user_id == User.id)
        
        if not include_deleted:
            query = query.filter(Post.deleted_at.is_(None))
        
        total = query.count()
        
        offset = (page - 1) * page_size
        results = query.order_by(desc(Post.created_at)).offset(offset).limit(page_size).all()
        
        items = []
        for post, username in results:
            items.append({
                "id": post.id,
                "user_id": post.user_id,
                "username": username,
                "title": post.title,
                "content_preview": post.content_text[:100] if post.content_text else "",
                "like_count": post.like_count,
                "save_count": post.save_count,
                "created_at": post.created_at,
                "deleted_at": post.deleted_at
            })
        
        return items, total
    
    @staticmethod
    def delete_post(
        db: Session,
        post_id: int,
        reason: Optional[str],
        admin_id: uuid.UUID
    ) -> Post:
        """Soft delete post"""
        post = db.query(Post).filter(Post.id == post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post.deleted_at:
            raise HTTPException(status_code=400, detail="Post already deleted")
        
        post.deleted_at = datetime.now(timezone.utc)
        post.updated_at = datetime.now(timezone.utc)
        
        # TODO: Log action
        
        db.commit()
        db.refresh(post)
        
        return post