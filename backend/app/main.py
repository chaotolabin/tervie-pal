from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.settings import settings
from app.core.database import get_db, engine

# ==================== Import Routes ====================
from app.api.routes import (
    auth,
    users,
    chatbot,
    biometric,
    food,
    exercise,
    logs,
    support,
    streak,
    goals,
    blog,
)
from app.api.routes import settings as settings_routes
from app.api.routes.admin import router as admin_router

# ==================== App Init ====================
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Tervie Pal API",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
)

# ==================== CORS Configuration ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Register Routers ====================
app.include_router(auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(settings_routes.router, prefix="/api/v1")

app.include_router(biometric.router, prefix="/api/v1")
app.include_router(food.router, prefix="/api/v1")
app.include_router(exercise.router, prefix="/api/v1")
app.include_router(goals.router, prefix="/api/v1")
app.include_router(streak.router, prefix="/api/v1")

app.include_router(logs.router, prefix="/api/v1/logs")
app.include_router(support.router, prefix="/api/v1/support")

app.include_router(chatbot.router, prefix="/api/v1")  # ✅ giữ chatbot
app.include_router(blog.router, prefix="/api/v1")     # ✅ giữ blog

app.include_router(admin_router, prefix="/api/v1/admin")

# ==================== Root ====================
@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.PROJECT_VERSION,
        "status": "running",
    }

# ==================== Health Check ====================
@app.get("/health", tags=["Root"])
async def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy",
                "database": "connected",
                "message": "Database connection successful",
            },
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
            },
        )
