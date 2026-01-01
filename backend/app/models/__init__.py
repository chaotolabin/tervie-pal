# Import tất cả models để Alembic có thể tự động detect
# và để sử dụng trong các file khác

from app.models.base import Base, TimestampMixin

# Auth models
from app.models.auth import (
    User,
    Profile,
    RefreshSession,
    UserRole,
    Gender,
    Goal
)

# Password Reset models
from app.models.password_reset import PasswordResetToken

# Food models
from app.models.food import (
    Food,
    FoodPortion,
    FoodNutrient
)

# Exercise models
from app.models.exercise import Exercise

# Log models
from app.models.log import (
    MealType,
    FoodLogEntry,
    FoodLogItem,
    ExerciseLogEntry,
    ExerciseLogItem
)

# Biometric models
from app.models.biometric import BiometricsLog

# Support models
from app.models.support import (
    SupportTicket,
    TicketStatus
)

# Blog models
from app.models.blog import (
    Post,
    PostMedia,
    PostLike,
    PostSave,
    Hashtag,
    PostHashtag,
    MediaType
)

# Streak models
from app.models.streak import (
    StreakDayCache,
    StreakStatus
)

# Export all models
__all__ = [
    # Base
    "Base",
    "TimestampMixin",
    
    # Auth
    "User",
    "Profile",
    "RefreshSession",
    "UserRole",
    "Gender",
    "Goal",
    
    # Signup
    "SignupSession",
    
    # Food
    "Food",
    "FoodPortion",
    "FoodNutrient",
    
    # Exercise
    "Exercise",
    
    # Logs
    "MealType",
    "FoodLogEntry",
    "FoodLogItem",
    "ExerciseLogEntry",
    "ExerciseLogItem",
    
    # Biometric
    "BiometricsLog",
    
    # Support
    "SupportTicket",
    "TicketStatus",
    
    # Blog
    "Post",
    "PostMedia",
    "PostLike",
    "PostSave",
    "Hashtag",
    "PostHashtag",
    "MediaType",
    
    # Streak
    "StreakDayCache",
    "StreakStatus",
]