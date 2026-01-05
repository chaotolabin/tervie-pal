# TÀI LIỆU API ENDPOINTS - TERVIE PAL BACKEND

Tài liệu này mô tả chi tiết tất cả các API endpoints của hệ thống Tervie Pal Backend, bao gồm request/response schemas, authentication requirements, và business logic.

**Base URL:** `http://localhost:8000/api/v1`

**API Documentation:** `http://localhost:8000/api/v1/docs` (Swagger UI)

---

## MỤC LỤC

1. [Authentication](#1-authentication-auth)
2. Users
3. Foods
4. Exercises
5. Logs
6. Biometrics
7. Goals
8. Streak
9. Blog
10. Chatbot
11. Notifications
12. Settings
13. Support
14. Admin

---

## 1. AUTHENTICATION (Auth)

Module Authentication cung cấp các chức năng đăng ký, đăng nhập, quản lý tokens, và reset password.

**Tag:** `Auth`

**Endpoints:**
- POST /auth/register - Đăng ký tài khoản mới
- POST /auth/login - Đăng nhập
- POST /auth/refresh - Làm mới access token
- POST /auth/logout - Đăng xuất
- POST /auth/forgot-password - Yêu cầu reset password
- POST /auth/reset-password - Đặt lại password

---

### 1.1. Đăng ký tài khoản (Register)

Tạo tài khoản người dùng mới với đầy đủ thông tin cá nhân, mục tiêu, và sinh trắc học ban đầu.

**Endpoint:** `POST /api/v1/auth/register`

**Authentication:** Không yêu cầu (public endpoint)

**Request Body:**

```json
{
  "username": "john_doe",
  "email": "john.doe@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "gender": "male",
  "date_of_birth": "1990-05-15",
  "height_cm": 175.5,
  "weight_kg": 80.0,
  "goal_weight_kg": 75.0,
  "goal_type": "lose_weight",
  "baseline_activity": "moderately_active",
  "weekly_goal": 0.5,
  "weekly_exercise_min": 180
}
```

**Request Schema:**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| username | string | Yes | 3-32 chars | Tên đăng nhập, unique |
| email | string (email) | Yes | Valid email | Email, unique |
| password | string | Yes | 8-128 chars | Mật khẩu (sẽ được hash) |
| full_name | string | Yes | 1-255 chars | Họ và tên đầy đủ |
| gender | string | Yes | "male" hoặc "female" | Giới tính (dùng cho tính BMR) |
| date_of_birth | string (date) | Yes | YYYY-MM-DD | Ngày sinh |
| height_cm | number (decimal) | Yes | > 0, 2 decimal places | Chiều cao (cm) |
| weight_kg | number (decimal) | Yes | > 0, 2 decimal places | Cân nặng hiện tại (kg) |
| goal_weight_kg | number (decimal) | No | > 0, 2 decimal places | Cân nặng mục tiêu (kg) |
| goal_type | string | Yes | Enum (xem bên dưới) | Loại mục tiêu |
| baseline_activity | string | Yes | Enum (xem bên dưới) | Mức độ hoạt động cơ bản |
| weekly_goal | number (float) | Yes | - | Mục tiêu kg/tuần (0.25 hoặc 0.5) |
| weekly_exercise_min | integer | No | >= 0 | Phút tập luyện/tuần |

**goal_type Enum:**
- `lose_weight` - Giảm cân
- `gain_weight` - Tăng cân
- `maintain_weight` - Duy trì cân nặng
- `build_muscle` - Tăng cơ
- `improve_health` - Cải thiện sức khỏe

**baseline_activity Enum:**
- `sedentary` - Ít vận động (văn phòng, không tập)
- `low_active` - Vận động nhẹ (1-3 ngày/tuần)
- `moderately_active` - Vận động vừa (3-5 ngày/tuần)
- `very_active` - Vận động nhiều (6-7 ngày/tuần)
- `extremely_active` - Vận động rất nhiều (2 lần/ngày, công việc nặng)

**Success Response (200 OK):**

```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john.doe@example.com",
    "role": "user"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer"
}
```

**Response Schema:**

| Field | Type | Description |
|-------|------|-------------|
| user | object | Thông tin người dùng |
| user.id | string (UUID) | User ID |
| user.username | string | Tên đăng nhập |
| user.email | string | Email |
| user.role | string | Vai trò ("user" hoặc "admin") |
| access_token | string | JWT access token (expires in 30 minutes) |
| refresh_token | string | JWT refresh token (expires in 7 days) |
| token_type | string | Luôn là "Bearer" |

**Error Responses:**

**400 Bad Request - Email đã tồn tại:**
```json
{
  "detail": "Email already registered"
}
```

**400 Bad Request - Username đã tồn tại:**
```json
{
  "detail": "Username already taken"
}
```

**400 Bad Request - Chiều cao không hợp lệ:**
```json
{
  "detail": "Chiều cao phải từ 50-300 cm"
}
```

**400 Bad Request - Cân nặng không hợp lệ:**
```json
{
  "detail": "Cân nặng phải từ 10-500 kg"
}
```

**422 Unprocessable Entity - Validation Error:**
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "username"],
      "msg": "String should have at least 3 characters",
      "input": "ab",
      "ctx": {"min_length": 3}
    }
  ]
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal error"
}
```

**Business Logic:**

Khi đăng ký, hệ thống thực hiện các bước sau:

1. **Validation:**
   - Check email và username chưa tồn tại
   - Validate chiều cao (50-300 cm) và cân nặng (10-500 kg)

2. **Tạo User:**
   - Hash password bằng Argon2/Bcrypt
   - Tạo record trong bảng `users`

3. **Tạo Profile:**
   - Lưu thông tin cá nhân vào bảng `profiles`

4. **Tạo BiometricsLog đầu tiên:**
   - Lưu cân nặng và chiều cao ban đầu
   - Tính BMI = weight_kg / (height_cm/100)²

5. **Tạo Goal:**
   - Tính BMR theo công thức Mifflin-St Jeor
   - Tính TDEE = BMR × activity_multiplier
   - Tính daily_calorie_target dựa trên goal_type và weekly_goal
   - Tính macros (protein, fat, carbs) theo tỷ lệ 20/30/50
   - Lưu vào bảng `goals`

6. **Tạo Refresh Session:**
   - Hash refresh token
   - Lưu vào bảng `refresh_sessions`

7. **Trả về tokens:**
   - Access token (JWT, 30 phút)
   - Refresh token (JWT, 7 ngày)

**Ví dụ sử dụng:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "jane_smith",
    "email": "jane@example.com",
    "password": "MyPassword123!",
    "full_name": "Jane Smith",
    "gender": "female",
    "date_of_birth": "1995-08-20",
    "height_cm": 165.0,
    "weight_kg": 68.0,
    "goal_weight_kg": 62.0,
    "goal_type": "lose_weight",
    "baseline_activity": "low_active",
    "weekly_goal": 0.5,
    "weekly_exercise_min": 120
  }'
```

