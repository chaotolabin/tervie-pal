# 📝 Tính Năng 1: ĐĂNG KÝ (Registration)

## 📋 Tóm tắt Thực hiện

Đã hoàn thành tính năng **ĐĂNG KÝ** với các thành phần:

### ✅ Files Được Tạo/Cập nhật:

1. **`app/api/schemas.py`** - Pydantic schemas cho validation
   - `RegisterRequest`: username (3-32), email, password (8-128)
   - `AuthTokensResponse`: trả về user, access_token, refresh_token
   - `UserPublic`, `Profile`, `ProfilePatchRequest`, v.v.

2. **`app/api/deps.py`** - Dependency utilities
   - `hash_password()`: Hash password bằng bcrypt
   - `verify_password()`: Xác thực password
   - `create_access_token()`: Tạo JWT access token (30 min)
   - `create_refresh_token()`: Tạo JWT refresh token (7 days)
   - `decode_token()`: Decode JWT token
   - `get_current_user()`: Dependency để lấy user từ access token
   - `get_current_admin_user()`: Dependency để kiểm tra admin role

3. **`app/api/routes/auth.py`** - Authentication routes
   - `POST /api/v1/auth/register` - Endpoint đăng ký

4. **`app/main.py`** - Cập nhật FastAPI app
   - Thêm CORS middleware
   - Include auth router với prefix `/api/v1`
   - Cấu hình OpenAPI docs

5. **`requirements.txt`** - Thêm dependencies
   - `pydantic-settings`, `pydantic[email]`
   - `passlib[bcrypt]`, `PyJWT`, `python-multipart`

6. **`alembic/versions/001_create_auth_tables.py`** - Database migration
   - Tạo bảng `users`
   - Tạo bảng `profiles`
   - Tạo bảng `refresh_sessions`
   - ENUM types: `user_role_enum`, `gender_enum`

---

## 🔐 Chi tiết Bảo mật

### Password Security
```
1. Client gửi password plaintext qua HTTPS
2. Server hash password bằng bcrypt (rounds=12 default)
3. Lưu password_hash vào DB (NEVER store plaintext)
4. Verification: bcrypt.verify(input_pwd, stored_hash)
```

### Token Management
```
Access Token (JWT):
- Expires: 30 minutes
- Claims: sub (user_id), exp, type
- Usage: Authorization: Bearer <token>

Refresh Token (JWT):
- Expires: 7 days
- Stored as hash in DB (security best practice)
- Rotation: Each refresh creates new tokens
- Can revoke: Set revoked_at timestamp
```

### Database Design
```
users:
  - id: UUID (primary key)
  - username: UNIQUE
  - email: UNIQUE
  - password_hash: bcrypt hash
  - role: ENUM (user|admin)
  - password_changed_at: NULL (for token revocation)
  - created_at, updated_at: Timezone-aware timestamps

profiles:
  - user_id: FK -> users(id) CASCADE
  - full_name, gender, date_of_birth, height_cm_default: Optional
  - One-to-one relationship with users

refresh_sessions:
  - user_id: FK -> users(id) CASCADE
  - refresh_token_hash: UNIQUE (store hash, not token)
  - device_label, user_agent, ip: Track device info
  - revoked_at: NULL = active, SET = revoked
  - One-to-many relationship with users
```

---

## 🧪 Hướng dẫn Test

### 1. Setup Database

```bash
# Vào thư mục backend
cd backend

# Cài dependencies
pip install -r requirements.txt

# Cấu hình DATABASE_URL trong .env (PostgreSQL)
# DATABASE_URL=postgresql://user:password@localhost:5432/tervie_pal

# Chạy migration
alembic upgrade head
```

### 2. Chạy Server

```bash
# Terminal 1: FastAPI development server
cd backend
uvicorn app.main:app --reload --port 8000
```

### 3. Test Endpoint

#### **POST /api/v1/auth/register**

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

**Success Response (200):**
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john@example.com",
    "role": "user"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Error: Username Exists (409)**
```json
{
  "detail": "Username already exists"
}
```

**Error: Email Exists (409)**
```json
{
  "detail": "Email already exists"
}
```

**Error: Validation (422)**
```json
{
  "detail": [
    {
      "loc": ["body", "username"],
      "msg": "ensure this value has at least 3 characters",
      "type": "value_error.string.too_short"
    }
  ]
}
```

---

## 💾 Quy trình Đăng ký Chi tiết

### Flow:
```
1. Client gửi POST /auth/register {username, email, password}
   ↓
2. Validate input (length, email format)
   ↓
3. Check username UNIQUE
   ✗ → 409 Conflict
   ✓ → Continue
   ↓
4. Check email UNIQUE
   ✗ → 409 Conflict
   ✓ → Continue
   ↓
5. Hash password (bcrypt)
   ↓
6. Create User record (role=user by default)
   ↓
7. Create empty Profile (user can update later)
   ↓
8. Create Refresh Token & hash it
   ↓
9. Store RefreshSession in DB (device tracking)
   ↓
10. Generate Access Token
    ↓
11. Return {user, access_token, refresh_token}
    ↓
12. Client lưu tokens vào localStorage/secureStorage
```

---

## 🛠️ Cấu hình & Environment Variables

**`.env` file:**
```env
PROJECT_NAME=Tervie Pal
PROJECT_VERSION=0.1.0
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/tervie_pal
SECRET_KEY=your-super-secret-key-change-in-production
ENVIRONMENT=development
```

---

## 📊 Validation Rules

| Field | Min | Max | Format | Required |
|-------|-----|-----|--------|----------|
| username | 3 | 32 | alphanumeric, underscore | ✓ |
| email | - | - | valid email | ✓ |
| password | 8 | 128 | any printable chars | ✓ |

---

## 🔄 Token Usage

**Use Access Token for Protected Endpoints:**
```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <access_token>"
```

**Refresh Expired Token:**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<refresh_token>"
  }'
```

---

## ✨ Đặc điểm Nổi bật

✅ **Password Security**: Bcrypt hashing với rounds tối ưu  
✅ **JWT Tokens**: Access (30m) + Refresh (7d) separation  
✅ **Device Tracking**: Lưu user_agent, IP, device_label  
✅ **Token Revocation**: Có thể revoke sessions  
✅ **Timezone-aware**: Tất cả timestamps dùng UTC  
✅ **Soft Delete Ready**: Database design hỗ trợ soft delete  
✅ **Input Validation**: Pydantic validation + SQL constraints  
✅ **Error Handling**: Descriptive error messages  

---

## 🎯 Tính năng Tiếp theo

1. **Login** - `/auth/login`
2. **Logout** - `/auth/logout`
3. **Token Refresh** - `/auth/refresh`
4. **Password Reset** - `/auth/forgot-password`, `/auth/reset-password`
5. **Get Current User** - `/users/me`
6. **Update Profile** - `/profile` (PATCH)

---

Sẵn sàng check tính năng này trước khi code tính năng tiếp theo?
