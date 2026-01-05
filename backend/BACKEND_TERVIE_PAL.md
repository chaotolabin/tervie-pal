# TÀI LIỆU KỸ THUẬT DỰ ÁN TERVIE PAL BACKEND

---

## PHẦN 1: TỔNG QUAN DỰ ÁN

### 1.1. Giới thiệu dự án

**Tervie Pal** là một ứng dụng theo dõi sức khỏe và thể hình toàn diện (Health & Fitness Tracking Application), được thiết kế để giúp người dùng quản lý và đạt được các mục tiêu sức khỏe cá nhân của họ một cách khoa học và hiệu quả. Backend của ứng dụng được xây dựng trên nền tảng FastAPI (Python) kết hợp với cơ sở dữ liệu PostgreSQL, cung cấp các API RESTful mạnh mẽ cho các ứng dụng client (web, mobile).

### 1.2. Mục đích và phạm vi

Dự án Tervie Pal Backend được phát triển với các mục đích chính sau:

**A. Theo dõi dinh dưỡng hàng ngày**
- Ghi nhận và phân tích lượng calories tiêu thụ qua các bữa ăn
- Theo dõi chi tiết các chất dinh dưỡng chính: Protein, Carbohydrates, Fat
- Tính toán tự động thông tin dinh dưỡng dựa trên khối lượng thực phẩm
- Lưu trữ lịch sử nhật ký ăn uống để phân tích xu hướng

**B. Quản lý mục tiêu sức khỏe cá nhân**
- Hỗ trợ nhiều loại mục tiêu: giảm cân, tăng cân, duy trì cân nặng, tăng cơ, cải thiện sức khỏe
- Tính toán mục tiêu calories hàng ngày dựa trên đặc điểm sinh học cá nhân
- Đề xuất tỷ lệ macro nutrients phù hợp với từng mục tiêu
- Theo dõi tiến trình đạt được mục tiêu theo thời gian

**C. Tính toán khoa học các chỉ số sinh học**
- Áp dụng công thức Mifflin-St Jeor để tính BMR (Basal Metabolic Rate)
- Tính toán TDEE (Total Daily Energy Expenditure) dựa trên mức độ hoạt động
- Tự động điều chỉnh calorie deficit/surplus phù hợp với mục tiêu và tốc độ thay đổi cân nặng mong muốn
- Tính toán chỉ số BMI và các metrics sinh học khác

**D. Trợ lý AI tư vấn dinh dưỡng**
- Tích hợp chatbot thông minh sử dụng Google Gemini AI
- Cung cấp thông tin dinh dưỡng chi tiết về các loại thực phẩm
- Đưa ra gợi ý món ăn phù hợp với mục tiêu cá nhân
- Tư vấn kế hoạch ăn uống và luyện tập
- Hỗ trợ tìm kiếm thông tin dinh dưỡng thông qua RAG (Retrieval-Augmented Generation)

**E. Hệ thống cộng đồng và chia sẻ**
- Nền tảng blog/social feed để người dùng chia sẻ hành trình
- Tương tác qua like, save, comment trên các bài viết
- Hashtag system để tổ chức và tìm kiếm nội dung
- Khuyến khích động lực thông qua cộng đồng

**F. Gamification - Hệ thống Streak**
- Theo dõi chuỗi ngày liên tục đạt mục tiêu
- Tạo động lực duy trì thói quen ghi nhật ký
- Thống kê và hiển thị thành tích cá nhân
- Phân loại trạng thái hoàn thành theo màu (green, yellow)

### 1.3. Đối tượng người dùng

**Người dùng cuối (End Users):**
- Người muốn giảm cân/tăng cân một cách khoa học
- Người tập gym muốn theo dõi macro cho muscle building
- Người quan tâm đến sức khỏe và dinh dưỡng
- Vận động viên cần kiểm soát chế độ ăn
- Người muốn xây dựng thói quen ăn uống lành mạnh

**Quản trị viên (Administrators):**
- Quản lý và giám sát hoạt động của hệ thống
- Kiểm duyệt nội dung blog và đóng góp từ người dùng
- Phân tích thống kê và hành vi người dùng
- Quản lý dữ liệu thực phẩm và bài tập global

---

## PHẦN 2: KIẾN TRÚC DỰ ÁN

### 2.1. Tổng quan kiến trúc