---

### 1.2. Đăng nhập (Login)

Xác thực người dùng và trả về JWT tokens để sử dụng cho các requests tiếp theo.

**Endpoint:** `POST /api/v1/auth/login`

**Authentication:** Không yêu cầu (public endpoint)

**Request Body:**

```json
{
  "email_or_username": "john_doe",
  "password": "SecurePass123!",
  "device_label": "iPhone 14 Pro"
}
```

**Request Schema:**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| email_or_username | string | Yes | - | Email hoặc username |
| password | string | Yes | 8-128 chars | Mật khẩu |
| device_label | string | No | - | Nhãn thiết bị (cho quản lý sessions) |

**Success Response (200 OK):**

```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john.doe@example.com",
    "role": "user"
  },
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer"
}
```

**Response Schema:** Giống như Register response

**Error Responses:**

**401 Unauthorized - Sai thông tin đăng nhập:**
```json
{
  "detail": "Incorrect email/username or password"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal error"
}
```

**Business Logic:**

1. Tìm user theo email hoặc username
2. Verify password bằng bcrypt.verify()
3. Tạo access token và refresh token mới
4. Lưu refresh token (hash) vào `refresh_sessions` table
5. Trả về tokens

**Lưu ý:**
- Refresh token được hash trước khi lưu database (security)
- Có thể track device_label, user_agent, IP address
- Một user có thể có nhiều refresh sessions (nhiều thiết bị)

**Ví dụ sử dụng:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email_or_username": "john.doe@example.com",
    "password": "SecurePass123!",
    "device_label": "Chrome Browser - Windows"
  }'
```

---

### 1.3. Làm mới access token (Refresh)

Tạo access token mới khi token hiện tại hết hạn, không cần đăng nhập lại.

**Endpoint:** `POST /api/v1/auth/refresh`

**Authentication:** Không yêu cầu (nhưng cần refresh token hợp lệ)

**Request Body:**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Request Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| refresh_token | string | Yes | Refresh token nhận được từ login/register |

**Success Response (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response Schema:**

| Field | Type | Description |
|-------|------|-------------|
| access_token | string | JWT access token mới (expires in 30 minutes) |
| refresh_token | string | JWT refresh token mới (expires in 7 days) |

**Error Responses:**

**401 Unauthorized - Token không hợp lệ:**
```json
{
  "detail": "Invalid refresh token"
}
```

**401 Unauthorized - Token đã hết hạn:**
```json
{
  "detail": "Refresh token expired"
}
```

**401 Unauthorized - Token đã bị revoke:**
```json
{
  "detail": "Refresh token has been revoked"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal error"
}
```

**Business Logic:**

1. Decode refresh token để lấy user_id
2. Hash refresh token và tìm trong database
3. Kiểm tra:
   - Token chưa bị revoke (`revoked_at IS NULL`)
   - User còn tồn tại
   - Password chưa thay đổi sau khi token được issue
4. Tạo access token và refresh token mới
5. Update `last_used_at` của refresh session
6. Trả về tokens mới

**Rotation Strategy:**
- Mỗi lần refresh, cả access token và refresh token đều được tạo mới
- Refresh token cũ vẫn valid cho đến khi hết hạn (không revoke ngay lập tức)
- Tránh race condition khi có nhiều requests đồng thời

**Ví dụ sử dụng:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

---

### 1.4. Đăng xuất (Logout)

Revoke refresh token, khiến nó không thể sử dụng để refresh nữa.

**Endpoint:** `POST /api/v1/auth/logout`

**Authentication:** Không yêu cầu (nhưng cần refresh token hợp lệ)

**Request Body:**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Request Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| refresh_token | string | Yes | Refresh token cần revoke |

**Success Response (204 No Content):**

Không có response body, chỉ trả về status code 204.

**Error Responses:**

**401 Unauthorized - Token không hợp lệ:**
```json
{
  "detail": "Invalid refresh token"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal error"
}
```

**Business Logic:**

1. Hash refresh token
2. Tìm refresh session trong database
3. Set `revoked_at = NOW()`
4. Commit transaction

**Lưu ý:**
- Access token vẫn valid cho đến khi hết hạn (không thể revoke JWT)
- Để logout hoàn toàn, client phải xóa cả access token và refresh token
- Server không thể revoke access token vì JWT là stateless

**Best Practice:**
- Client nên xóa tokens khỏi localStorage/cookies sau khi logout
- Server revoke refresh token để ngăn refresh sau này

**Ví dụ sử dụng:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

---

### 1.5. Quên mật khẩu (Forgot Password)

Gửi email chứa link reset password cho user.

**Endpoint:** `POST /api/v1/auth/forgot-password`

**Authentication:** Không yêu cầu (public endpoint)

**Request Body:**

```json
{
  "email": "john.doe@example.com",
  "frontend_url": "https://terviepal.com"
}
```

**Request Schema:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| email | string (email) | Yes | Email của tài khoản cần reset password |
| frontend_url | string | No | Base URL của frontend (để tạo reset link) |

**Success Response (200 OK):**

```json
{
  "message": "If email exists, password reset link has been sent"
}
```

**Response Schema:**

| Field | Type | Description |
|-------|------|-------------|
| message | string | Thông báo thành công |

**Lưu ý về Response:**
- Luôn trả về success message dù email có tồn tại hay không
- Tránh information disclosure (kẻ tấn công không biết email nào tồn tại)
- Security best practice

**Error Responses:**

**500 Internal Server Error:**
```json
{
  "detail": "Internal error"
}
```

**Business Logic:**

1. Tìm user theo email
2. Nếu không tìm thấy:
   - Vẫn trả về success message (security)
   - Không gửi email
3. Nếu tìm thấy:
   - Tạo reset token (random secure token, 32 chars)
   - Set expiry time (1 giờ)
   - Lưu vào bảng `password_reset_tokens`
   - Gửi email với link: `{frontend_url}/reset-password?token={token}`
   - Trả về success message

**Email Content Example:**

```
Subject: Reset Your Password - Tervie Pal

