# Study With AI - Hệ Thống Gợi Ý Lộ Trình Học Tập

Một ứng dụng web giúp sinh viên lập kế hoạch và theo dõi quá trình học tập của mình với AI.

## 📋 Yêu Cầu Hệ Thống

- Python 3.8+
- MariaDB 10.0+
- pip (package manager)

## 🚀 Cài Đặt

### 1. Clone/Tải Dự Án
```bash
cd /path/to/student_support_system
```

### 2. Tạo Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate  # Windows
```

### 3. Cài Đặt Dependencies
```bash
pip install -r requirements.txt
```

### 4. Cấu Hình Database
- Tạo database MariaDB:
```sql
CREATE DATABASE studywithai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

- File `.env` đã được tạo sẵn với các thông tin:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=Dk@17092004
DB_NAME=studywithai
```

### 5. Khởi Tạo Database
```bash
python
>>> from app import create_app
>>> from seed import seed_database
>>> app = create_app()
>>> with app.app_context():
...     seed_database()
```

### 6. Chạy Ứng Dụng
```bash
python app.py
```

Truy cập: http://localhost:5000

## 📁 Cấu Trúc Thư Mục

```
student_support_system/
├── app.py                 # Entry point
├── config.py             # Configuration
├── models.py             # Database models
├── seed.py               # Database seed data
├── .env                  # Environment variables
├── requirements.txt      # Dependencies
├── routes/               # Flask blueprints
│   ├── user.py          # User routes (login, profile, settings)
│   ├── home.py          # Home page
│   ├── subject.py       # Subject management
│   ├── roadmap.py       # Roadmap management
│   ├── ranking.py       # Rankings
│   └── feedback.py      # Feedback
├── templates/           # HTML templates
│   ├── login.html
│   ├── register.html
│   ├── home.html
│   ├── profile.html
│   ├── settings.html
│   ├── statistics.html
│   ├── subject.html
│   ├── subject_detail.html
│   ├── roadmap.html
│   ├── roadmap_detail.html
│   ├── ranking.html
│   └── feedback.html
├── static/              # Static files
│   ├── css/            # Stylesheets
│   ├── js/             # JavaScript
│   └── images/         # Images (including user avatars)
└── data/               # Data files (CSV)
```

## 🗄️ Database Schema

### Users Table
- id, name, email, password, age, avatar, year, major, gpa, career_goal, status

### Subjects Table
- id, name, description, code, category, level, duration, image_url

### Lessons Table
- id, subject_id, title, description, order, content

### Enrollments Table
- id, user_id, subject_id, progress_percentage, status, start_date, completion_date

### Roadmaps Table
- id, name, description, image_url, estimated_duration

### RoadmapSubjects Table
- id, roadmap_id, subject_id, order

### RoadmapProgress Table
- id, user_id, roadmap_id, progress_percentage, status, start_date, completion_date

### Feedback Table
- id, user_id, subject, message, rating, status

### Progress Table
- id, user_id, lesson_id, is_completed, completion_date

### OutlineItems Table
- id, subject_id, title, description, order

## 🔐 Authentication

- Tài khoản test (sau khi seed):
  - Email: khang@example.com
  - Password: password (cần cập nhật sau khi đăng ký)

## 📝 Các Tính Năng Chính

### User Management
- ✅ Đăng ký/Đăng nhập
- ✅ Chỉnh sửa hồ sơ (tên, email)
- ✅ Đổi avatar
- ✅ Xem thống kê học tập

### Subject Management
- ✅ Danh sách môn học
- ✅ Lọc theo category/level
- ✅ Đăng ký môn học
- ✅ Theo dõi tiến độ

### Roadmap Management
- ✅ Danh sách lộ trình
- ✅ Chi tiết lộ trình
- ✅ Bắt đầu lộ trình
- ✅ Theo dõi tiến độ

### Additional Features
- ✅ Ranking users
- ✅ Feedback system
- ✅ Progress tracking

## 🛠️ API Endpoints

### User Routes
- POST `/login` - Đăng nhập
- GET `/register` - Trang đăng ký
- POST `/register` - Đăng ký
- GET `/profile` - Xem hồ sơ
- POST `/profile/update` - Cập nhật thông tin
- POST `/profile/update-avatar` - Đổi avatar
- GET `/settings` - Cài đặt
- GET `/statistics` - Thống kê
- GET `/logout` - Đăng xuất

### Subject Routes
- GET `/subject` - Danh sách môn học
- GET `/subject/<id>` - Chi tiết môn học
- POST `/subject/<id>/enroll` - Đăng ký môn học

### Roadmap Routes
- GET `/roadmap` - Danh sách lộ trình
- GET `/roadmap/<id>` - Chi tiết lộ trình
- POST `/roadmap/<id>/start` - Bắt đầu lộ trình

### Other Routes
- GET `/home` - Trang chủ
- GET `/ranking` - Bảng xếp hạng
- GET `/feedback` - Trang feedback
- POST `/feedback/submit` - Gửi feedback

## 🔄 Workflows

### User Registration & Login
1. Người dùng đăng ký với email/password
2. Mật khẩu được hash bằng werkzeug.security
3. User object được lưu vào database
4. Session được tạo sau khi đăng nhập

### Enrollment & Progress Tracking
1. User đăng ký môn học → Enrollment record tạo
2. Hệ thống theo dõi progress_percentage
3. Khi hoàn thành → status = "Completed"
4. GPA được cập nhật dựa trên hoàn thành

### Roadmap Tracking
1. User chọn roadmap
2. System tạo RoadmapProgress record
3. Các subject trong roadmap được unlock theo thứ tự
4. Progress tương ứng update khi hoàn thành subjects

## 📊 Database Initialization

```bash
# Python interactive
python
```

```python
from app import create_app
from seed import seed_database

app = create_app()
with app.app_context():
    seed_database()  # Seed initial data
```

## 🐛 Troubleshooting

### MariaDB Connection Error
- Kiểm tra MariaDB service có chạy không
- Kiểm tra database credentials trong .env
- Tạo database nếu chưa tồn tại

### Port Already in Use
```bash
# Thay đổi port trong app.py
app.run(debug=True, port=5001)
```

### Import Errors
```bash
# Cài lại requirements
pip install -r requirements.txt --force-reinstall
```

## 📚 Technology Stack

- **Backend**: Flask, SQLAlchemy
- **Database**: MariaDB
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Authentication**: Flask-Session, werkzeug.security
- **File Upload**: werkzeug.utils

## 👨‍💻 Tác Giả

Study With AI Team

## 📄 License

MIT License

---

**Lần cập nhật cuối**: 29/12/2025