Tervie Pal Backend được xây dựng theo mô hình **Layered Architecture** (Kiến trúc phân tầng) với 4 tầng chính, đảm bảo tính separation of concerns, dễ bảo trì và mở rộng:

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT APPLICATIONS                      │
│              (Web App, iOS App, Android App)                 │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/HTTPS
                           │ REST API
┌──────────────────────────┴──────────────────────────────────┐
│                    API LAYER (Routes)                        │
│  - Request validation (Pydantic schemas)                     │
│  - Response formatting                                       │
│  - Authentication & Authorization (JWT)                      │
│  - HTTP status codes handling                                │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                  SERVICE LAYER (Business Logic)              │
│  - Core business rules                                       │
│  - Calculations (BMR, TDEE, macros)                         │
│  - Data orchestration                                        │
│  - Transaction management                                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│               REPOSITORY LAYER (Data Access)                 │
│  - Database queries                                          │
│  - CRUD operations                                           │
│  - Data mapping                                              │
│  - Query optimization                                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                    MODEL LAYER (ORM Models)                  │
│  - Database schema definition                                │
│  - Table relationships                                       │
│  - Constraints and indexes                                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│                   POSTGRESQL DATABASE                        │
│  - Data persistence                                          │
│  - Relational integrity                                      │
│  - Transaction support                                       │
└──────────────────────────────────────────────────────────────┘
```

### 2.2. Chi tiết các tầng

#### 2.2.1. API Layer (Tầng HTTP/Routing)

**Vị trí:** `app/api/routes/`

**Trách nhiệm:**
- Tiếp nhận và xử lý HTTP requests từ client
- Validation dữ liệu đầu vào thông qua Pydantic schemas
- Thực hiện authentication và authorization
- Gọi Service Layer để xử lý business logic
- Format dữ liệu trả về cho client (response serialization)
- Xử lý HTTP status codes và error responses

**Đặc điểm:**
- Thin layer: Chỉ chứa logic liên quan đến HTTP, không chứa business logic
- Type-safe: Sử dụng Pydantic models cho request/response
- Dependency Injection: Sử dụng FastAPI Dependencies để inject database session, current user
- OpenAPI/Swagger: Tự động generate API documentation

**Ví dụ cấu trúc:**
```python
# app/api/routes/food.py
@router.post("/foods", response_model=FoodDetail)
def create_food(
    data: FoodCreateRequest,                    # Request validation
    db: Session = Depends(get_db),              # Database injection
    current_user: User = Depends(get_current_user)  # Auth injection
) -> FoodDetail:
    """Thin layer - delegate to service"""
    food = FoodService.create_food(db, current_user.id, data)
    return FoodDetail.model_validate(food)
```

#### 2.2.2. Service Layer (Tầng Business Logic)

**Vị trí:** `app/services/`

**Trách nhiệm:**
- Chứa toàn bộ business logic và business rules
- Thực hiện các tính toán phức tạp (BMR, TDEE, macros, calories)
- Orchestrate multiple repositories để hoàn thành một use case
- Transaction management (commit/rollback)
- Validation logic phức tạp vượt quá schema validation
- Error handling và business exceptions

**Đặc điểm:**
- Framework-agnostic: Không phụ thuộc vào FastAPI
- Testable: Dễ dàng unit test mà không cần HTTP context
- Reusable: Có thể được gọi từ nhiều routes khác nhau
- Pure Python: Không có SQL trực tiếp, sử dụng repositories

**Ví dụ cấu trúc:**
```python
# app/services/goal_service.py
class GoalService:
    @staticmethod
    def calculate_bmr(weight_kg, height_cm, gender, date_of_birth):
        """Business logic: BMR calculation"""
        age = calculate_age(date_of_birth)
        if gender == "male":
            return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    
    @staticmethod
    def create_or_update_goal(db, user_id, data):
        """Orchestrate multiple operations"""
        # 1. Get latest biometrics
        biometrics = BiometricsRepository.get_latest(db, user_id)
        # 2. Get profile
        profile = ProfileRepository.get_by_user_id(db, user_id)
        # 3. Calculate values
        bmr = GoalService.calculate_bmr(...)
        tdee = GoalService.calculate_tdee(bmr, data.baseline_activity)
        daily_calorie = GoalService.calculate_daily_calorie(tdee, data.goal_type)
        # 4. Save to database
        goal = GoalRepository.upsert(db, user_id, ...)
        db.commit()
        return goal