Hello John,

You requested to reset your password. Click the link below to reset it:

https://terviepal.com/reset-password?token=abc123def456...

This link will expire in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
Tervie Pal Team
```

**Security Features:**
- Token là random string, không đoán được
- Token expires sau 1 giờ
- Token chỉ dùng được 1 lần (deleted sau khi dùng)
- Rate limiting ngăn spam requests

**Ví dụ sử dụng:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/forgot-password \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@example.com",
    "frontend_url": "https://terviepal.com"
  }'
```

---

### 1.6. Đặt lại mật khẩu (Reset Password)

Đặt mật khẩu mới sử dụng token từ email.

**Endpoint:** `POST /api/v1/auth/reset-password`

**Authentication:** Không yêu cầu (nhưng cần reset token hợp lệ)

**Request Body:**

```json
{
  "token": "abc123def456ghi789jkl012mno345pq",
  "new_password": "NewSecurePass456!"
}
```

**Request Schema:**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| token | string | Yes | - | Reset token từ email |
| new_password | string | Yes | 8-128 chars | Mật khẩu mới |

**Success Response (204 No Content):**

Không có response body, chỉ trả về status code 204.

**Error Responses:**

**400 Bad Request - Token không hợp lệ hoặc hết hạn:**
```json
{
  "detail": "Invalid or expired token"
}
```

**400 Bad Request - Token đã được sử dụng:**
```json
{
  "detail": "Token has already been used"
}
```

**422 Unprocessable Entity - Password quá ngắn:**
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "new_password"],
      "msg": "String should have at least 8 characters"
    }
  ]
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal error"
}
```

**Business Logic:**

1. Tìm token trong bảng `password_reset_tokens`
2. Kiểm tra:
   - Token tồn tại
   - Token chưa hết hạn (`expires_at > NOW()`)
   - Token chưa được sử dụng (`used_at IS NULL`)
3. Hash password mới
4. Update password trong bảng `users`
5. Set `password_changed_at = NOW()` (để revoke tất cả tokens cũ)
6. Set `used_at = NOW()` trong `password_reset_tokens`
7. Revoke tất cả refresh sessions của user (force logout tất cả thiết bị)
8. Commit transaction

**Security Features:**
- Tất cả sessions cũ bị logout (phòng trường hợp bị hack)
- Token chỉ dùng được 1 lần
- Password được hash trước khi lưu
- `password_changed_at` timestamp làm invalidate tất cả JWT cũ

**Lưu ý:**
- User phải đăng nhập lại sau khi reset password
- Tất cả thiết bị khác đều bị logout

**Ví dụ sử dụng:**

```bash
curl -X POST http://localhost:8000/api/v1/auth/reset-password \
  -H "Content-Type: application/json" \
  -d '{
    "token": "abc123def456ghi789jkl012mno345pq",
    "new_password": "MyNewPassword789!"
  }'
```

---

### JWT Token Structure

**Access Token Payload:**
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",  // user_id
  "role": "user",
  "exp": 1704470400,  // Expiry timestamp (30 minutes)
  "iat": 1704468600   // Issued at timestamp
}
```

**Refresh Token Payload:**
```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",  // user_id
  "exp": 1705075200,  // Expiry timestamp (7 days)
  "iat": 1704468600   // Issued at timestamp
}
```

