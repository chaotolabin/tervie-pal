# Tervie Pal - Hệ thống theo dõi sức khỏe cá nhân

## Mục lục

1. [Giới thiệu](#giới-thiệu)
2. [Tính năng chính](#tính-năng-chính)
3. [Công nghệ sử dụng](#công-nghệ-sử-dụng)
4. [Yêu cầu hệ thống](#yêu-cầu-hệ-thống)
5. [Cài đặt](#cài-đặt)
   - [Cài đặt bằng Docker (Khuyến nghị)](#cài-đặt-bằng-docker-khuyến-nghị)
   - [Cài đặt thủ công](#cài-đặt-thủ-công)
6. [Cấu hình](#cấu-hình)
7. [Chạy dự án](#chạy-dự-án)
8. [Hướng dẫn sử dụng](#hướng-dẫn-sử-dụng)
9. [API Documentation](#api-documentation)
10. [Cấu trúc dự án](#cấu-trúc-dự-án)
11. [Troubleshooting](#troubleshooting)

---

## Giới thiệu

Tervie Pal là một hệ thống web hỗ trợ theo dõi sức khỏe cá nhân và quản lý thói quen sinh hoạt. Hệ thống cho phép người dùng:

- Nhập và theo dõi thông tin sức khỏe cá nhân
- Ghi nhận hoạt động thể chất và chế độ ăn uống hàng ngày
- Tính toán tự động các chỉ số dinh dưỡng (calories, protein, carbs, fat)
- Theo dõi tiến độ đạt mục tiêu sức khỏe
- Tương tác với cộng đồng qua blog và chia sẻ kinh nghiệm
- Nhận tư vấn từ AI chatbot về dinh dưỡng và sức khỏe

Đây là dự án cuối kỳ môn **Cơ sở dữ liệu Web và Hệ thống thông tin**.

---

## Tính năng chính

### 1. Quản lý hồ sơ người dùng
- Đăng ký và đăng nhập với xác thực JWT
- Quản lý thông tin cá nhân (họ tên, giới tính, ngày sinh, chiều cao)
- Theo dõi lịch sử cân nặng và các chỉ số sinh trắc học
- Thiết lập mục tiêu sức khỏe (giảm cân, tăng cân, duy trì, tăng cơ, cải thiện sức khỏe)

### 2. Theo dõi dinh dưỡng
- Tìm kiếm thực phẩm từ cơ sở dữ liệu (global + custom)
- Ghi nhận bữa ăn theo loại (sáng, trưa, tối, đồ ăn vặt)
- Tính toán tự động calories và macros (protein, carbs, fat) dựa trên khẩu phần
- Tạo thực phẩm tùy chỉnh cho riêng mình
- Đóng góp thực phẩm cho cộng đồng (cần admin duyệt)

### 3. Theo dõi bài tập
- Tìm kiếm bài tập từ cơ sở dữ liệu (global + custom)
- Tính toán calories đốt cháy dựa trên MET value, thời gian và cân nặng
- Ghi nhận thời gian tập luyện
- Tạo bài tập tùy chỉnh
- Đóng góp bài tập cho cộng đồng

### 4. Dashboard và thống kê
- Tổng quan hôm nay: Calories đã ăn, đã đốt, net calories
- Biểu đồ theo dõi cân nặng (7 lần cân gần nhất)
- Biểu đồ calories (30 ngày gần nhất)
- Tóm tắt macros: Protein, Carbs, Fat so với mục tiêu
- Quick Add: Thêm nhanh thực phẩm, bài tập, cân nặng

### 5. Streak System
- Theo dõi chuỗi ngày hoàn thành mục tiêu calories
- Hiển thị current streak và longest streak
- Trạng thái: Green (hoàn thành đúng hạn), Yellow (hoàn thành trễ), Gray (chưa hoàn thành)

### 6. Blog và cộng đồng
- Tạo bài viết với text và media (ảnh/video)
- Hashtags tự động
- Like và Save bài viết
- Xem feed: Global, Trending, Personal
- Upload media qua ImageKit.io

### 7. AI Chatbot
- Chat về dinh dưỡng và sức khỏe
- Sử dụng Google Gemini AI
- RAG (Retrieval Augmented Generation) với ChromaDB
- Hiểu context từ profile và goals của user

### 8. Hỗ trợ
- Gửi ticket báo lỗi hoặc yêu cầu hỗ trợ
- Admin quản lý và xử lý tickets

### 9. Admin Panel
- Quản lý người dùng
- Duyệt bài viết và contributions (foods/exercises)
- Quản lý support tickets
- Xem analytics và thống kê hệ thống

---

## Công nghệ sử dụng

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL (Supabase)
- **ORM**: SQLAlchemy 2.0
- **Migration**: Alembic
- **Authentication**: JWT (Access + Refresh tokens)
- **Password Hashing**: Argon2
- **AI**: Google Gemini API
- **Vector Database**: ChromaDB
- **File Storage**: ImageKit.io
- **Email**: SMTP (Gmail)

### Frontend
- **Framework**: React 18 + TypeScript
- **Build Tool**: Vite
- **UI Library**: Radix UI
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Form Handling**: React Hook Form

### DevOps
- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx (production frontend)

---

## Yêu cầu hệ thống

### Tối thiểu
- **OS**: Windows 10/11, macOS 10.15+, hoặc Linux
- **RAM**: 4GB
- **Docker**: Docker Desktop 4.0+ (nếu dùng Docker)
- **Node.js**: 18+ (nếu cài đặt thủ công frontend)
- **Python**: 3.11+ (nếu cài đặt thủ công backend)

### Khuyến nghị
- **RAM**: 8GB trở lên
- **Docker**: Docker Desktop mới nhất
- **Database**: PostgreSQL 14+ (hoặc Supabase cloud)

---

## Cài đặt

### Cài đặt bằng Docker (Khuyến nghị)

#### Bước 1: Cài đặt Docker Desktop
1. Tải Docker Desktop từ [docker.com](https://www.docker.com/products/docker-desktop)
2. Cài đặt và khởi động Docker Desktop
3. Đảm bảo Docker đang chạy (icon Docker xuất hiện ở system tray)

#### Bước 2: Clone hoặc giải nén dự án
```bash
# Nếu clone từ Git
git clone <repository-url>
cd tervie-pal

# Hoặc giải nén file zip và mở terminal tại thư mục tervie-pal
```

#### Bước 3: Cấu hình môi trường
Tạo file `.env` trong thư mục `backend/` với nội dung:

```env
PROJECT_NAME=Tervie Pal
PROJECT_VERSION=1.0.0
DATABASE_URL=postgresql://user:password@host:port/database
GEMINI_API_KEY=your-gemini-api-key
CHROMA_DB_PATH=./chroma_db
FRONTEND_URL=http://localhost
IMAGEKIT_PRIVATE_KEY=your-imagekit-private-key
IMAGEKIT_PUBLIC_KEY=your-imagekit-public-key
IMAGEKIT_URL=your-imagekit-url
SMTP_ENABLED=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**Lưu ý**: 
- Thay thế các giá trị placeholder bằng thông tin thực tế
- Đối với Gmail, cần tạo App Password (không phải mật khẩu thường)
- Nếu không dùng chatbot, có thể bỏ qua `GEMINI_API_KEY`
- Nếu không dùng ImageKit, có thể bỏ qua các key ImageKit

#### Bước 4: Chạy dự án
```bash
# Build và khởi động containers
docker-compose up -d --build

# Xem logs
docker-compose logs -f

# Kiểm tra trạng thái
docker-compose ps
```

#### Bước 5: Chạy database migrations
```bash
# Vào container backend
docker exec -it tervie-backend bash

# Chạy migrations
alembic upgrade head

# Thoát container
exit
```

#### Bước 6: Truy cập ứng dụng
- **Website**: http://localhost
- **API Documentation**: http://localhost:8000/api/v1/docs
- **API ReDoc**: http://localhost:8000/api/v1/redoc

#### Dừng dự án
```bash
# Dừng containers (giữ data)
docker-compose stop

# Dừng và xóa containers (giữ data)
docker-compose down

# Dừng và xóa containers + volumes (xóa data)
docker-compose down -v
```

---

### Cài đặt thủ công

#### Backend

##### Bước 1: Cài đặt Python và dependencies
```bash
cd backend

# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

##### Bước 2: Cấu hình môi trường
Tạo file `.env` trong thư mục `backend/` (xem mẫu ở phần Docker)

##### Bước 3: Chạy database migrations
```bash
alembic upgrade head
```

##### Bước 4: Khởi động backend
```bash
# Development mode (auto-reload)
fastapi dev app/main.py

# Hoặc
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend sẽ chạy tại: http://localhost:8000

#### Frontend

##### Bước 1: Cài đặt Node.js và dependencies
```bash
cd frontend

# Cài đặt dependencies
npm install
```

##### Bước 2: Cấu hình API endpoint
Kiểm tra file `frontend/src/app/components/lib/api.ts`:
- Development: `http://localhost:8000/api/v1`
- Production: Cập nhật URL backend thực tế

##### Bước 3: Khởi động frontend
```bash
# Development mode
npm run dev

# Build production
npm run build
```

Frontend sẽ chạy tại: http://localhost:5173 (development)

---

## Cấu hình

### Database
- Sử dụng PostgreSQL (Supabase hoặc self-hosted)
- Connection string format: `postgresql://user:password@host:port/database`
- Đảm bảo database đã được tạo trước khi chạy migrations

### Google Gemini API
1. Truy cập [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Tạo API key
3. Thêm vào `.env`: `GEMINI_API_KEY=your-api-key`

### ImageKit.io (Tùy chọn)
1. Đăng ký tài khoản tại [imagekit.io](https://imagekit.io)
2. Lấy Private Key, Public Key và URL
3. Thêm vào `.env`

### SMTP Email (Tùy chọn)
1. Với Gmail:
   - Bật 2-Step Verification
   - Tạo App Password tại [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
   - Sử dụng App Password (16 ký tự) thay vì mật khẩu thường

---

## Chạy dự án

### Development Mode

#### Backend (Manual)
```bash
cd backend
source venv/bin/activate  # hoặc venv\Scripts\activate trên Windows
fastapi dev app/main.py
```

#### Frontend (Manual)
```bash
cd frontend
npm run dev
```

### Production Mode (Docker)
```bash
docker-compose up -d --build
```

---

## Hướng dẫn sử dụng

### Đăng ký tài khoản
1. Truy cập http://localhost
2. Click "Đăng ký" hoặc "Sign Up"
3. Điền thông tin:
   - Username (3-32 ký tự)
   - Email (phải hợp lệ và chưa được sử dụng)
   - Password (8-128 ký tự)
   - Họ và tên
   - Giới tính
   - Ngày sinh
   - Chiều cao (cm)
   - Cân nặng hiện tại (kg)
   - Mục tiêu sức khỏe
   - Mức độ hoạt động
4. Click "Đăng ký"
5. Hệ thống tự động tạo profile, goal và biometric log ban đầu

### Đăng nhập
1. Click "Đăng nhập" hoặc "Login"
2. Nhập email/username và password
3. Click "Đăng nhập"
4. Hệ thống lưu access token và refresh token vào localStorage

### Dashboard Home
- Xem tổng quan hôm nay: Calories, Macros
- Xem biểu đồ cân nặng và calories
- Sử dụng Quick Add để thêm nhanh food/exercise/biometrics

### Ghi nhận dinh dưỡng
1. Vào tab "Dinh dưỡng"
2. Chọn bữa ăn (Sáng, Trưa, Tối, Đồ ăn vặt)
3. Tìm kiếm thực phẩm
4. Chọn khẩu phần (cups, grams, servings)
5. Nhập số lượng
6. Click "Thêm"
7. Hệ thống tự động tính calories và macros

### Ghi nhận bài tập
1. Vào tab "Tập luyện"
2. Tìm kiếm bài tập
3. Nhập thời gian tập (phút)
4. Click "Thêm"
5. Hệ thống tự động tính calories đốt cháy dựa trên cân nặng hiện tại

### Tạo bài viết blog
1. Vào tab "Tervie Blog"
2. Click "Tạo bài viết"
3. Nhập tiêu đề và nội dung
4. Upload ảnh/video (nếu có)
5. Thêm hashtags
6. Click "Đăng"
7. Admin sẽ duyệt bài viết (nếu cần)

### Sử dụng AI Chatbot
1. Click icon chatbot ở góc dưới bên phải
2. Nhập câu hỏi về dinh dưỡng hoặc sức khỏe
3. Chatbot sẽ trả lời dựa trên context của bạn

### Xem và chỉnh sửa profile
1. Click vào avatar/username ở header
2. Chọn "Cá nhân" hoặc vào tab "Cá nhân"
3. Xem và chỉnh sửa thông tin
4. Cập nhật mục tiêu sức khỏe
5. Xem lịch sử cân nặng

### Gửi ticket hỗ trợ
1. Vào tab "Trợ giúp"
2. Click "Gửi yêu cầu hỗ trợ"
3. Điền tiêu đề và mô tả
4. Click "Gửi"
5. Admin sẽ xem và phản hồi

---

## API Documentation

### Base URL
- Development: `http://localhost:8000/api/v1`
- Production: `https://tervie-backend.onrender.com/api/v1`

### Authentication
Hầu hết các endpoints yêu cầu authentication:
```
Authorization: Bearer <access_token>
```

### Endpoints chính

#### Authentication
- `POST /auth/register` - Đăng ký
- `POST /auth/login` - Đăng nhập
- `POST /auth/refresh` - Refresh token
- `POST /auth/logout` - Đăng xuất
- `POST /auth/forgot-password` - Yêu cầu reset password
- `POST /auth/reset-password` - Đặt lại password

#### Users
- `GET /users/me` - Lấy thông tin user hiện tại
- `PATCH /users/me` - Cập nhật thông tin user

#### Foods
- `GET /foods` - Tìm kiếm thực phẩm
- `POST /foods` - Tạo thực phẩm custom
- `GET /foods/{id}` - Lấy chi tiết thực phẩm

#### Exercises
- `GET /exercises` - Tìm kiếm bài tập
- `POST /exercises` - Tạo bài tập custom
- `GET /exercises/{id}` - Lấy chi tiết bài tập

#### Logs
- `POST /logs/food` - Ghi nhận bữa ăn
- `POST /logs/exercise` - Ghi nhận bài tập
- `GET /logs/summary/{date}` - Lấy tổng hợp ngày
- `GET /logs/food/{date}` - Lấy nhật ký bữa ăn
- `GET /logs/exercise/{date}` - Lấy nhật ký bài tập

#### Goals
- `GET /goals` - Lấy mục tiêu hiện tại
- `PATCH /goals` - Cập nhật mục tiêu

#### Biometrics
- `POST /biometrics` - Ghi nhận cân nặng/chiều cao
- `GET /biometrics` - Lấy lịch sử

#### Streak
- `GET /streak` - Lấy thông tin streak

#### Blog
- `GET /blog/posts` - Lấy danh sách bài viết
- `POST /blog/posts` - Tạo bài viết
- `GET /blog/posts/{id}` - Lấy chi tiết bài viết
- `POST /blog/posts/{id}/like` - Like bài viết
- `POST /blog/posts/{id}/save` - Save bài viết

#### Chatbot
- `POST /chatbot/chat` - Chat với AI

#### Support
- `POST /support/tickets` - Tạo ticket
- `GET /support/tickets` - Lấy danh sách tickets

Xem chi tiết tại: http://localhost:8000/api/v1/docs (Swagger UI)

---

## Cấu trúc dự án

```
tervie-pal/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/          # API endpoints
│   │   │   ├── deps.py          # Dependencies (auth, db)
│   │   │   └── schemas/         # Pydantic schemas
│   │   ├── core/
│   │   │   ├── database.py      # SQLAlchemy setup
│   │   │   └── settings.py      # Settings từ .env
│   │   ├── models/              # SQLAlchemy models
│   │   ├── repositories/        # Data access layer
│   │   ├── services/            # Business logic
│   │   ├── middleware/          # Middleware
│   │   └── utils/               # Utilities
│   ├── alembic/                 # Database migrations
│   ├── chroma_db/              # ChromaDB data
│   ├── Dockerfile
│   ├── requirements.txt
│   └── main.py                 # FastAPI app entry
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── App.tsx          # Main router
│   │   │   ├── components/      # React components
│   │   │   ├── hooks/           # Custom hooks
│   │   │   ├── types/           # TypeScript types
│   │   │   └── styles/          # CSS files
│   │   └── main.jsx             # React entry
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
├── docker-compose.yml
└── README.md
```

---

## Troubleshooting

### Lỗi kết nối database
- Kiểm tra `DATABASE_URL` trong `.env`
- Đảm bảo database đang chạy và có thể truy cập
- Kiểm tra firewall và network

### Lỗi migration
```bash
# Xem trạng thái migrations
alembic current

# Xem lịch sử migrations
alembic history

# Rollback migration cuối
alembic downgrade -1

# Chạy lại migrations
alembic upgrade head
```

### Frontend không kết nối được backend
- Kiểm tra backend đang chạy tại port 8000
- Kiểm tra CORS settings trong `backend/app/main.py`
- Kiểm tra API_BASE_URL trong `frontend/src/app/components/lib/api.ts`

### Lỗi token expired
- Hệ thống tự động refresh token
- Nếu vẫn lỗi, đăng xuất và đăng nhập lại
- Kiểm tra refresh token trong localStorage

### Docker containers không start
```bash
# Xem logs
docker-compose logs

# Xem logs của service cụ thể
docker-compose logs backend
docker-compose logs frontend

# Restart containers
docker-compose restart

# Rebuild và restart
docker-compose up -d --build --force-recreate
```

### Lỗi ChromaDB
- Đảm bảo thư mục `chroma_db` tồn tại
- Kiểm tra quyền truy cập thư mục
- Nếu lỗi, có thể xóa và tạo lại thư mục (sẽ mất dữ liệu vector)

### Lỗi ImageKit upload
- Kiểm tra ImageKit credentials trong `.env`
- Kiểm tra quyền truy cập ImageKit account
- Kiểm tra file size (có thể có giới hạn)

### Lỗi SMTP email
- Với Gmail: Đảm bảo đã tạo App Password (không phải mật khẩu thường)
- Kiểm tra SMTP settings trong `.env`
- Kiểm tra firewall có chặn port 587 không

### Port đã được sử dụng
```bash
# Windows: Tìm process sử dụng port
netstat -ano | findstr :8000
netstat -ano | findstr :80

# macOS/Linux: Tìm process sử dụng port
lsof -i :8000
lsof -i :80

# Kill process (thay PID bằng process ID thực tế)
# Windows:
taskkill /PID <PID> /F
# macOS/Linux:
kill -9 <PID>
```

---

## Liên hệ và hỗ trợ

Nếu gặp vấn đề, vui lòng:
1. Kiểm tra phần Troubleshooting ở trên
2. Xem logs để tìm lỗi chi tiết
3. Tạo issue trên repository (nếu có)
4. Gửi ticket hỗ trợ qua ứng dụng

---

## Postman
https://maiduyen05-9072474.postman.co/workspace/Mai-Duyen's-Team's-Workspace~6f47f7bf-6de7-4dcb-8a6a-d7537bb16b82/folder/51146228-69cbadd4-1762-4eac-a8f0-8efd2bee8991?action=share&creator=51146228&ctx=documentation
---

## License

Dự án này được tạo cho mục đích học tập và nghiên cứu.
