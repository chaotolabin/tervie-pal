\# Hệ thống theo dõi sức khỏe cá nhân



Môn học: Cơ sở dữ liệu Web và Hệ thống thông tin


I Giới thiệu


Project cuối kì môn Cơ sở dữ liệu web và hệ thống thông tin:


Website hỗ trợ theo dõi sức khỏe cá nhân và quản lý thói quen sinh hoạt. Hệ thống cho phép người dùng nhập thông tin sức khỏe, theo dõi hoạt động thể chất và chế độ ăn uống, từ đó tính toán các chỉ số dinh dưỡng và đưa ra gợi ý cá nhân hóa.


II Tính năng chính


1\. Quản lý hồ sơ người dùng: Thông tin và các chỉ số sức khỏe

2\. Theo dõi dinh dưỡng: Tính calo và dinh dưỡng từ CSDL thực phẩm

3\. Theo dõi bài tập: Tính calo đốt với các bài tập

4\. Thống kê Dashboard: Biểu đồ chỉ số sức khỏe, theo dõi sức chỉ số cơ thể

5\. Streak System: Theo dõi chuỗi ngày hoạt động

6\. Cộng đồng: Chia sẻ bài viết, like, save, xem xu hướng

7\. Hỗ trợ: Gửi báo lỗi, hỗ trợ tới nhóm phát triển



III Công nghệ sử dụng


\- \*\*Backend:\*\* FastAPI, PostgreSQL, Supabase AI Chatbot (Google Gemini, ChromaDB)

\- \*\*Frontend:\*\* React + Vite

\- \*\*DevOps:\*\* Docker, Docker Compose


IV Hướng dẫn chạy dự án:


1\. Chuẩn bị


\- Cài Docker Desktop và mở chương trình


2\. Cách chạy


Bước 1: Giải nén file zip và mở Terminal tại thư mục dự án


cd tervie-pal


Bước 2: Chạy lệnh Docker 


docker-compose up -d --build


Bước 3: Truy cập


\- Website: http://localhost

\- API Docs: http://localhost:8000/api/docs


Dừng chạy:


docker-compose down