---

### Authentication Flow

**Luồng đăng nhập và sử dụng API:**

```
1. User đăng ký/đăng nhập
   → Server trả về access_token và refresh_token

2. Client lưu tokens (localStorage/secure cookie)

3. Mọi request tiếp theo, client gửi header:
   Authorization: Bearer <access_token>

4. Server verify access_token:
   - Decode JWT
   - Kiểm tra signature
   - Kiểm tra expiry
   - Kiểm tra password_changed_at
   → Inject current_user vào route handler

5. Khi access_token hết hạn (30 phút):
   - Client call /auth/refresh với refresh_token
   - Server trả về tokens mới
   - Client update tokens

6. Khi user logout:
   - Client call /auth/logout với refresh_token
   - Client xóa tokens khỏi storage
   - Server revoke refresh_token
```

---

### Security Best Practices

**1. Password Security:**
- Minimum 8 characters
- Hash với Argon2/Bcrypt (không lưu plaintext)
- Server không bao giờ trả về password trong response

**2. Token Security:**
- Access token short-lived (30 minutes)
- Refresh token long-lived nhưng có thể revoke
- Tokens gửi qua HTTPS only
- Refresh token hash trước khi lưu DB

**3. Session Management:**
- Có thể xem danh sách thiết bị đang đăng nhập
- Có thể logout từ xa (revoke specific session)
- Logout all devices khi đổi password

**4. Rate Limiting:**
- Login: 5 requests/minute/IP
- Forgot password: 3 requests/hour/email
- Register: 10 requests/hour/IP

**5. Input Validation:**
- Email format check
- Password strength check
- SQL injection prevention (ORM)
- XSS prevention (output escaping)

---
## 2. USERS

Module Users cung cấp thông tin về người dùng hiện tại và profile.

**Tag:** `Users`

**Endpoints:**
- GET /users/me - Lấy thông tin user hiện tại

---

### 2.1. Lấy thông tin user hiện tại (Get Current User Info)

Lấy thông tin đầy đủ về user đang đăng nhập, bao gồm user info và profile.

**Endpoint:** `GET /api/v1/users/me`

**Authentication:** Required (Bearer token)

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:** Không có (GET request)

**Success Response (200 OK):**

```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "username": "john_doe",
    "email": "john.doe@example.com",
    "role": "user",
    "created_at": "2025-12-15T10:30:00Z"
  },
  "profile": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "full_name": "John Doe",
    "gender": "male",
    "date_of_birth": "1990-05-15",
    "height_cm_default": 175.5
  }
}
```

**Response Schema:**

| Field | Type | Description |
|-------|------|-------------|
| user | object | Thông tin user |
| user.id | string (UUID) | User ID |
| user.username | string | Tên đăng nhập |
| user.email | string | Email |
| user.role | string | Vai trò ("user" hoặc "admin") |
| user.created_at | string (datetime) | Ngày tham gia |
| profile | object | Thông tin profile |
| profile.user_id | string (UUID) | User ID (FK) |
| profile.full_name | string \| null | Họ và tên |
| profile.gender | string \| null | Giới tính ("male", "female") |
| profile.date_of_birth | string \| null | Ngày sinh (YYYY-MM-DD) |
| profile.height_cm_default | number \| null | Chiều cao mặc định (cm) |

**Error Responses:**

**401 Unauthorized - Chưa đăng nhập hoặc token không hợp lệ:**
```json
{
  "detail": "Not authenticated"
}
```

**401 Unauthorized - Token hết hạn:**
```json
{
  "detail": "Token expired"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal error"
}
```

**Business Logic:**

1. Decode JWT access token từ Authorization header
2. Lấy user_id từ token
3. Query user từ database
4. Refresh user object để đảm bảo dữ liệu mới nhất
5. Lấy profile của user (relationship)
6. Format và trả về response

**Use Cases:**
- Hiển thị thông tin user trên UI (navbar, profile page)
- Kiểm tra role để show/hide admin features
- Lấy thông tin profile để pre-fill forms
- Verify user vẫn còn active và có quyền

**Ví dụ sử dụng:**

