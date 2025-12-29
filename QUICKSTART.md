# 🚀 Quick Start Guide - Study With AI

## Cài Đặt Nhanh (5 phút)

### 1️⃣ Chuẩn Bị
- Cài Python 3.8+
- Cài MariaDB 10.0+
- Clone/Download dự án

### 2️⃣ Cài Đặt Môi Trường

#### Linux/Mac:
```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt
source venv/bin/activate

# Cài đặt dependencies
pip install -r requirements.txt
```

#### Windows:
```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt
venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt
```

### 3️⃣ Cấu Hình Database

```sql
-- Mở MariaDB command line
CREATE DATABASE studywithai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

File `.env` đã có sẵn với thông tin:
- Host: localhost
- User: root
- Password: Dk@17092004
- Database: studywithai

### 4️⃣ Khởi Tạo Database

```bash
python init_db.py
```

Chọn `y` khi được hỏi seed data

### 5️⃣ Chạy Ứng Dụng

```bash
python run.py
```

Truy cập: http://localhost:5000

---

## 🔐 Tài Khoản Test

Sau khi seed data, bạn có thể sử dụng:
- **Email**: khang@example.com
- **Password**: (bạn phải đăng ký hoặc reset)

Hoặc đơn giản, **Đăng ký tài khoản mới** từ trang Register

---

## 📁 Cấu Trúc Quan Trọng

```
student_support_system/
├── app.py              ⭐ Entry point chính
├── run.py              ⭐ Chạy ứng dụng
├── init_db.py          ⭐ Khởi tạo database
├── models.py           ⭐ Database schema
├── seed.py             ⭐ Sample data
├── config.py           ⭐ Configuration
├── .env                ⭐ Environment variables
├── requirements.txt    ⭐ Dependencies
├── routes/             📂 API endpoints
├── templates/          📂 HTML pages
├── static/             📂 CSS, JS, Images
└── DATABASE_SETUP.md   📚 Documentation
```

---

## ⚙️ Các Lệnh Hữu Ích

```bash
# Khởi tạo lại database (xóa tất cả data)
python init_db.py

# Chạy ứng dụng
python run.py

# Hoặc
python app.py

# Chỉ seed data (giữ nguyên structure)
python seed.py

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Deactivate
deactivate
```

---

## 🔧 Troubleshooting

### ❌ ModuleNotFoundError: No module named 'flask'
```bash
pip install -r requirements.txt
```

### ❌ Can't connect to MariaDB
1. Kiểm tra MariaDB chạy: `mysql -u root -p`
2. Kiểm tra .env có đúng credentials
3. Tạo database: `CREATE DATABASE studywithai;`

### ❌ Port 5000 đã được sử dụng
Sửa trong .env:
```
FLASK_PORT=5001
```

### ❌ Lỗi file upload
Kiểm tra folder `static/images/` tồn tại

---

## 📊 Database Schema

**Users** - Tài khoản người dùng
**Subjects** - Các khóa học
**Lessons** - Các bài học
**Enrollments** - Ghi danh khóa học
**Roadmaps** - Lộ trình học
**RoadmapProgress** - Tiến độ lộ trình
**Feedback** - Phản hồi
**Progress** - Tiến độ bài học

---

## ✅ Checklist Chuẩn Bị

- [ ] Python 3.8+ cài đặt
- [ ] MariaDB cài đặt và chạy
- [ ] Virtual environment tạo
- [ ] Dependencies cài đặt
- [ ] .env được cấu hình
- [ ] Database khởi tạo
- [ ] Ứng dụng chạy thành công
- [ ] Đăng nhập/Đăng ký hoạt động

---

## 🎯 Next Steps

1. Đăng ký tài khoản mới
2. Đăng ký môn học
3. Chọn lộ trình
4. Xem thống kê
5. Gửi feedback

---

## 📞 Support

Xem `DATABASE_SETUP.md` để biết thêm chi tiết

---

**Happy Learning! 🎓**