```

#### 2.2.3. Repository Layer (Tầng Data Access)

**Vị trí:** `app/repositories/`

**Trách nhiệm:**
- Thực hiện các truy vấn database (CRUD operations)
- Encapsulate SQLAlchemy queries
- Mapping giữa database rows và model objects
- Query optimization và indexing awareness
- Không chứa business logic

**Đặc điểm:**
- Pure data access: Chỉ chứa SQL/ORM queries
- Stateless: Không lưu state, nhận db session từ caller
- Focused: Mỗi repository phục vụ một entity chính
- Chainable: Có thể combine nhiều repository calls trong service

**Ví dụ cấu trúc:**
```python
# app/repositories/user_repository.py
class UserRepository:
    @staticmethod
    def get_by_id(db: Session, user_id: UUID) -> User | None:
        """Simple query - get by primary key"""
        return db.execute(
            select(User).where(User.id == user_id)
        ).scalar_one_or_none()
    
    @staticmethod
    def get_by_email(db: Session, email: str) -> User | None:
        """Query with filter"""
        return db.execute(
            select(User).where(User.email == email)
        ).scalar_one_or_none()
    
    @staticmethod
    def create(db: Session, **kwargs) -> User:
        """Create new record"""
        user = User(**kwargs)
        db.add(user)
        return user
```

#### 2.2.4. Model Layer (Tầng Database Schema)

**Vị trí:** `app/models/`

**Trách nhiệm:**
- Định nghĩa database schema sử dụng SQLAlchemy ORM
- Khai báo tables, columns, data types
- Thiết lập relationships giữa các tables
- Định nghĩa constraints, indexes, foreign keys
- Mapping Python classes ↔ Database tables

**Đặc điểm:**
- Declarative style: Sử dụng SQLAlchemy 2.0 Mapped syntax
- Type-annotated: Rõ ràng về kiểu dữ liệu
- Relationship-aware: Lazy loading, eager loading configuration
- Migration-ready: Alembic detect changes automatically

**Ví dụ cấu trúc:**
```python
# app/models/food.py
class Food(Base, TimestampMixin):
    __tablename__ = "foods"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    owner_user_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True), 
        nullable=True,
        comment="NULL = global, has value = user custom"
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    
    # Relationships
    portions: Mapped[List["FoodPortion"]] = relationship(
        "FoodPortion",
        back_populates="food",
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index("ix_foods_owner_user_id_name", "owner_user_id", "name"),
    )
