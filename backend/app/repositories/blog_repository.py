"""
Blog Repository - Data access layer cho Blog module.
CRUD operations cho posts, media, likes, saves, hashtags.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, List, Tuple

from sqlalchemy import select, delete, update, func, and_, or_, desc, asc
from sqlalchemy.orm import Session, selectinload

from app.models.blog import Post, PostMedia, PostLike, PostSave, Hashtag, PostHashtag


class BlogRepository:
    """Repository cho Blog - tất cả database operations"""
    
    # ==================== POST CRUD ====================
    @staticmethod
    def create_post(
        db: Session,
        user_id: uuid.UUID,
        content_text: str,
        title: Optional[str] = None
    ) -> Post:
        """Tạo post mới (chưa có media/hashtags)"""
        post = Post(
            user_id=user_id,
            title=title,
            content_text=content_text,
            like_count=0,
            save_count=0
        )
        db.add(post)
        db.flush()  # Để lấy post.id
        return post
    
    @staticmethod
    def get_post_by_id(
        db: Session,
        post_id: int,
        include_deleted: bool = False
    ) -> Optional[Post]:
        """Lấy post theo ID, kèm media và hashtags"""
        query = (
            select(Post)
            .options(
                selectinload(Post.media),
                selectinload(Post.hashtags)
            )
            .where(Post.id == post_id)
        )
        
        if not include_deleted:
            query = query.where(Post.deleted_at.is_(None))
        
        result = db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    def update_post(
        db: Session,
        post: Post,
        title: Optional[str] = None,
        content_text: Optional[str] = None
    ) -> Post:
        """Cập nhật nội dung post"""
        if title is not None:
            post.title = title
        if content_text is not None:
            post.content_text = content_text
        post.updated_at = datetime.now(timezone.utc)
        db.flush()
        return post
    
    @staticmethod
    def soft_delete_post(db: Session, post: Post) -> None:
        """Soft delete post"""
        post.deleted_at = datetime.now(timezone.utc)
        db.flush()
    
    # ==================== POST MEDIA ====================
    @staticmethod
    def add_media_to_post(
        db: Session,
        post_id: int,
        media_list: List[dict]
    ) -> List[PostMedia]:
        """Thêm media vào post"""
        result = []
        for idx, m in enumerate(media_list):
            media = PostMedia(
                post_id=post_id,
                url=m["url"],
                media_type=m["media_type"],
                mime_type=m.get("mime_type"),
                width=m.get("width"),
                height=m.get("height"),
                size_bytes=m.get("size_bytes"),
                sort_order=m.get("sort_order", idx)
            )
            db.add(media)
            result.append(media)
        db.flush()
        return result
    
    @staticmethod
    def delete_all_media_of_post(db: Session, post_id: int) -> None:
        """Xóa tất cả media của post"""
        db.execute(delete(PostMedia).where(PostMedia.post_id == post_id))
    
    # ==================== HASHTAGS ====================
    @staticmethod
    def get_or_create_hashtags(db: Session, names: List[str]) -> List[Hashtag]:
        """
        Lấy hoặc tạo hashtags theo tên.
        Tên được chuẩn hóa: lowercase, bỏ ký tự đặc biệt.
        """
        if not names:
            return []
        
        # Chuẩn hóa tên
        normalized = [BlogRepository._normalize_hashtag(n) for n in names]
        normalized = [n for n in normalized if n]  # Bỏ empty
        
        if not normalized:
            return []
        
        # Tìm existing
        existing = db.execute(
            select(Hashtag).where(Hashtag.name.in_(normalized))
        ).scalars().all()
        
        existing_names = {h.name for h in existing}
        
        # Tạo mới những chưa có
        new_hashtags = []
        for name in normalized:
            if name not in existing_names:
                h = Hashtag(name=name)
                db.add(h)
                new_hashtags.append(h)
        
        if new_hashtags:
            db.flush()
        
        return list(existing) + new_hashtags
    
    @staticmethod
    def _normalize_hashtag(name: str) -> str:
        """Chuẩn hóa hashtag: lowercase, chỉ giữ alphanumeric"""
        import re
        name = name.strip().lower()
        name = name.lstrip("#")  # Bỏ # nếu có
        name = re.sub(r"[^a-z0-9_]", "", name)
        return name[:50] if name else ""
    
    @staticmethod
    def set_post_hashtags(db: Session, post_id: int, hashtag_ids: List[int]) -> None:
        """Set hashtags cho post (xóa cũ, thêm mới)"""
        # Xóa cũ
        db.execute(delete(PostHashtag).where(PostHashtag.post_id == post_id))
        
        # Thêm mới
        for h_id in hashtag_ids:
            link = PostHashtag(post_id=post_id, hashtag_id=h_id)
            db.add(link)
        
        db.flush()
    
    @staticmethod
    def search_hashtags(db: Session, query: str, limit: int = 20) -> List[Hashtag]:
        """Tìm hashtags theo prefix"""
        normalized = BlogRepository._normalize_hashtag(query)
        if not normalized:
            return []
        
        result = db.execute(
            select(Hashtag)
            .where(Hashtag.name.ilike(f"{normalized}%"))
            .order_by(Hashtag.name)
            .limit(limit)
        )
        return result.scalars().all()
    
    @staticmethod
    def get_hashtag_by_name(db: Session, name: str) -> Optional[Hashtag]:
        """Lấy hashtag theo tên"""
        normalized = BlogRepository._normalize_hashtag(name)
        result = db.execute(select(Hashtag).where(Hashtag.name == normalized))
        return result.scalar_one_or_none()
    
    # ==================== LIKES ====================
    @staticmethod
    def add_like(db: Session, user_id: uuid.UUID, post_id: int) -> bool:
        """
        Thêm like. Trả về True nếu like mới, False nếu đã like.
        """
        # Check existing
        existing = db.execute(
            select(PostLike).where(
                PostLike.user_id == user_id,
                PostLike.post_id == post_id
            )
        ).scalar_one_or_none()
        
        if existing:
            return False
        
        like = PostLike(user_id=user_id, post_id=post_id)
        db.add(like)
        
        # Update counter
        db.execute(
            update(Post)
            .where(Post.id == post_id)
            .values(like_count=Post.like_count + 1)
        )
        
        db.flush()
        return True
    
    @staticmethod
    def remove_like(db: Session, user_id: uuid.UUID, post_id: int) -> bool:
        """
        Xóa like. Trả về True nếu xóa thành công, False nếu chưa like.
        """
        result = db.execute(
            delete(PostLike).where(
                PostLike.user_id == user_id,
                PostLike.post_id == post_id
            )
        )
        
        if result.rowcount > 0:
            # Update counter
            db.execute(
                update(Post)
                .where(Post.id == post_id)
                .values(like_count=func.greatest(Post.like_count - 1, 0))
            )
            db.flush()
            return True
        return False
    
    @staticmethod
    def is_liked(db: Session, user_id: uuid.UUID, post_id: int) -> bool:
        """Kiểm tra user đã like post chưa"""
        result = db.execute(
            select(PostLike).where(
                PostLike.user_id == user_id,
                PostLike.post_id == post_id
            )
        )
        return result.scalar_one_or_none() is not None
    
    # ==================== SAVES ====================
    @staticmethod
    def add_save(db: Session, user_id: uuid.UUID, post_id: int) -> bool:
        """Thêm save. Trả về True nếu save mới."""
        existing = db.execute(
            select(PostSave).where(
                PostSave.user_id == user_id,
                PostSave.post_id == post_id
            )
        ).scalar_one_or_none()
        
        if existing:
            return False
        
        save = PostSave(user_id=user_id, post_id=post_id)
        db.add(save)
        
        # Update counter
        db.execute(
            update(Post)
            .where(Post.id == post_id)
            .values(save_count=Post.save_count + 1)
        )
        
        db.flush()
        return True
    
    @staticmethod
    def remove_save(db: Session, user_id: uuid.UUID, post_id: int) -> bool:
        """Xóa save. Trả về True nếu xóa thành công."""
        result = db.execute(
            delete(PostSave).where(
                PostSave.user_id == user_id,
                PostSave.post_id == post_id
            )
        )
        
        if result.rowcount > 0:
            db.execute(
                update(Post)
                .where(Post.id == post_id)
                .values(save_count=func.greatest(Post.save_count - 1, 0))
            )
            db.flush()
            return True
        return False
    
    @staticmethod
    def is_saved(db: Session, user_id: uuid.UUID, post_id: int) -> bool:
        """Kiểm tra user đã save post chưa"""
        result = db.execute(
            select(PostSave).where(
                PostSave.user_id == user_id,
                PostSave.post_id == post_id
            )
        )
        return result.scalar_one_or_none() is not None
    
    # ==================== FEED QUERIES ====================
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
    ) -> Tuple[List[Post], int]:
        """
        Lấy feed với filters và offset/limit pagination.
        
        Args:
            sort: "recent" hoặc "trending"
            hashtag: Lọc theo hashtag name
            author_id: Lọc theo tác giả
            saved_only: Chỉ lấy bài đã save
            limit: Số lượng posts mỗi trang (mặc định 15)
            page: Số trang (bắt đầu từ 1)
        
        Returns:
            (posts, total_count) - danh sách posts và tổng số bài viết
        """
        # Base query cho đếm tổng
        base_query = select(Post).where(Post.deleted_at.is_(None))
        
        # Query lấy dữ liệu với eager loading
        query = (
            select(Post)
            .options(
                selectinload(Post.media),
                selectinload(Post.hashtags)
            )
            .where(Post.deleted_at.is_(None))
        )
        
        # Filter: hashtag
        if hashtag:
            normalized_hashtag = BlogRepository._normalize_hashtag(hashtag)
            query = query.join(PostHashtag).join(Hashtag).where(
                Hashtag.name == normalized_hashtag
            )
        
        # Filter: author
        if author_id:
            query = query.where(Post.user_id == author_id)
            base_query = base_query.where(Post.user_id == author_id)
        
        # Filter: saved only
        if saved_only:
            query = query.join(PostSave).where(PostSave.user_id == user_id)
            base_query = base_query.join(PostSave).where(PostSave.user_id == user_id)
        
        # Filter: hashtag (áp dụng cho cả count query)
        if hashtag:
            normalized_hashtag = BlogRepository._normalize_hashtag(hashtag)
            base_query = base_query.join(PostHashtag).join(Hashtag).where(
                Hashtag.name == normalized_hashtag
            )
        
        # Đếm tổng số bài viết (cho pagination info)
        count_query = select(func.count()).select_from(base_query.subquery())
        total_count = db.execute(count_query).scalar() or 0
        
        # Sorting - luôn áp dụng ORDER BY trước OFFSET/LIMIT
        if sort == "trending":
            # Trending: (like_count + save_count) DESC, sau đó created_at DESC
            score_expr = Post.like_count + Post.save_count
            query = query.order_by(score_expr.desc(), Post.created_at.desc(), Post.id.desc())
        else:
            # Recent: created_at DESC (mới nhất trước)
            query = query.order_by(Post.created_at.desc(), Post.id.desc())
        
        # Offset/Limit pagination
        # page=1 → offset=0, page=2 → offset=15, page=3 → offset=30...
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)
        
        result = db.execute(query)
        posts = result.scalars().all()
        
        return posts, total_count
    
    @staticmethod
    def get_user_interactions(
        db: Session,
        user_id: uuid.UUID,
        post_ids: List[int]
    ) -> Tuple[set, set]:
        """
        Lấy liked_ids và saved_ids của user cho list post_ids.
        Returns: (liked_ids_set, saved_ids_set)
        """
        if not post_ids:
            return set(), set()
        
        # Liked
        liked = db.execute(
            select(PostLike.post_id).where(
                PostLike.user_id == user_id,
                PostLike.post_id.in_(post_ids)
            )
        ).scalars().all()
        
        # Saved
        saved = db.execute(
            select(PostSave.post_id).where(
                PostSave.user_id == user_id,
                PostSave.post_id.in_(post_ids)
            )
        ).scalars().all()
        
        return set(liked), set(saved)
