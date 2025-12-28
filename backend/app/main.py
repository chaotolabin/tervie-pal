from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.utils.database import get_db, engine

# import routes
from app.api.routes import auth, admin, users, meals, workouts, chatbot

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Tervie Pal API"
)

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
    Kiem tra tinh trang he thong va ket noi database.
    
    - db: Session = Depends(get_db) nghia la:
      + FastAPI se tu dong goi get_db() de tao session
      + Truyen session vao tham so db
      + Tu dong dong session sau khi xu ly xong
    """
    try:
        # Thực hiện query đơn giản để test connection
        db.execute("SELECT 1")
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