```bash
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**JavaScript Example:**

```javascript
const response = await fetch('http://localhost:8000/api/v1/users/me', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

const data = await response.json();
console.log(data.user.username); // "john_doe"
console.log(data.profile.full_name); // "John Doe"
```

---

## 3. SETTINGS

Module Settings cung cấp các chức năng cài đặt tài khoản người dùng.

**Tag:** `Settings`

**Endpoints:**
- PATCH /settings/password - Đổi mật khẩu

---

### 3.1. Đổi mật khẩu (Change Password)

Thay đổi mật khẩu cho user đang đăng nhập. Yêu cầu xác thực mật khẩu cũ.

**Endpoint:** `PATCH /api/v1/settings/password`

**Authentication:** Required (Bearer token)

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "current_password": "OldPassword123!",
  "new_password": "NewSecurePass456!"
}
```

**Request Schema:**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| current_password | string | Yes | - | Mật khẩu hiện tại |
| new_password | string | Yes | 8-128 chars | Mật khẩu mới |

**Success Response (204 No Content):**

Không có response body, chỉ trả về status code 204.

**Error Responses:**

**401 Unauthorized - Mật khẩu hiện tại sai:**
```json
{
  "detail": "Current password is incorrect"
}
```

**401 Unauthorized - Chưa đăng nhập:**
```json
{
  "detail": "Not authenticated"
}
```

**400 Bad Request - Mật khẩu mới giống mật khẩu cũ:**
```json
{
  "detail": "New password must be different from current password"
}
```

**422 Unprocessable Entity - Mật khẩu mới quá ngắn:**
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "new_password"],
      "msg": "String should have at least 8 characters",
      "input": "short",
      "ctx": {"min_length": 8}
    }
  ]
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal error"
}
```

**Business Logic:**

1. Get current_user từ JWT token
2. Verify current_password:
   - Hash current_password và compare với password_hash trong DB
   - Nếu sai → 401 Unauthorized
3. Check new_password khác current_password:
   - Nếu giống → 400 Bad Request
4. Hash new_password bằng Argon2/Bcrypt
5. Update users.password_hash
6. Set users.password_changed_at = NOW()
7. Revoke tất cả refresh_sessions của user:
   - Set revoked_at = NOW() cho tất cả sessions
   - Force logout tất cả thiết bị
8. Commit transaction

**Security Features:**
- Yêu cầu xác thực mật khẩu cũ (không cho đổi tự do)
- Force logout tất cả thiết bị (phòng trường hợp bị hack)
- Password được hash trước khi lưu
- `password_changed_at` timestamp làm invalidate tất cả JWT cũ

**Lưu ý:**
- User phải đăng nhập lại sau khi đổi password
- Tất cả thiết bị khác đều bị logout
- Access tokens cũ sẽ invalid ngay lập tức (check password_changed_at)

**Ví dụ sử dụng:**

```bash
curl -X PATCH http://localhost:8000/api/v1/settings/password \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "OldPassword123!",
    "new_password": "NewSecurePass456!"
  }'
```

**JavaScript Example:**

```javascript
const response = await fetch('http://localhost:8000/api/v1/settings/password', {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    current_password: 'OldPassword123!',
    new_password: 'NewSecurePass456!'
  })
});

if (response.status === 204) {
  console.log('Password changed successfully');
  // Redirect to login page
  window.location.href = '/login';
}
```

**Workflow sau khi đổi password:**

```
1. User submit form đổi password
2. API trả về 204 No Content
3. Client xóa tokens khỏi storage
4. Client redirect về login page
5. User đăng nhập lại với password mới
6. Nhận tokens mới
```

---

## 4. BIOMETRICS

Module Biometrics cung cấp chức năng theo dõi cân nặng và chiều cao theo thời gian.

**Tag:** `Biometrics`

**Endpoints:**
- POST /biometrics - Tạo biometrics log mới
- GET /biometrics - Lấy danh sách logs
- GET /biometrics/latest - Lấy log mới nhất
- PATCH /biometrics/{biometric_id} - Update một log
- DELETE /biometrics/{biometric_id} - Xóa một log
- GET /biometrics/summary - Thống kê tổng hợp

---

### 4.1. Tạo biometrics log (Create Biometrics Log)

Tạo một record mới về cân nặng và/hoặc chiều cao. BMI sẽ tự động được tính nếu có đủ cả hai thông tin.

**Endpoint:** `POST /api/v1/biometrics`

**Authentication:** Required (Bearer token)

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**

```json
{
  "logged_at": "2026-01-05T08:00:00Z",
  "weight_kg": 75.5,
  "height_cm": 175.0
}
```

**Request Schema:**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| logged_at | string (datetime) | Yes | ISO 8601 format | Thời điểm đo |
| weight_kg | number | No | > 0, <= 700 | Cân nặng (kg) |
| height_cm | number | No | > 0, <= 300 | Chiều cao (cm) |

**Validation Rules:**
- Phải có ít nhất một trong hai: `weight_kg` hoặc `height_cm`
- Nếu có `weight_kg`: phải > 0 và <= 700
- Nếu có `height_cm`: phải > 0 và <= 300

**Success Response (201 Created):**

```json
{
  "id": 1234,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "logged_at": "2026-01-05T08:00:00Z",
  "weight_kg": 75.5,
  "height_cm": 175.0,
  "bmi": 24.6,
  "created_at": "2026-01-05T08:05:30Z"
}
```

**Response Schema:**

| Field | Type | Description |
|-------|------|-------------|
| id | integer | ID của log |
| user_id | string (UUID) | User ID |
| logged_at | string (datetime) | Thời điểm đo (do user set) |
| weight_kg | number \| null | Cân nặng (kg) |
| height_cm | number \| null | Chiều cao (cm) |
| bmi | number \| null | Chỉ số BMI (tự động tính) |
| created_at | string (datetime) | Thời điểm tạo record (server set) |

**BMI Calculation:**
```
BMI = weight_kg / (height_cm / 100)²

Example:
weight = 75.5 kg
height = 175 cm = 1.75 m
BMI = 75.5 / (1.75)² = 75.5 / 3.0625 = 24.65
```

**Error Responses:**

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

**422 Unprocessable Entity - Thiếu cả weight và height:**
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body"],
      "msg": "Phải nhập ít nhất một trong hai: cân nặng hoặc chiều cao"
    }
  ]
}
```

**422 Unprocessable Entity - Weight vượt quá giới hạn:**
```json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["body", "weight_kg"],
      "msg": "Input should be less than or equal to 700"
    }
  ]
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal error"
}
```

**Business Logic:**

