# Schemas initialization - export all schemas for convenient importing
from .auth import (
    RegisterRequest,
    LoginRequest,
    RefreshRequest,
    LogoutRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    UserPublic,
    AuthTokensResponse,
    RefreshResponse,
)
from .users import (
    Profile,
    ProfilePatchRequest,
    UserMeResponse,
    Session,
    SessionsListResponse,
    UserRolePatchRequest,
)
from .settings import ChangePasswordRequest
from .common import ErrorResponse, GenericMessageResponse
from .streak import StreakStatus, StreakDayResponse, StreakResponse, StreakWeekResponse
from .goals import (
    GoalType,
    ActivityLevel,
    GoalCreateRequest,
    GoalPatchRequest,
    GoalResponse,
    GoalCalculateRequest,
    GoalCalculateResponse,
)
from .biometric import (
    BiometricsCreateRequest,
    BiometricsPatchRequest,
    BiometricsLogResponse,
    BiometricsListResponse,
)
from .blog import (
    MediaType,
    FeedSort,
    PostMediaIn,
    PostMediaOut,
    PostCreateRequest,
    PostPatchRequest,
    PostDetail,
    FeedItem,
    FeedResponse,
    HashtagOut,
    HashtagSearchResponse,
    FeedQueryParams,
)
from .admin import (
    AdminDashboardStatsResponse,
    AdminSimpleDashboardResponse,
    UserStatsResponse,
    LogStatsResponse,
    RetentionMetricsResponse,
    BlogStatsResponse,
    StreakStatsResponse,
    AdminUserListResponse,
    AdminUserDetailResponse,
    UserRolePatchRequest as AdminUserRolePatchRequest,
    StreakAdjustRequest,
    AdminPostListResponse,
    PostDeleteRequest,
    AdminActionResponse,
)

__all__ = [
    # Auth schemas
    "RegisterRequest",
    "LoginRequest",
    "RefreshRequest",
    "LogoutRequest",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "UserPublic",
    "AuthTokensResponse",
    "RefreshResponse",

    # User schemas
    "Profile",
    "ProfilePatchRequest",
    "UserMeResponse",
    "Session",
    "SessionsListResponse",
    "UserRolePatchRequest",

    # Settings schemas
    "ChangePasswordRequest",

    # Common schemas
    "ErrorResponse",
    "GenericMessageResponse",

    # Streak schemas
    "StreakStatus",
    "StreakDayResponse",
    "StreakResponse",
    "StreakWeekResponse",

    # Goals schemas
    "GoalType",
    "ActivityLevel",
    "GoalCreateRequest",
    "GoalPatchRequest",
    "GoalResponse",
    "GoalCalculateRequest",
    "GoalCalculateResponse",

    # Biometric schemas
    "BiometricsCreateRequest",
    "BiometricsPatchRequest",
    "BiometricsLogResponse",
    "BiometricsListResponse",

    # Blog schemas
    "MediaType",
    "FeedSort",
    "PostMediaIn",
    "PostMediaOut",
    "PostCreateRequest",
    "PostPatchRequest",
    "PostDetail",
    "FeedItem",
    "FeedResponse",
    "HashtagOut",
    "HashtagSearchResponse",
    "FeedQueryParams",

    # Admin schemas
    "AdminDashboardStatsResponse",
    "AdminSimpleDashboardResponse",
    "UserStatsResponse",
    "LogStatsResponse",
    "RetentionMetricsResponse",
    "BlogStatsResponse",
    "StreakStatsResponse",
    "AdminUserListResponse",
    "AdminUserDetailResponse",
    "AdminUserRolePatchRequest",
    "StreakAdjustRequest",
    "AdminPostListResponse",
    "PostDeleteRequest",
    "AdminActionResponse",
]
