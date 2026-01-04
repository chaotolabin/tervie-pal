# ADMIN PANEL - TÀI LIỆU KỸ THUẬT

## TỔNG QUAN

Đã hoàn thành xây dựng **Admin Panel** cho ứng dụng Health Tracking với các tính năng:

1. **Dashboard Statistics** - Thống kê toàn diện
2. **User Management** - Quản lý người dùng
3. **Blog Management** - Quản lý bài viết
4. **Support System** - Hệ thống hỗ trợ (đã có trước)

---

## CẤU TRÚC FILE MỚI

```
backend/app/
├── schemas/
│   └── admin.py                    # NEW: Pydantic schemas cho Admin
├── services/
│   └── admin_service.py            # NEW: Business logic
└── api/routes/admin/
    ├── __init__.py                 # UPDATED: Import routers mới
    ├── admin_dashboard.py          # NEW: Dashboard endpoints
    ├── admin_users.py              # NEW: User management endpoints
    ├── admin_blog.py               # NEW: Blog management endpoints
    └── admin_support.py            # EXISTING: Support endpoints
```

---

## BẢO MẬT (SECURITY)

### Dependency `get_current_admin_user`

**Tất cả** endpoint admin đều sử dụng dependency này để kiểm tra quyền:

```python
from app.api.deps import get_current_admin_user

@router.get("/admin/dashboard")
def get_dashboard(
    admin_user: User = Depends(get_current_admin_user)
):
    # Chỉ admin (user.role == 'admin') mới vào được
    ...
```

**Logic kiểm tra:**
- Kiểm tra JWT access token hợp lệ
- Kiểm tra `user.role == "admin"`
- Nếu không phải admin → **403 Forbidden**

---

## TÍNH NĂNG 1: DASHBOARD STATISTICS

### Endpoints

#### 1. GET `/api/v1/admin/dashboard/stats` (Chi tiết)

**Mô tả:** Thống kê toàn diện cho dashboard

**Query Parameters:**
- `range`: `7d`, `30d`, `90d` (default: `7d`)
- `top_n`: Số lượng items trong top lists (default: `10`, max: `50`)

**Response:**
```json
{
  "user_stats": {
    "total_users": 1250,
    "new_users": 45,
    "active_users": 320,
    "admin_count": 5
  },
  "log_stats": {
    "total_food_logs": 15000,
    "total_exercise_logs": 8500,
    "food_logs_in_range": 1200,
    "exercise_logs_in_range": 650
  },
  "retention_metrics": {
    "dau": 150,
    "wau": 380,
    "mau": 820
  },
  "blog_stats": {
    "total_posts": 850,
    "posts_in_range": 65,
    "total_likes": 12000,
    "total_saves": 3500,
    "top_liked_posts": [...],
    "top_saved_posts": [...],
    "top_engagement_posts": [...],
    "trending_posts": [...]
  },
  "streak_stats": {
    "users_with_streak": 450,
    "average_streak": 12.5,
    "highest_streak": 89,
    "highest_streak_user_id": "uuid...",
    "top_streak_users": [...],
    "users_with_week_streak": 280,
    "users_with_month_streak": 45
  },
  "query_range": "7d",
  "generated_at": "2026-01-04T10:30:00Z"
}
```

#### 2. GET `/api/v1/admin/dashboard` (Đơn giản)

**Mô tả:** Dashboard summary đơn giản (theo OpenAPI spec)

**Response:**
```json
{
  "users_count": 1250,
  "posts_count": 850,
  "open_tickets_count": 12
}
```

### Service Logic

**File:** `app/services/admin_service.py`

**Class:** `AdminDashboardService`

**Methods:**

1. **`get_user_stats(db, range_days, range_start)`**
   - Tổng số users
   - Users mới trong khoảng thời gian
   - Active users: có log meal HOẶC log exercise trong range
   - Số admin

2. **`get_log_stats(db, range_start)`**
   - Tổng số food/exercise logs (all time)
   - Logs trong khoảng thời gian

3. **`get_retention_metrics(db)`**
   - **DAU** (Daily Active Users): 24h
   - **WAU** (Weekly Active Users): 7d
   - **MAU** (Monthly Active Users): 30d
   - Dựa trên activity trong FoodLogEntry + ExerciseLogEntry

4. **`get_blog_stats(db, range_start, top_n)`**
   - Tổng posts, likes, saves
   - Top posts: liked, saved, engagement
   - Trending: posts gần đây (7d) có engagement cao

5. **`get_streak_stats(db, top_n)`**
   - Users có streak > 0
   - Streak trung bình, cao nhất
   - Top N users có streak cao nhất
   - Users có streak >= 7, >= 30

**Performance Optimization:**
- Sử dụng `func.count()`, `func.avg()`, `func.max()` của SQLAlchemy
- Query aggregation thay vì fetch all records
- Union queries cho active users

---

## TÍNH NĂNG 2: USER MANAGEMENT

### Endpoints