1. Validate request data
2. Tạo BiometricsLog record với:
   - user_id từ current_user
   - logged_at từ request
   - weight_kg, height_cm từ request
3. Nếu có cả weight và height:
   - Tính BMI = weight_kg / (height_cm/100)²
   - Round đến 1 chữ số thập phân
4. Lưu vào database
5. Trả về log vừa tạo

**Use Cases:**
- User nhập cân nặng sau khi cân
- User nhập chiều cao (update lần đầu hoặc khi thay đổi)
- App tự động sync từ thiết bị đo (smart scale)
- Theo dõi tiến trình giảm cân/tăng cân

**Ví dụ sử dụng:**

**Case 1: Nhập cả cân nặng và chiều cao**
```bash
curl -X POST http://localhost:8000/api/v1/biometrics \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "logged_at": "2026-01-05T08:00:00Z",
    "weight_kg": 75.5,
    "height_cm": 175.0
  }'
```

**Case 2: Chỉ nhập cân nặng (chiều cao giữ nguyên)**
```bash
curl -X POST http://localhost:8000/api/v1/biometrics \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "logged_at": "2026-01-05T20:00:00Z",
    "weight_kg": 75.0
  }'
```

**Case 3: Chỉ nhập chiều cao (update profile)**
```bash
curl -X POST http://localhost:8000/api/v1/biometrics \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "logged_at": "2026-01-05T10:00:00Z",
    "height_cm": 176.0
  }'
```

---

### 4.2. Lấy danh sách logs (List Biometrics Logs)

Lấy danh sách các biometrics logs của user trong khoảng thời gian. Hỗ trợ filter theo date range.

**Endpoint:** `GET /api/v1/biometrics`

**Authentication:** Required (Bearer token)

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**

| Parameter | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| from | string (date) | No | None | YYYY-MM-DD | Ngày bắt đầu (inclusive) |
| to | string (date) | No | None | YYYY-MM-DD | Ngày kết thúc (inclusive) |
| limit | integer | No | 100 | 1-365 | Số records tối đa |

**Success Response (200 OK):**

```json
{
  "items": [
    {
      "id": 1235,
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "logged_at": "2026-01-05T20:00:00Z",
      "weight_kg": 75.0,
      "height_cm": 175.0,
      "bmi": 24.5,
      "created_at": "2026-01-05T20:05:00Z"
    },
    {
      "id": 1234,
      "user_id": "550e8400-e29b-41d4-a716-446655440000",
      "logged_at": "2026-01-05T08:00:00Z",
      "weight_kg": 75.5,
      "height_cm": 175.0,
      "bmi": 24.6,
      "created_at": "2026-01-05T08:05:30Z"
    }
  ]
}
```

**Response Schema:**

| Field | Type | Description |
|-------|------|-------------|
| items | array | Danh sách logs |
| items[].id | integer | Log ID |
| items[].user_id | string (UUID) | User ID |
| items[].logged_at | string (datetime) | Thời điểm đo |
| items[].weight_kg | number \| null | Cân nặng |
| items[].height_cm | number \| null | Chiều cao |
| items[].bmi | number \| null | BMI |
| items[].created_at | string (datetime) | Thời điểm tạo |

**Sorting:**
- Logs được sắp xếp theo `logged_at` DESC (mới nhất trước)

**Error Responses:**

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

**422 Unprocessable Entity - Invalid date format:**
```json
{
  "detail": [
    {
      "type": "date_parsing",
      "loc": ["query", "from"],
      "msg": "Input should be a valid date"
    }
  ]
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal error"
}
```

**Business Logic:**

1. Get current_user từ JWT
2. Build query:
   - Filter by user_id
   - If from_date: Filter logged_at >= from_date 00:00:00
   - If to_date: Filter logged_at <= to_date 23:59:59
   - Order by logged_at DESC
   - Limit results
3. Execute query
4. Return list

**Use Cases:**
- Hiển thị history trên profile page
- Vẽ biểu đồ weight chart theo thời gian
- Export data ra CSV/Excel
- Phân tích xu hướng weight loss/gain

**Ví dụ sử dụng:**

**Case 1: Lấy tất cả logs (mới nhất, limit 100)**
```bash
curl -X GET http://localhost:8000/api/v1/biometrics \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Case 2: Lấy logs trong tháng 12/2025**
```bash
curl -X GET "http://localhost:8000/api/v1/biometrics?from=2025-12-01&to=2025-12-31" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Case 3: Lấy 30 logs gần nhất**
```bash
curl -X GET "http://localhost:8000/api/v1/biometrics?limit=30" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Case 4: Lấy logs từ ngày 1/1/2026 đến nay**
```bash
curl -X GET "http://localhost:8000/api/v1/biometrics?from=2026-01-01" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

### 4.3. Lấy log mới nhất (Get Latest Biometrics)

Lấy biometrics log mới nhất của user. Dùng để hiển thị cân nặng/chiều cao hiện tại.

**Endpoint:** `GET /api/v1/biometrics/latest`

**Authentication:** Required (Bearer token)

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:** Không có (GET request)

**Success Response (200 OK):**

```json
{
  "id": 1235,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "logged_at": "2026-01-05T20:00:00Z",
  "weight_kg": 75.0,
  "height_cm": 175.0,
  "bmi": 24.5,
  "created_at": "2026-01-05T20:05:00Z"
}
```

**Response Schema:** Giống như BiometricsLogResponse (single object, not array)

**Error Responses:**

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

