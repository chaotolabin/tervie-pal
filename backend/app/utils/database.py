# Quan ly ket noi voi database
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.core.settings import settings

# BƯỚC 1: Tạo engine - đối tượng quản lý kết nối database
# pool_pre_ping=True: Kiểm tra kết nối trước khi sử dụng (tránh lỗi khi connection timeout)
# echo=True: In ra SQL queries (dùng khi debug, nên tắt ở production)
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=False  # Đổi thành True nếu muốn xem SQL queries
)

# BƯỚC 2: Tạo SessionLocal - factory để tạo database sessions
# autocommit=False: Không tự động commit, phải gọi session.commit() thủ công
# autoflush=False: Không tự động flush changes vào DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# BƯỚC 3: Tạo Base class cho các models
# Tất cả các models (User, Meal, Workout...) sẽ kế thừa từ Base này
Base = declarative_base()


# BƯỚC 4: Dependency function để inject database session vào routes
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
        yield db  # Trả session cho route handler
    finally:
        db.close()  # Đảm bảo luôn đóng session sau khi dùng xong