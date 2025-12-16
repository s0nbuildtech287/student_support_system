"""
Script để tạo dữ liệu mẫu cho bảng users
Chạy script này sau khi đã tạo database và bảng users
"""
from werkzeug.security import generate_password_hash
from utils.db import get_db_connection

def seed_users():
    """Thêm các tài khoản mẫu vào database"""
    
    # Danh sách users mẫu: (fullname, email, password_plain)
    sample_users = [
        ("Nguyễn Văn Admin", "admin@example.com", "admin123"),
        ("Trần Thị User", "user1@example.com", "user123"),
        ("Lê Văn Test", "test@example.com", "test123"),
        ("Phạm Thị Demo", "demo@example.com", "demo123"),
        ("Hoàng Văn Sample", "sample@example.com", "sample123"),
    ]
    
    connection = get_db_connection()
    if not connection:
        print("Lỗi: Không thể kết nối database!")
        return
    
    try:
        cursor = connection.cursor()
        
        # Kiểm tra và insert từng user
        inserted_count = 0
        skipped_count = 0
        
        for fullname, email, password_plain in sample_users:
            # Kiểm tra email đã tồn tại chưa
            check_query = "SELECT id FROM users WHERE email = %s"
            cursor.execute(check_query, (email,))
            
            if cursor.fetchone():
                print(f"⚠️  Email {email} đã tồn tại, bỏ qua...")
                skipped_count += 1
                continue
            
            # Hash password và insert
            # Force pbkdf2 to tránh phụ thuộc hashlib.scrypt trên một số bản Python/Windows
            hashed_password = generate_password_hash(password_plain, method="pbkdf2:sha256")
            insert_query = """
                INSERT INTO users (fullname, email, password) 
                VALUES (%s, %s, %s)
            """
            cursor.execute(insert_query, (fullname, email, hashed_password))
            inserted_count += 1
            print(f"✅ Đã thêm: {fullname} ({email}) - Password: {password_plain}")
        
        connection.commit()
        print(f"\n📊 Kết quả: Đã thêm {inserted_count} user, Bỏ qua {skipped_count} user")
        print("\n📝 Danh sách tài khoản để đăng nhập:")
        print("-" * 60)
        for fullname, email, password_plain in sample_users:
            print(f"Email: {email:<25} | Password: {password_plain}")
        print("-" * 60)
        
    except Exception as e:
        connection.rollback()
        print(f"❌ Lỗi khi seed data: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    print("🚀 Bắt đầu seed dữ liệu users...")
    seed_users()
    print("✅ Hoàn thành!")

