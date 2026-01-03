# Biometrics Repository
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.biometric import BiometricsLog
from datetime import datetime, timezone
import uuid


class BiometricsRepository:
    """Repository for BiometricsLog entity operations"""
    
    @staticmethod
    def create(
        db: Session, 
        user_id: uuid.UUID, 
        weight_kg: float, 
        height_cm: float, 
        bmi: float  # ✅ Thêm parameter BMI (đã tính sẵn từ Service)
    ) -> BiometricsLog:
        """Create biometrics log entry - BMI phải được tính sẵn từ Service"""
        biometric = BiometricsLog(
            user_id=user_id,
            logged_at=datetime.now(timezone.utc),
            weight_kg=weight_kg,
            height_cm=height_cm,
            bmi=bmi 
        )
        db.add(biometric)
        return biometric