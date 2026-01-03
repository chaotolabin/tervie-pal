"""
Media Service - Xử lý upload media lên ImageKit.
Hỗ trợ upload ảnh/video cho Blog module.
Compatible với imagekitio SDK v5.0.0
"""
import os
import uuid
import tempfile
from typing import Optional, List

from fastapi import UploadFile, HTTPException, status
from imagekitio import ImageKit

from app.core.settings import settings


class MediaService:
    """Service xử lý upload media lên ImageKit"""
    
    # Các định dạng file được phép
    ALLOWED_IMAGE_TYPES = {
        "image/jpeg": ".jpg",
        "image/png": ".png", 
        "image/gif": ".gif",
        "image/webp": ".webp"
    }
    
    ALLOWED_VIDEO_TYPES = {
        "video/mp4": ".mp4",
        "video/quicktime": ".mov",
        "video/x-msvideo": ".avi",
        "video/webm": ".webm"
    }
    
    # Giới hạn kích thước file (bytes)
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB
    
    _imagekit: Optional[ImageKit] = None
    
    @classmethod
    def _get_imagekit(cls) -> ImageKit:
        """Lazy initialization của ImageKit client (SDK v5.0.0)"""
        if cls._imagekit is None:
            if not settings.IMAGEKIT_PRIVATE_KEY:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="ImageKit configuration is not set up"
                )
            
            # SDK v5.0.0 chỉ cần private_key
            cls._imagekit = ImageKit(
                private_key=settings.IMAGEKIT_PRIVATE_KEY
            )
        return cls._imagekit
    
    @staticmethod
    def _validate_file(file: UploadFile) -> tuple[str, str]:
        """
        Validate file upload.
        Returns: (media_type, extension)
        Raises: HTTPException nếu file không hợp lệ
        """
        content_type = file.content_type or ""
        
        # Check image types
        if content_type in MediaService.ALLOWED_IMAGE_TYPES:
            return "image", MediaService.ALLOWED_IMAGE_TYPES[content_type]
        
        # Check video types
        if content_type in MediaService.ALLOWED_VIDEO_TYPES:
            return "video", MediaService.ALLOWED_VIDEO_TYPES[content_type]
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {content_type}. "
                   f"Allowed: {list(MediaService.ALLOWED_IMAGE_TYPES.keys()) + list(MediaService.ALLOWED_VIDEO_TYPES.keys())}"
        )
    
    @classmethod
    def _check_file_size(cls, file: UploadFile, media_type: str) -> None:
        """
        Kiểm tra kích thước file TRƯỚC khi đọc vào memory.
        Sử dụng file.size (từ Content-Length header).
        
        Args:
            file: UploadFile từ request
            media_type: "image" hoặc "video"
        """
        max_size = cls.MAX_IMAGE_SIZE if media_type == "image" else cls.MAX_VIDEO_SIZE
        
        if file.size is not None and file.size > max_size:
            max_mb = max_size / (1024 * 1024)
            file_mb = file.size / (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum for {media_type}: {max_mb:.0f}MB. Your file: {file_mb:.2f}MB"
            )
    
    @classmethod
    async def upload_file(
        cls,
        file: UploadFile,
        user_id: uuid.UUID,
        folder: str = "blog"
    ) -> dict:
        """
        Upload file lên ImageKit.
        
        Args:
            file: File từ request
            user_id: UUID của user upload
            folder: Thư mục trên ImageKit (mặc định: blog)
            
        Returns:
            dict với thông tin file: url, file_id, media_type, mime_type, width, height, size_bytes
        """
        temp_file_path = None
        
        try:
            # 1. Validate file type
            media_type, extension = cls._validate_file(file)
            
            # 2. CHECK KÍCH THƯỚC TRƯỚC (từ header - không cần đọc file)
            cls._check_file_size(file, media_type)
            
            # 3. Get original filename
            original_filename = file.filename or f"upload{extension}"
            
            # 4. Xác định giới hạn size dựa trên media type
            max_size = cls.MAX_IMAGE_SIZE if media_type == "image" else cls.MAX_VIDEO_SIZE
            
            # 5. Đọc file theo chunks để an toàn với memory
            contents = bytearray()
            chunk_size = 1024 * 1024  # 1MB per chunk
            
            while True:
                chunk = await file.read(chunk_size)
                if not chunk:
                    break
                contents.extend(chunk)
                
                # Double-check kích thước trong khi đọc (phòng trường hợp header sai)
                if len(contents) > max_size:
                    max_mb = max_size / (1024 * 1024)
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail=f"File too large. Maximum for {media_type}: {max_mb:.0f}MB"
                    )
            
            size_bytes = len(contents)
            
            # 6. Lưu vào temp file (ImageKit SDK cần file path hoặc file object)
            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=extension
            ) as temp_file:
                temp_file_path = temp_file.name
                temp_file.write(contents)  # Ghi bytes trực tiếp
            
            # 7. Upload lên ImageKit (SDK v5.0.0 API)
            imagekit = cls._get_imagekit()
            
            # Tạo tên file unique
            unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
            
            # Mở temp file để upload
            with open(temp_file_path, "rb") as f:
                # SDK v5.0.0: sử dụng ik.files.upload()
                upload_result = imagekit.files.upload(
                    file=f,
                    file_name=unique_filename,
                    folder=f"/{folder}/{str(user_id)}",
                    tags=["blog-upload", str(user_id)],
                    use_unique_file_name=True
                )
            
            # 8. Trả về kết quả
            # SDK v5.0.0 trả về object với các attributes
            return {
                "url": upload_result.url,
                "file_id": upload_result.file_id,
                "file_name": upload_result.name,
                "media_type": media_type,
                "mime_type": file.content_type,
                "width": getattr(upload_result, 'width', None),
                "height": getattr(upload_result, 'height', None),
                "size_bytes": size_bytes,
                "sort_order": 0
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Upload failed: {str(e)}"
            )
        finally:
            # Xóa temp file sau khi upload xong
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    @classmethod
    async def upload_multiple_files(
        cls,
        files: List[UploadFile],
        user_id: uuid.UUID,
        folder: str = "blog"
    ) -> List[dict]:
        """
        Upload nhiều files lên ImageKit.
        
        Args:
            files: Danh sách files từ request
            user_id: UUID của user upload
            folder: Thư mục trên ImageKit
            
        Returns:
            List các dict với thông tin từng file
        """
        if len(files) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 files allowed per upload"
            )
        
        results = []
        for idx, file in enumerate(files):
            result = await cls.upload_file(file, user_id, folder)
            result["sort_order"] = idx
            results.append(result)
        
        return results
    
    @classmethod
    def delete_file(cls, file_id: str) -> bool:
        """
        Xóa file từ ImageKit (optional, dùng khi xóa post).
        
        Args:
            file_id: ImageKit file ID
            
        Returns:
            True nếu xóa thành công
        """
        try:
            imagekit = cls._get_imagekit()
            # SDK v5.0.0: sử dụng ik.files.delete()
            imagekit.files.delete(file_id)
            return True
        except Exception:
            # Log error nhưng không throw - file có thể đã bị xóa
            return False