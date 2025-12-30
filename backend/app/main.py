from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.settings import settings
from app.core.database import get_db, engine

# import routes
from app.api.routes import auth, admin, users, meals, workouts, chatbot

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Tervie Pal API",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc"
)

# ==================== CORS Configuration ====================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Thay đổi thành specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Root Endpoints ====================
@app.get("/", tags=["Root"])
async def root():
    """Health check endpoint"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.PROJECT_VERSION,
        "status": "running"
    }


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


# ==================== Include API Routes ====================
app.include_router(auth.router, prefix="/api/v1")
# app.include_router(admin.router, prefix="/api/v1")
# app.include_router(users.router, prefix="/api/v1")
# app.include_router(meals.router, prefix="/api/v1")
# app.include_router(workouts.router, prefix="/api/v1")
# app.include_router(chatbot.router, prefix="/api/v1")