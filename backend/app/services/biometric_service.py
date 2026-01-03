"""
Service Layer cho Biometrics Module
Chịu trách nhiệm:
- CRUD operations với database
- Business logic (tính BMI, validation)
- Error handling
- Trigger goal recalculation when biometrics change
"""
import uuid
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.biometric import BiometricsLog
from app.schemas.biometric import (
    BiometricsCreateRequest,
    BiometricsPatchRequest,
    BiometricsLogResponse
)


class BiometricService:
    """Service xử lý nghiệp vụ Biometrics"""

    @staticmethod
    def calculate_bmi(weight_kg: float, height_cm: float) -> float:
        """
        Tính chỉ số BMI (Body Mass Index)
        Công thức: BMI = weight(kg) / (height(m))^2
        
        Args:
            weight_kg: Cân nặng tính bằng kg
            height_cm: Chiều cao tính bằng cm
        
        Returns:
            float: Chỉ số BMI (làm tròn 2 chữ số thập phân)
        
        Raises:
            ValueError: Nếu weight hoặc height <= 0
        """
        if weight_kg <= 0 or height_cm <= 0:
            raise ValueError("Cân nặng và chiều cao phải lớn hơn 0")
        
        # Convert cm sang meters
        height_m = height_cm / 100
        bmi = weight_kg / (height_m ** 2)
        
        return round(bmi, 2)

    @staticmethod
    def _try_recalculate_goal(db: Session, user_id: uuid.UUID) -> None:
        """
        Thử recalculate goal nếu user đã có goal.
        Gọi silent - không raise error nếu không có goal.
        
        Args:
            db: Database session
            user_id: User UUID
        """
        try:
            from app.services.goal_service import GoalService
            
            # Kiểm tra xem user có goal không
            existing_goal = GoalService.get_goal(db, user_id)
            if existing_goal:
                # Recalculate với các giá trị hiện tại
                GoalService.recalculate_goal(
                    db=db,
                    user_id=user_id,
                    commit=False  # Sẽ commit cùng với biometrics
                )
        except HTTPException:
            # Ignore errors (e.g., missing profile data)
            # Goal sẽ được recalculate khi user có đủ data
            pass
        except Exception:
            # Log error but don't fail biometrics operation
            pass

    @staticmethod
    def create_biometrics_log(
        db: Session,
        user_id: uuid.UUID, 
        data: BiometricsCreateRequest
    ) -> BiometricsLog:
        """
        Tạo một biometrics log mới
        
        Args:
            db: Database session
            user_id: UUID của user hiện tại
            data: Dữ liệu từ request
        
        Returns:
            BiometricsLog: Record vừa tạo

        Rules: Mỗi user chỉ được tạo một log cho mỗi thời điểm logged_at.
        Nếu đã có log cho thời điểm đó, trả về lỗi 400.

        Side Effects:
        - Nếu user có goal, goal sẽ được recalculate với weight/height mới
        """
        # Tính BMI tự động
        bmi = BiometricService.calculate_bmi(data.weight_kg, data.height_cm)
        
        # Kiểm tra nếu đã có log cho user và logged_at này
        existing_query = select(BiometricsLog).where(
            and_(
                BiometricsLog.user_id == user_id,
                BiometricsLog.logged_at == data.logged_at
            )
        )
        
        # scalar_one_or_none() trả về None nếu không có record nào
        existing_log = db.execute(existing_query).scalar_one_or_none()
        
        if existing_log:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Biometrics log at this time already exists. Use PATCH to update."
            )

        # Tạo record mới
        db_log = BiometricsLog(
            user_id=user_id,
            logged_at=data.logged_at,
            weight_kg=data.weight_kg,
            height_cm=data.height_cm,
            bmi=bmi
        )
        
        db.add(db_log)

        # Recalculate goal nếu có (với biometrics mới nhất)
        BiometricService._try_recalculate_goal(db, user_id)

        db.commit()
        db.refresh(db_log)
        
        return db_log

    @staticmethod
    def get_biometrics_logs(
        db: Session,
        user_id: uuid.UUID,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        limit: int = 100
    ) -> List[BiometricsLog]:
        """
        Lấy danh sách biometrics logs trong khoảng thời gian
        
        Args:
            db: Database session
            user_id: UUID của user
            from_date: Ngày bắt đầu (inclusive)
            to_date: Ngày kết thúc (inclusive)
            limit: Số lượng record tối đa (default 100, max 365)
        
        Returns:
            List[BiometricsLog]: Danh sách logs, sắp xếp theo logged_at DESC
        """
        # Build query
        query = select(BiometricsLog).where(BiometricsLog.user_id == user_id)
        
        # Filter theo date range nếu có
        if from_date:
            # So sánh DATE của logged_at với from_date
            query = query.where(
                and_(BiometricsLog.logged_at >= datetime.combine(from_date, datetime.min.time()))
            )
        
        if to_date:
            # To date inclusive (đến 23:59:59 của ngày đó)
            query = query.where(
                and_(BiometricsLog.logged_at < datetime.combine(
                    to_date, datetime.max.time()
                ))
            )
        
        # Sắp xếp và limit
        query = query.order_by(desc(BiometricsLog.logged_at)).limit(min(limit, 365))
        
        result = db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    def get_latest_biometrics(
        db: Session,
        user_id: uuid.UUID
    ) -> Optional[BiometricsLog]:
        """
        Lấy biometrics log mới nhất của user
        
        Args:
            db: Database session
            user_id: UUID của user
        
        Returns:
            BiometricsLog | None: Log mới nhất hoặc None nếu chưa có log nào
        """
        query = (
            select(BiometricsLog)
            .where(BiometricsLog.user_id == user_id)
            .order_by(desc(BiometricsLog.logged_at))
            .limit(1)
        )
        
        result = db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    def get_biometrics_by_id(
        db: Session,
        biometric_id: int,
        user_id: uuid.UUID
    ) -> BiometricsLog:
        """
        Lấy một biometrics log theo ID
        
        Args:
            db: Database session
            biometric_id: ID của log
            user_id: UUID của user (để verify ownership)
        
        Returns:
            BiometricsLog: Log được tìm thấy
        
        Raises:
            HTTPException 404: Nếu không tìm thấy hoặc không thuộc về user
        """
        query = select(BiometricsLog).where(
            and_(
                BiometricsLog.id == biometric_id,
                BiometricsLog.user_id == user_id
            )
        )
        
        result = db.execute(query)
        db_log = result.scalar_one_or_none()
        
        if not db_log:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Biometrics log with id {biometric_id} not found"
            )
        
        return db_log

    @staticmethod
    def update_biometrics_log(
        db: Session,
        biometric_id: int,
        user_id: uuid.UUID,
        data: BiometricsPatchRequest
    ) -> BiometricsLog:
        """
        Cập nhật một biometrics log
        
        Args:
            db: Database session
            biometric_id: ID của log cần update
            user_id: UUID của user
            data: Dữ liệu cần update (partial)
        
        Returns:
            BiometricsLog: Log sau khi update
        
        Raises:
            HTTPException 404: Nếu không tìm thấy
        """
        # Lấy log hiện tại
        db_log = BiometricService.get_biometrics_by_id(db, biometric_id, user_id)
        
        # Update các fields được cung cấp
        update_data = data.model_dump(exclude_unset=True)  # Chỉ lấy fields không None
        
        for field, value in update_data.items():
            setattr(db_log, field, value)
        
        # Recalculate BMI nếu weight hoặc height thay đổi
        needs_goal_recalc = False
        if 'weight_kg' in update_data or 'height_cm' in update_data:
            db_log.bmi = BiometricService.calculate_bmi(
                db_log.weight_kg,
                db_log.height_cm
            )
            needs_goal_recalc = True
        
        # Recalculate goal nếu biometrics thay đổi
        if needs_goal_recalc:
            BiometricService._try_recalculate_goal(db, user_id)
        
        db.commit()
        db.refresh(db_log)
        
        return db_log

    @staticmethod
    def delete_biometrics_log(
        db: Session,
        biometric_id: int,
        user_id: uuid.UUID
    ) -> None:
        """
        Xóa một biometrics log (hard delete)
        
        Args:
            db: Database session
            biometric_id: ID của log cần xóa
            user_id: UUID của user
        
        Raises:
            HTTPException 404: Nếu không tìm thấy
        """
        db_log = BiometricService.get_biometrics_by_id(db, biometric_id, user_id)
        
        db.delete(db_log)
        db.commit()

    @staticmethod
    def get_summary(db, user_id, from_date, to_date):
        """
        Lấy tóm tắt biometrics trong khoảng thời gian
        """
        logs = (
            db.query(BiometricsLog)
            .filter(
                BiometricsLog.user_id == user_id,
                func.date(BiometricsLog.logged_at) >= from_date,
                func.date(BiometricsLog.logged_at) <= to_date,
            )
            .order_by(BiometricsLog.logged_at)
            .all()
        )

        if not logs:
            return {
                "height_change": 0,
                "weight_change": 0,
                "avg_bmi": None
            }

        height_change = logs[-1].height_cm - logs[0].height_cm
        weight_change = logs[-1].weight_kg - logs[0].weight_kg
        avg_bmi = sum(l.bmi for l in logs if l.bmi) / len(logs)

        return {
            "height_change": round(height_change, 2),
            "weight_change": round(weight_change, 2),
            "avg_bmi": round(avg_bmi, 2)
        }