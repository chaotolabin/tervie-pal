from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.settings import settings
from app.core.database import get_db, engine

# import routes
from app.api.routes import auth, users, chatbot, biometric, food, exercise, logs, support, streak, goals, blog
from app.api.routes import settings as settings_routes
from app.api.routes.admin import router as admin_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Tervie Pal API"
    # openapi_url="/api/v1/openapi.json",
    # docs_url="/api/v1/docs"
)

# ==================== CORS Configuration ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Thay đổi thành specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(biometric.router, prefix="/api/v1")
app.include_router(food.router, prefix="/api/v1")
app.include_router(exercise.router, prefix="/api/v1")
app.include_router(logs.router, prefix="/api/v1/logs")
app.include_router(support.router, prefix="/api/v1/support")
app.include_router(admin_router, prefix="/api/v1/admin")
app.include_router(auth.router, prefix="/api/v1")
app.include_router(settings_routes.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(streak.router, prefix="/api/v1")
app.include_router(goals.router, prefix="/api/v1")
app.include_router(blog.router, prefix="/api/v1")

# Root endpoint: dung de kiem tra tinh trang hoat dong cua he thong
@app.get("/", tags=["Root"])    # http://127.0.0.1:8000/, tags: phan loai endpoint
async def root():
    """Health check endpoint"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.PROJECT_VERSION,
        "status": "running"
    }


# Health check endpoint: kiem tra ket noi database
@app.get("/health", tags=["Root"])
async def health_check(db: Session = Depends(get_db)):
    """
    Kiem tra ket noi database.
    
    - db: Session = Depends(get_db) nghia la:
      + FastAPI se tu dong goi get_db() de tao session
      + Truyen session vao tham so db
      + Tu dong dong session sau khi xu ly xong
    """
    try:
        # Thuc hien query don gian de test connection
        # text() bat buoc trong SQLAlchemy 2.0+ khi dung raw SQL
        db.execute(text("SELECT 1"))
        return JSONResponse(
            status_code=200,
            content={
                "status": "healthy", 
                "database": "connected",
                "message": "Database connection successful"
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )