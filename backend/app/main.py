from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.settings import settings

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


# @app.get("/health", tags=["Root"])
# async def health_check():
#     """System health check"""
#     # need to add more detailed health checks (e.g., database connectivity)
#     return JSONResponse(
#         status_code=200,
#         content={"status": "healthy", "database": "connected"}
#     )