```

### 2.3. Tech Stack chi tiết

#### 2.3.1. Core Framework

**FastAPI (v0.125.0+)**
- **Lý do chọn:**
  - Performance cao: Tương đương NodeJS/Go, nhanh hơn Flask/Django
  - Async/await support: Xử lý concurrent requests hiệu quả
  - Automatic OpenAPI documentation: Tự động generate API docs
  - Type hints: Type-safe với Python type annotations
  - Data validation: Tích hợp Pydantic tự động validate request/response
  - Modern Python: Sử dụng các features mới nhất của Python 3.10+

- **Chức năng sử dụng:**
  - APIRouter: Tổ chức routes theo module
  - Dependency Injection: get_db, get_current_user
  - Background Tasks: Send emails, update cache
  - WebSocket: Realtime notifications (future)
  - CORS Middleware: Cho phép cross-origin requests

#### 2.3.2. Database & ORM

**PostgreSQL (v14+)**
- **Lý do chọn:**
  - Relational database mạnh mẽ: ACID compliance
  - Rich data types: UUID, JSONB, Array, INET
  - Advanced features: Partial indexes, GIN indexes
  - Full-text search: Tìm kiếm text tiếng Việt
  - Scalability: Vertical và horizontal scaling
  
- **Chức năng sử dụng:**
  - ENUM types: user_role_enum, gender_enum, streak_status_enum
  - UUID: Primary keys cho User, Profile
  - Partial indexes: Index với WHERE clause
  - Cascade delete: Tự động xóa related records
  - Check constraints: Validation ở database level

**SQLAlchemy 2.0**
- **Lý do chọn:**
  - Industry standard ORM cho Python
  - Type-safe với Mapped syntax mới
  - Query optimization: N+1 query prevention
  - Migration friendly: Tích hợp tốt với Alembic
  - Flexibility: Raw SQL khi cần performance

- **Patterns sử dụng:**
  - Declarative Base: Define models as classes
  - Mapped columns: Type-annotated columns
  - Relationships: One-to-Many, Many-to-Many
  - Session management: Context manager pattern
  - Eager loading: selectinload, joinedload

**Alembic**
- Database migration tool
- Version control cho database schema
- Auto-generate migrations từ models
- Rollback support khi cần
- Team collaboration: Merge multiple migrations

#### 2.3.3. Authentication & Security

**JWT (JSON Web Tokens)**
- **python-jose**: JWT encoding/decoding
- **Access token**: Short-lived (30 minutes), chứa user_id, role
- **Refresh token**: Long-lived (7 days), lưu hash trong DB
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Claims**: iss, sub (user_id), exp, iat, password_changed_at

**Password Hashing**
- **passlib with argon2**: State-of-the-art password hashing
- **Argon2id**: Winner of Password Hashing Competition 2015
- **Bcrypt fallback**: Compatibility với old systems
- **Salt**: Random salt mỗi password
- **No plaintext**: Never store passwords in plaintext

#### 2.3.4. AI & Machine Learning

**Google Gemini AI (gemini-2.5-flash)**
- **Sử dụng cho:** Chatbot tư vấn dinh dưỡng
- **Capabilities:**
  - Natural language understanding
  - Context-aware responses
  - Multi-turn conversations
  - Vietnamese language support
  
- **Integration:**
  - google-generativeai SDK
  - Prompt engineering cho nutrition domain
  - Safety settings để filter harmful content

**ChromaDB**
- **Vector database** cho RAG system
- **Chức năng:**
  - Embedding foods data thành vectors
  - Semantic search: Tìm kiếm based on meaning, not keywords
  - Top-k retrieval: Lấy k documents liên quan nhất
  - Persistent storage: Lưu vectors trên disk

- **Workflow RAG:**
  1. User hỏi: "Gà có bao nhiêu protein?"
  2. Embed câu hỏi thành vector
  3. ChromaDB tìm top-5 foods liên quan
  4. Gemini AI generate response dựa trên context

#### 2.3.5. Additional Services

**ImageKit.io**
- CDN for image/video storage
- Automatic optimization
- Resize, crop, format conversion
- URL-based transformations

**SMTP (Gmail)**
- Send transactional emails
- Password reset links
- Welcome emails
- Notification emails

**Translation & NLP**
- **langdetect**: Detect user language (vi, en)
- **deep-translator**: Translate queries/responses
- Seamless multilingual support

### 2.4. Cấu trúc thư mục chi tiết

```
backend/
│
├── alembic/                          # Database migrations
│   ├── versions/                     # Migration files (timestamped)
│   │   ├── 001_create_auth_tables.py
│   │   ├── 002_create_goals_table.py
│   │   ├── 003_create_food_and_exercise_tables.py
│   │   └── ...
│   ├── env.py                        # Alembic environment config
│   ├── script.py.mako                # Migration template
│   └── README                        # Alembic instructions
│
├── app/                              # Main application package
│   │
│   ├── api/                          # API Layer
│   │   ├── deps.py                   # Shared dependencies (auth, DB)
│   │   └── routes/                   # Route handlers (controllers)
│   │       ├── __init__.py
│   │       ├── auth.py               # Authentication endpoints
│   │       ├── users.py              # User management
│   │       ├── food.py               # Food CRUD
│   │       ├── exercise.py           # Exercise CRUD
│   │       ├── logs.py               # Daily logs (food/exercise)
│   │       ├── biometric.py          # Weight/height tracking
│   │       ├── goals.py              # Goal management
│   │       ├── streak.py             # Streak system
│   │       ├── blog.py               # Blog/social feed
│   │       ├── chatbot.py            # AI chatbot
│   │       ├── notifications.py      # Notifications
│   │       ├── settings.py           # User settings
│   │       ├── support.py            # Support tickets
│   │       └── admin/                # Admin panel routes
│   │           ├── __init__.py
│   │           ├── admin_dashboard.py
│   │           ├── admin_users.py
│   │           ├── admin_blog.py
│   │           ├── admin_support.py
│   │           └── admin_contributions.py
│   │
│   ├── core/                         # Core configuration
│   │   ├── database.py               # Database connection & session
│   │   └── settings.py               # App settings (from .env)
│   │
│   ├── models/                       # Database models (ORM)
│   │   ├── __init__.py
│   │   ├── base.py                   # Base model & mixins
│   │   ├── auth.py                   # User, Profile, RefreshSession
│   │   ├── food.py                   # Food, FoodPortion, FoodNutrient
│   │   ├── exercise.py               # Exercise
│   │   ├── log.py                    # FoodLogEntry, ExerciseLogEntry
│   │   ├── biometric.py              # BiometricsLog
│   │   ├── blog.py                   # Post, PostMedia, PostLike, PostSave
│   │   ├── streak.py                 # StreakDayCache, UserStreakState
│   │   ├── notification.py           # Notification
│   │   ├── support.py                # SupportTicket, SupportMessage
│   │   ├── password_reset.py         # PasswordResetToken
│   │   └── admin_stats.py            # DailySystemStats
│   │
│   ├── repositories/                 # Data access layer
│   │   ├── __init__.py
│   │   ├── user_repository.py
│   │   ├── profile_repository.py
│   │   ├── refresh_token_repository.py
│   │   ├── goal_repository.py
│   │   ├── biometrics_repository.py
│   │   ├── blog_repository.py
│   │   └── password_reset_repository.py
│   │
│   ├── schemas/                      # Pydantic schemas (validation)
│   │   ├── __init__.py
│   │   ├── auth.py                   # RegisterRequest, LoginRequest
│   │   ├── users.py                  # UserPublic, ProfileUpdate
│   │   ├── food.py                   # FoodCreateRequest, FoodDetail
│   │   ├── exercise.py               # ExerciseCreateRequest
│   │   ├── log.py                    # FoodLogEntryCreate
│   │   ├── biometric.py              # BiometricLogCreate
│   │   ├── goals.py                  # GoalCreateRequest, GoalResponse
│   │   ├── streak.py                 # StreakResponse
│   │   ├── blog.py                   # PostCreateRequest, PostResponse
│   │   ├── notification.py           # NotificationResponse
│   │   ├── support.py                # SupportTicketCreate
│   │   ├── settings.py               # UserSettingsUpdate
│   │   ├── admin.py                  # Admin schemas
│   │   └── common.py                 # Shared schemas (ErrorResponse)
│   │
│   ├── services/                     # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py           # Registration, login logic
│   │   ├── goal_service.py           # BMR, TDEE, macro calculations
│   │   ├── biometric_service.py      # Weight tracking logic
│   │   ├── streak_service.py         # Streak calculation logic
│   │   ├── password_service.py       # Password reset logic
│   │   ├── session_service.py        # Refresh token management
│   │   ├── media_service.py          # ImageKit integration
│   │   ├── send_mail_smtp.py         # Email sending
│   │   ├── admin_service.py          # Admin dashboard stats
│   │   ├── blog_service.py           # Blog business logic
│   │   ├── support_service.py        # Support ticket logic
│   │   ├── exercise_service.py       # Exercise calories calculation
│   │   │
│   │   ├── foods/                    # Food module services
│   │   │   ├── __init__.py
│   │   │   ├── food_service.py       # Food CRUD logic
│   │   │   ├── portion_service.py    # Portion management
│   │   │   ├── nutrient_service.py   # Nutrient management
│   │   │   ├── nutrients.py          # Nutrient definitions
│   │   │   ├── portions.py           # Portion definitions
│   │   │   ├── permissions.py        # Food access control
│   │   │   └── core.py               # Shared food logic
│   │   │
│   │   ├── logs/                     # Logging services
│   │   │   ├── __init__.py
│   │   │   ├── food_log_service.py   # Food log creation
│   │   │   ├── exercise_log_service.py
│   │   │   └── daily_log_service.py  # Daily summary
│   │   │
│   │   ├── nutri_chatbot/            # AI Chatbot
│   │   │   ├── chatbot_service.py    # Main chatbot orchestrator
│   │   │   ├── intent_classifier.py  # Classify user intent
│   │   │   ├── rag_service.py        # RAG system (ChromaDB)
│   │   │   ├── translate_service.py  # Multi-language support
│   │   │   └── database_adapter.py   # Query database for context
│   │   │
│   │   └── admin/                    # Admin services
│   │       ├── __init__.py
│   │       ├── admin_dashboard_service.py
│   │       ├── admin_user_service.py
│   │       └── admin_blog_service.py
│   │
│   ├── middleware/                   # Custom middleware
│   │   ├── __init__.py
│   │   └── auth_middleware.py        # Auth middleware (if needed)
│   │
│   ├── utils/                        # Utility functions
│   │   ├── __init__.py
│   │   └── timezone.py               # Timezone conversion helpers
│   │
│   ├── tests/                        # Unit tests
│   │   ├── test_biometrics.py
│   │   ├── test_exercises.py
│   │   └── test_logs.py
│   │
│   └── main.py                       # FastAPI app entry point
│
├── chroma_db/                        # ChromaDB persistent storage
│   ├── chroma.sqlite3                # SQLite for metadata
│   └── [collection_ids]/             # Vector embeddings
│
├── docs/                             # Documentation
│   ├── ADMIN_PANEL_API.md
│   ├── LOGS_API.md
│   └── ...
│
├── alembic.ini                       # Alembic configuration
├── pyproject.toml                    # Python project metadata
├── requirements.txt                  # Python dependencies
├── Dockerfile                        # Docker container definition
├── .env                              # Environment variables (not in git)
├── env.example.txt                   # .env template
├── README.md                         # Project README
└── FEATURE_01_REGISTER.md            # Feature documentation
```

### 2.5. Data Flow (Luồng xử lý dữ liệu)

#### Ví dụ: User tạo Food Log

```
1. CLIENT
   POST /api/v1/logs/food
   Body: {
     "logged_at": "2026-01-05T12:00:00Z",
     "meal_type": "lunch",
     "items": [
       {"food_id": 123, "portion_id": 456, "quantity": 2}
     ]
   }
   Header: Authorization: Bearer <access_token>

