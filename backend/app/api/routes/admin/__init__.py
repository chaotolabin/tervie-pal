"""
Admin Routes Package
"""
from fastapi import APIRouter
from .admin_support import router as support_router
from .admin_dashboard import router as dashboard_router
from .admin_users import router as users_router
from .admin_blog import router as blog_router
from .admin_contributions import router as contributions_router

router = APIRouter()

# Dashboard endpoints
router.include_router(dashboard_router, tags=["Admin Dashboard"])

# User management endpoints
router.include_router(users_router, tags=["Admin Users"])

# Blog management endpoints
router.include_router(blog_router, tags=["Admin Blog"])

# Support endpoints
router.include_router(support_router, prefix="/support", tags=["Admin Support"])

# Contributions endpoints
router.include_router(contributions_router, tags=["Admin Contributions"])