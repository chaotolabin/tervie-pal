"""
Admin Routes Package
"""
from fastapi import APIRouter
from .admin_support import router as support_router

router = APIRouter()
router.include_router(support_router, prefix="/support", tags=["Admin"])