2. API LAYER (app/api/routes/logs.py)
   - FastAPI nhận request
   - Pydantic validate FoodLogEntryCreate schema
   - Dependency get_current_user: Decode JWT → User object
   - Dependency get_db: Inject database session
   - Call FoodLogService.create_food_log()

3. SERVICE LAYER (app/services/logs/food_log_service.py)
   - Tạo FoodLogEntry với totals = 0
   - Loop qua items:
     a. Query Food từ DB (via repository)
     b. Query FoodPortion để lấy grams
     c. Tính grams thực tế: quantity × portion.grams
     d. Query FoodNutrients (protein, carbs, fat per 100g)
     e. Calculate nutrition: (grams / 100) × nutrient_per_100g
     f. Tạo FoodLogItem với snapshot values
   - Aggregate totals từ tất cả items
   - Update FoodLogEntry.total_* fields
   - Call StreakService.on_log_created() để update streak
   - db.commit()

4. REPOSITORY LAYER
   - Execute SQLAlchemy queries
   - Return model objects

5. DATABASE (PostgreSQL)
   - Insert vào food_log_entries table
   - Insert vào food_log_items table
   - Update streak_days_cache table
   - Update user_streak_state table

6. SERVICE LAYER
   - Return FoodLogEntry object với relationships loaded

7. API LAYER
   - Serialize FoodLogEntry → FoodLogEntryResponse (Pydantic)
   - Return HTTP 201 Created với JSON response

8. CLIENT
   - Nhận response, update UI
```

### 2.6. Design Patterns được sử dụng

**1. Repository Pattern**
- Tách biệt business logic và data access
- Dễ test, dễ mock database
- Dễ thay đổi database implementation

**2. Dependency Injection**
- FastAPI Depends() cho database session, authentication
- Loose coupling giữa components
- Testability cao

**3. Service Layer Pattern**
- Centralize business logic
- Reusable across multiple endpoints
- Transaction boundary rõ ràng

**4. DTO (Data Transfer Object)**
- Pydantic schemas là DTOs
- Type-safe data transfer
- Validation tự động

**5. Factory Pattern**
- SessionLocal factory tạo database sessions
- Create_access_token, create_refresh_token factories

**6. Strategy Pattern**
- Different calculation strategies cho goals (lose/gain/maintain)
- Different portion calculation methods (by grams vs by portion)

---

**LƯU Ý:** Đây là phần đầu tiên của tài liệu. Các phần tiếp theo sẽ đi sâu vào chi tiết từng module chức năng, database schema, API endpoints, và các tính toán khoa học.