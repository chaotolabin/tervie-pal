# Quan ly ket noi voi database
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.settings import settings

# Tao engine - doi tuong quan ly ket noi database
# pool_pre_ping=True: Kiem tra ket noi truoc khi su dung (tranh loi khi connection timeout)
# echo=True: In ra SQL queries (dung khi debug, nen tat o production)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False  # Khong in SQL queries
)

# Tao SessionLocal - factory de tao database sessions, moi request se co 1 session rieng (phien lam viec voi dbs)
# autocommit=False: Khong tu dong commit, phai goi session.commit() thu cong
# autoflush=False: Khong tu dong flush changes vao DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tao Base class cho cac models
# Tat ca cac models (User, Meal, Workout...) se ke thua tu Base nay
Base = declarative_base()


# Dependency function de inject database session vao routes
def get_db():
    """
    Hàm này sẽ được dùng trong FastAPI dependencies.
    
    Cách hoạt động:
    1. Tạo một database session mới
    2. Yield session đó cho route handler sử dụng
    3. Sau khi route xử lý xong, tự động đóng session (cleanup)
    
    Ví dụ sử dụng:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db  # tra session cho route handler
    finally:
        db.close()  # Dam bao luon dong session sau khi dung xong