**404 Not Found - User chưa có log nào:**
```json
{
  "detail": "No biometrics logs found for this user"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal error"
}
```

**Business Logic:**

1. Get current_user từ JWT
2. Query:
   - Filter by user_id
   - Order by logged_at DESC
   - Limit 1
3. If không tìm thấy → 404
4. Return log

**Use Cases:**
- Hiển thị cân nặng hiện tại trên dashboard
- Dùng cho goal calculation (latest weight/height)
- Pre-fill form khi tạo log mới
- Show current BMI

**Ví dụ sử dụng:**

```bash
curl -X GET http://localhost:8000/api/v1/biometrics/latest \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**JavaScript Example:**

```javascript
const response = await fetch('http://localhost:8000/api/v1/biometrics/latest', {
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

if (response.ok) {
  const data = await response.json();
  console.log(`Current weight: ${data.weight_kg} kg`);
  console.log(`Current BMI: ${data.bmi}`);
} else if (response.status === 404) {
  console.log('No biometrics data yet. Please add your first log.');
}
```

---

### 4.4. Update biometrics log (Update Biometrics Record)

Cập nhật một log hiện có. Có thể update một hoặc nhiều fields. BMI sẽ tự động tính lại nếu weight/height thay đổi.

**Endpoint:** `PATCH /api/v1/biometrics/{biometric_id}`

**Authentication:** Required (Bearer token)

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| biometric_id | integer | Yes | ID của log cần update |

**Request Body (Partial Update):**

```json
{
  "weight_kg": 74.8
}
```

Hoặc update nhiều fields:

```json
{
  "logged_at": "2026-01-05T08:30:00Z",
  "weight_kg": 74.8,
  "height_cm": 175.5
}
```

**Request Schema:**

| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| logged_at | string (datetime) | No | ISO 8601 | Thời điểm đo (update nếu cần) |
| weight_kg | number | No | > 0, <= 700 | Cân nặng mới |
| height_cm | number | No | > 0, <= 300 | Chiều cao mới |

**Success Response (200 OK):**

```json
{
  "id": 1234,
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "logged_at": "2026-01-05T08:30:00Z",
  "weight_kg": 74.8,
  "height_cm": 175.5,
  "bmi": 24.3,
  "created_at": "2026-01-05T08:05:30Z"
}
```

**Response Schema:** Giống như BiometricsLogResponse (updated log)

**Error Responses:**

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

**404 Not Found - Log không tồn tại hoặc không thuộc về user:**
```json
{
  "detail": "Biometrics log not found"
}
```

**422 Unprocessable Entity - Invalid data:**
```json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["body", "weight_kg"],
      "msg": "Input should be less than or equal to 700"
    }
  ]
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal error"
}
```

**Business Logic:**

1. Get current_user từ JWT
2. Query log by ID và user_id:
   - Nếu không tìm thấy → 404
3. Update các fields được gửi (partial update):
   - Chỉ update fields có trong request
   - Giữ nguyên fields không có trong request
4. Recalculate BMI nếu weight hoặc height thay đổi:
   - Chỉ tính BMI nếu có cả weight_kg và height_cm
5. Commit transaction
6. Return updated log

**Use Cases:**
- Sửa lỗi nhập liệu
- Cập nhật thời gian đo (logged_at)
- Bổ sung chiều cao nếu ban đầu chỉ nhập cân nặng
- Fine-tune data từ thiết bị đo

**Ví dụ sử dụng:**

**Case 1: Chỉ update cân nặng**
```bash
curl -X PATCH http://localhost:8000/api/v1/biometrics/1234 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "weight_kg": 74.8
  }'
```

**Case 2: Update cả weight và height**
```bash
curl -X PATCH http://localhost:8000/api/v1/biometrics/1234 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "weight_kg": 74.8,
    "height_cm": 175.5
  }'
```

**Case 3: Chỉ update thời gian đo**
```bash
curl -X PATCH http://localhost:8000/api/v1/biometrics/1234 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "logged_at": "2026-01-05T07:00:00Z"
  }'
```

---

### 4.5. Xóa biometrics log (Delete Biometrics Record)

Xóa vĩnh viễn một biometrics log. Đây là hard delete, không thể khôi phục.

**Endpoint:** `DELETE /api/v1/biometrics/{biometric_id}`

**Authentication:** Required (Bearer token)

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| biometric_id | integer | Yes | ID của log cần xóa |

**Request Body:** Không có (DELETE request)

**Success Response (204 No Content):**

Không có response body, chỉ trả về status code 204.

**Error Responses:**

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

**404 Not Found - Log không tồn tại hoặc không thuộc về user:**
```json
{
  "detail": "Biometrics log not found"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal error"
}
```

**Business Logic:**

1. Get current_user từ JWT
2. Query log by ID và user_id:
   - Nếu không tìm thấy → 404
3. Delete log from database (hard delete)
4. Commit transaction
5. Return 204 No Content

**Security:**
- User chỉ có thể xóa logs của chính mình
- Không thể xóa logs của user khác (403 nếu cố gắng)

**Lưu ý:**
- Đây là hard delete (xóa vĩnh viễn)
- Không thể undo sau khi xóa
- Cân nhắc implement soft delete nếu cần lưu trữ lịch sử

**Use Cases:**
- Xóa entry nhập nhầm
- Xóa duplicate entries
- Dọn dẹp dữ liệu test

**Ví dụ sử dụng:**

```bash
curl -X DELETE http://localhost:8000/api/v1/biometrics/1234 \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**JavaScript Example:**