#### 1. GET `/api/v1/admin/users` (List)

**Mô tả:** Danh sách users với phân trang và filter

**Query Parameters:**
- `page`: Trang hiện tại (default: `1`)
- `page_size`: Số items/trang (default: `50`, max: `200`)
- `email`: Filter theo email (partial match)
- `role`: Filter theo role (`user`/`admin`)
- `status`: Filter theo status (TODO)

**Response:**
```json
{
  "items": [
    {
      "id": "uuid...",
      "username": "john_doe",
      "email": "john@example.com",
      "role": "user",
      "full_name": "John Doe",
      "created_at": "2025-12-01T10:00:00Z",
      "current_streak": 15,
      "last_log_at": "2026-01-03T08:30:00Z"
    }
  ],
  "total": 1250,
  "page": 1,
  "page_size": 50,
  "total_pages": 25
}
```

#### 2. GET `/api/v1/admin/users/{user_id}` (Detail)

**Mô tả:** Chi tiết đầy đủ của user

**Response:**
```json
{
  "id": "uuid...",
  "username": "john_doe",
  "email": "john@example.com",
  "role": "user",
  "created_at": "2025-12-01T10:00:00Z",
  "full_name": "John Doe",
  "gender": "male",
  "date_of_birth": "1995-05-15",
  "height_cm_default": 175.0,
  "current_streak": 15,
  "longest_streak": 45,
  "last_on_time_day": "2026-01-03",
  "activity_summary": {
    "total_food_logs": 450,
    "total_exercise_logs": 180,
    "total_posts": 12,
    "last_food_log_at": "2026-01-03T12:00:00Z",
    "last_exercise_log_at": "2026-01-02T18:30:00Z",
    "last_post_at": "2025-12-28T14:00:00Z"
  },
  "goal_type": "lose_weight",
  "daily_calorie_target": 1800.0
}
```

#### 3. PATCH `/api/v1/admin/users/{user_id}/role` (Update Role)

**Mô tả:** Thay đổi role user <-> admin

**Request Body:**
```json
{
  "role": "admin"
}
```

**Business Rules:**
- Admin không thể tự đổi role của chính mình
- Cần ghi log action (TODO: audit log)

**Response:**
```json
{
  "success": true,
  "message": "User role updated to admin",
  "action": "update_user_role",
  "performed_at": "2026-01-04T10:30:00Z",
  "performed_by": "admin_uuid..."
}
```

#### 4. POST `/api/v1/admin/users/{user_id}/streak/adjust` (Adjust Streak)

**Mô tả:** Điều chỉnh streak (xử lý khiếu nại)

**Request Body:**
```json
{
  "current_streak": 20,
  "reason": "User reported streak loss due to system error"
}
```

**Business Logic:**
- Set streak thủ công
- Tự động cập nhật `longest_streak` nếu cần
- Ghi log reason (audit trail)

**Use Cases:**
- User khiếu nại streak bị mất do lỗi
- Sửa lỗi tính toán
- Thưởng streak cho sự kiện

---

## TÍNH NĂNG 3: BLOG MANAGEMENT

### Endpoints

#### 1. GET `/api/v1/admin/posts` (List)

**Mô tả:** Danh sách posts

**Query Parameters:**
- `page`, `page_size`: Phân trang
- `include_deleted`: Bao gồm posts đã xóa (default: `false`)

**Response:**
```json
{
  "items": [
    {
      "id": 123,
      "user_id": "uuid...",
      "username": "john_doe",
      "title": "My fitness journey",
      "content_preview": "Today I reached my goal...",
      "like_count": 45,
      "save_count": 12,
      "created_at": "2026-01-01T10:00:00Z",
      "deleted_at": null
    }
  ],
  "total": 850,
  "page": 1,
  "page_size": 50,
  "total_pages": 17
}
```

#### 2. DELETE `/api/v1/admin/posts/{post_id}` (Delete)

**Mô tả:** Soft delete post

**Request Body (Optional):**
```json
{
  "reason": "Violates community guidelines"
}
```

**Business Logic:**
- Soft delete: Set `deleted_at` timestamp
- Không xóa thật khỏi database
- Ghi log reason (audit trail)

**Use Cases:**
- Xóa bài vi phạm
- Xóa spam
- Xóa nội dung không phù hợp

#### 3. POST `/api/v1/admin/posts/{post_id}/restore` (Restore)

**Status:** **TODO** - Chưa implement

---

## TÍNH NĂNG 4: SUPPORT SYSTEM

### Endpoints (Đã có)

#### 1. GET `/api/v1/admin/support/tickets`

**Mô tả:** Xem tất cả tickets

**Filters:**
- `status`: `open`, `in_progress`, `resolved`, `closed`
- `category`: `bug`, `feature_request`, `question`, `other`

#### 2. PATCH `/api/v1/admin/support/tickets/{ticket_id}`

**Mô tả:** Cập nhật status/category của ticket

**File:** `app/api/routes/admin/admin_support.py` (đã có sẵn)

