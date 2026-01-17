# 🌐 Hướng Dẫn Kết Nối Database Qua Playit.gg

## Tại Sao Cần Playit.gg?

Khi bạn deploy ứng dụng lên **Vercel** (hoặc bất kỳ hosting nào), nhưng database MySQL vẫn chạy trên **máy tính cá nhân**, bạn cần một "cầu nối" để Vercel có thể kết nối về máy bạn. **Playit.gg** là công cụ tạo tunnel miễn phí để làm việc này.

## ⚠️ Lỗi Thường Gặp

### ❌ SAI:
```ini
DB_HOST=localhost
DB_PORT=3306
```
**Điều này chỉ hoạt động khi chạy local!** Khi deploy lên Vercel, `localhost` là máy chủ của Vercel, không phải máy bạn.

### ✅ ĐÚNG (với Playit.gg):
```ini
DB_HOST=23.ip.gl.ply.gg    # IP từ Playit
DB_PORT=16714               # PORT từ Playit (không phải 3306!)
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=student_support
```

## 📋 Các Bước Cấu Hình

### Bước 1: Cài Đặt Playit.gg
1. Tải về từ: https://playit.gg/download
2. Cài đặt và chạy ứng dụng
3. Đăng nhập hoặc tạo tài khoản miễn phí

### Bước 2: Tạo Tunnel cho MySQL
1. Trong Playit, nhấn **"Add Tunnel"**
2. Chọn **TCP Tunnel** (không phải HTTP!)
3. Điền thông tin:
   - **Local Port**: `3306` (port MySQL trên máy bạn)
   - **Tunnel Name**: `mysql-tunnel` (tùy chọn)
4. Playit sẽ cấp cho bạn:
   - **Public IP**: Ví dụ `23.ip.gl.ply.gg`
   - **Public Port**: Ví dụ `16714`

### Bước 3: Cấu Hình File `.env`

#### Trên Máy Local (Development):
```ini
# Khi code/test trên máy
DB_HOST=localhost
DB_PORT=3306
```

#### Trên Vercel (Production):
```ini
# Khi deploy lên Vercel - dùng thông tin từ Playit
DB_HOST=23.ip.gl.ply.gg     # ← Thay bằng IP Playit cấp cho bạn
DB_PORT=16714                # ← Thay bằng PORT Playit cấp cho bạn
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=student_support
```

### Bước 4: Cấu Hình MySQL để Chấp Nhận Kết Nối Từ Xa

Mặc định MySQL chỉ chấp nhận kết nối từ `localhost`. Bạn cần cho phép kết nối từ bên ngoài:

```sql
-- 1. Tạo user cho remote access (nếu chưa có)
CREATE USER 'root'@'%' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON student_support.* TO 'root'@'%';
FLUSH PRIVILEGES;

-- 2. Kiểm tra bind-address trong file my.ini/my.cnf
-- Tìm file my.ini (Windows) hoặc my.cnf (Linux/Mac)
-- Tìm dòng: bind-address = 127.0.0.1
-- Đổi thành: bind-address = 0.0.0.0
-- Sau đó restart MySQL service
```

### Bước 5: Test Kết Nối

Trên máy local, bạn có thể test xem Playit tunnel có hoạt động không:

```bash
# Test từ máy khác (hoặc dùng online MySQL client)
mysql -h 23.ip.gl.ply.gy -P 16714 -u root -p
```

Nếu kết nối thành công → OK! Deploy lên Vercel sẽ hoạt động.

## 🔒 Bảo Mật

### ⚠️ Cảnh Báo
Khi expose database ra internet qua Playit:
1. **Đặt mật khẩu mạnh** cho user MySQL
2. **Chỉ GRANT quyền cần thiết**, không nên `GRANT ALL PRIVILEGES` cho môi trường production
3. **Theo dõi logs** để phát hiện truy cập bất thường
4. **Cân nhắc dùng MySQL Cloud** (PlanetScale, AWS RDS) cho production thực sự

### 💡 Giải Pháp Tốt Hơn Cho Production
- **PlanetScale** (MySQL miễn phí, serverless)
- **Railway** (Deploy cả backend + database)
- **Supabase** (PostgreSQL miễn phí)
- **AWS RDS Free Tier** (MySQL/PostgreSQL)

## 📝 Checklist Triển Khai

- [ ] Playit.gg đã chạy và tạo tunnel cho port 3306
- [ ] Ghi lại **IP** và **PORT** từ Playit
- [ ] Sửa `.env` trên Vercel với đúng IP và PORT của Playit
- [ ] MySQL đã cho phép remote connection (`bind-address = 0.0.0.0`)
- [ ] User MySQL đã có quyền truy cập từ `%` (any host)
- [ ] Đã test kết nối từ bên ngoài thành công
- [ ] **GIỮ PLAYIT CHẠY** mọi lúc để Vercel kết nối được

## ❓ FAQ

**Q: Tại sao không dùng localhost trên Vercel?**  
A: Vì `localhost` trên Vercel là máy chủ của Vercel, không phải máy bạn.

**Q: Tại sao không dùng port 3306?**  
A: Port 3306 là port **nội bộ** trên máy bạn. Playit tạo một port **công khai** khác (VD: 16714) để forward vào port 3306.

**Q: Playit có miễn phí không?**  
A: Có! Playit.gg có gói miễn phí với băng thông đủ dùng cho dự án nhỏ/vừa.

**Q: Nếu tắt máy hoặc tắt Playit thì sao?**  
A: Website trên Vercel sẽ không kết nối được database và báo lỗi. Bạn phải **giữ máy và Playit chạy** hoặc chuyển sang dùng cloud database.

**Q: Có cách nào tự động chạy Playit không?**  
A: Có, bạn có thể cài Playit như một service/daemon để tự khởi động cùng máy tính.

---

**🎯 Kết Luận**: Với Playit.gg, bạn có thể deploy app lên Vercel miễn phí mà vẫn dùng MySQL trên máy cá nhân. Nhưng nhớ **PHẢI ĐIỀN ĐÚNG IP VÀ PORT TỪ PLAYIT**, không phải `localhost:3306`!