```javascript
const response = await fetch('http://localhost:8000/api/v1/biometrics/1234', {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});

if (response.status === 204) {
  console.log('Biometrics log deleted successfully');
  // Refresh list
  fetchBiometricsList();
}
```

---

### 4.6. Thống kê biometrics (Biometrics Summary)

Lấy thống kê tổng hợp về biometrics trong khoảng thời gian (trung bình, min, max, xu hướng).

**Endpoint:** `GET /api/v1/biometrics/summary`

**Authentication:** Required (Bearer token)

**Request Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| from | string (date) | Yes | Ngày bắt đầu (YYYY-MM-DD) |
| to | string (date) | Yes | Ngày kết thúc (YYYY-MM-DD) |

**Success Response (200 OK):**

```json
{
  "total_logs": 15,
  "weight_summary": {
    "average": 75.2,
    "min": 74.5,
    "max": 76.0,
    "change": -1.5,
    "change_percentage": -1.96
  },
  "height_summary": {
    "average": 175.3,
    "min": 175.0,
    "max": 176.0
  },
  "bmi_summary": {
    "average": 24.4,
    "min": 24.0,
    "max": 24.8
  }
}
```

**Response Schema:**

| Field | Type | Description |
|-------|------|-------------|
| total_logs | integer | Tổng số logs trong khoảng thời gian |
| weight_summary | object \| null | Thống kê cân nặng |
| weight_summary.average | number | Cân nặng trung bình (kg) |
| weight_summary.min | number | Cân nặng thấp nhất (kg) |
| weight_summary.max | number | Cân nặng cao nhất (kg) |
| weight_summary.change | number | Thay đổi = latest - first (kg) |
| weight_summary.change_percentage | number | Phần trăm thay đổi (%) |
| height_summary | object \| null | Thống kê chiều cao |
| height_summary.average | number | Chiều cao trung bình (cm) |
| height_summary.min | number | Chiều cao thấp nhất (cm) |
| height_summary.max | number | Chiều cao cao nhất (cm) |
| bmi_summary | object \| null | Thống kê BMI |
| bmi_summary.average | number | BMI trung bình |
| bmi_summary.min | number | BMI thấp nhất |
| bmi_summary.max | number | BMI cao nhất |

**Error Responses:**

**401 Unauthorized:**
```json
{
  "detail": "Not authenticated"
}
```

**422 Unprocessable Entity - Missing required parameters:**
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["query", "from"],
      "msg": "Field required"
    }
  ]
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Internal error"
}
```

**Business Logic:**

1. Get current_user từ JWT
2. Query all logs trong khoảng [from_date, to_date]
3. Aggregate calculations:
   - COUNT(*)
   - AVG(weight_kg), MIN(weight_kg), MAX(weight_kg)
   - AVG(height_cm), MIN(height_cm), MAX(height_cm)
   - AVG(bmi), MIN(bmi), MAX(bmi)
4. Calculate change:
   - Get first log và last log trong period
   - change = last_weight - first_weight
   - change_percentage = (change / first_weight) × 100
5. Return summary

**Use Cases:**
- Hiển thị progress summary trên dashboard
- Vẽ biểu đồ thống kê
- Generate báo cáo tiến trình
- Track weight loss/gain rate

**Ví dụ sử dụng:**

**Case 1: Thống kê tháng 12/2025**
```bash
curl -X GET "http://localhost:8000/api/v1/biometrics/summary?from=2025-12-01&to=2025-12-31" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Case 2: Thống kê 30 ngày gần nhất**
```bash
# Assuming today is 2026-01-05
curl -X GET "http://localhost:8000/api/v1/biometrics/summary?from=2025-12-06&to=2026-01-05" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**JavaScript Example:**

```javascript
const from = '2025-12-01';
const to = '2025-12-31';

const response = await fetch(
  `http://localhost:8000/api/v1/biometrics/summary?from=${from}&to=${to}`,
  {
    headers: {
      'Authorization': `Bearer ${accessToken}`
    }
  }
);

const summary = await response.json();

console.log(`Total logs: ${summary.total_logs}`);
console.log(`Average weight: ${summary.weight_summary.average} kg`);
console.log(`Weight change: ${summary.weight_summary.change} kg (${summary.weight_summary.change_percentage}%)`);
```

---

### BMI Classification (Tham khảo)

BMI được phân loại theo tiêu chuẩn WHO:

| BMI Range | Classification | Health Risk |
|-----------|----------------|-------------|
| < 18.5 | Underweight (Thiếu cân) | Tăng nguy cơ suy dinh dưỡng |
| 18.5 - 24.9 | Normal weight (Bình thường) | Lý tưởng |
| 25.0 - 29.9 | Overweight (Thừa cân) | Tăng nguy cơ bệnh |
| 30.0 - 34.9 | Obesity Class I (Béo phì độ 1) | Nguy cơ cao |
| 35.0 - 39.9 | Obesity Class II (Béo phì độ 2) | Nguy cơ rất cao |
| >= 40.0 | Obesity Class III (Béo phì độ 3) | Nguy cơ cực cao |

**Lưu ý:**
- BMI không phân biệt giữa muscle mass và fat mass
- Không chính xác cho vận động viên, phụ nữ mang thai, người cao tuổi
- Nên kết hợp với các chỉ số khác: body fat percentage, waist circumference

---