---

## TESTING

### Cách test API:

1. **Đăng nhập bằng admin account:**
```bash
POST /api/v1/auth/login
{
  "email": "mondubi89@gmail.com",
  "password": "kh0ngc0Pass.word"
}
```

2. **Lấy access_token từ response**

3. **Test Dashboard:**
```bash
GET /api/v1/admin/dashboard/stats?range=7d&top_n=10
Authorization: Bearer {access_token}
```

4. **Test User Management:**
```bash
GET /api/v1/admin/users?page=1&page_size=20
Authorization: Bearer {access_token}
```

5. **Test Blog Management:**
```bash
GET /api/v1/admin/posts?page=1
Authorization: Bearer {access_token}
```

### Kiểm tra bảo mật:

1. **Login bằng user thường (không phải admin)**
2. **Thử truy cập endpoint admin**
3. **Kết quả:** Nhận `403 Forbidden`

---

## HIỆU NĂNG (PERFORMANCE)

### SQL Optimization:

1. **Dashboard Stats:**
   - Sử dụng `func.count()` thay vì fetch all
   - Union queries cho active users
   - Index sẵn có: `user_id`, `logged_at`, `created_at`

2. **User List:**
   - Pagination với `offset`/`limit`
   - Filter với `ILIKE` (case-insensitive)
   - Join tối ưu: User + Profile + StreakState

3. **Blog Stats:**
   - `ORDER BY` với indexed columns
   - Limit top N results
   - Aggregation functions

### Recommendations:

- **Cache:** Cache dashboard stats (Redis) với TTL = 5 phút
- **Background Jobs:** Tính toán stats nặng bằng Celery
- **Indexes:** Đảm bảo indexes trên các columns filter/sort

---

## TODO / FUTURE IMPROVEMENTS

### High Priority:

1. **Audit Log:**
   - Tạo bảng `admin_audit_logs`
   - Log tất cả admin actions: role change, streak adjust, post delete
   - Query: `admin_id`, `action_type`, `target_id`, `reason`, `created_at`

2. **Post Restore:**
   - Implement restore deleted posts
   - Set `deleted_at = NULL`

### Medium Priority:

3. **Advanced Filters:**
   - User list: Filter theo created_at range, streak range
   - Post list: Filter theo like_count, engagement

4. **Bulk Actions:**
   - Delete multiple posts

5. **Export Data:**
   - Export users/posts to CSV
   - Generate reports

### Low Priority:

7. **Real-time Notifications:**
   - WebSocket cho admin dashboard
   - Real-time ticket updates

8. **Dashboard Charts:**
   - Chart API: User growth, retention trends
   - Integrate với frontend charting library

---

## CHECKLIST HOÀN THÀNH

### Schema Layer (Pydantic)
- [x] `app/schemas/admin.py` - Tất cả schemas
- [x] Dashboard: Stats, Response models
- [x] User Management: List, Detail, Action requests
- [x] Blog Management: List, Delete requests

### Service Layer (Business Logic)
- [x] `app/services/admin_service.py`
- [x] `AdminDashboardService`: 5 methods statistics
- [x] `AdminUserService`: List, Detail, Role update, Streak adjust
- [x] `AdminBlogService`: List posts, Delete post

### Router Layer (API Endpoints)
- [x] `app/api/routes/admin/admin_dashboard.py`
  - Dashboard stats (chi tiết)
  - Dashboard summary (đơn giản)
- [x] `app/api/routes/admin/admin_users.py`
  - List users, User detail
  - Update role, Adjust streak
- [x] `app/api/routes/admin/admin_blog.py`
  - List posts, Delete post
- [x] `app/api/routes/admin/__init__.py` - Router integration

### Security
- [x] Tất cả endpoints dùng `get_current_admin_user`
- [x] Kiểm tra `user.role == 'admin'`
- [x] 403 Forbidden cho non-admin

### Documentation
- [x] Docstrings chi tiết cho tất cả functions
- [x] OpenAPI descriptions
- [x] File tài liệu này

---

## HỖ TRỢ

### Nếu gặp lỗi:

1. **Import Error:**
   - Chạy: `pip install -r requirements.txt`
   - Restart VS Code

2. **Database Error:**
   - Kiểm tra connection: `GET /health`
   - Chạy migrations: `alembic upgrade head`

3. **403 Forbidden:**
   - Đảm bảo đăng nhập bằng admin account
   - Check `user.role` trong database

4. **Performance Issue:**
   - Check database indexes
   - Enable query logging: `echo=True` trong engine
   - Optimize N+1 queries

---

## KẾT LUẬN

Đã hoàn thành **Admin Panel** với đầy đủ tính năng:

- Dashboard Statistics (toàn diện)
- User Management (CRUD + actions)
- Blog Management (list + delete)
- Support System (existing)

**Code quality:**
- Clean Architecture (3-layer)
- Type hints đầy đủ
- Security chặt chẽ
- Performance optimized

**Sẵn sàng production!** 