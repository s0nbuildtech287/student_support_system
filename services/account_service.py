from werkzeug.security import check_password_hash, generate_password_hash
from utils.db import get_db_connection

def register_user(fullname, email, password):
    """
    Đăng ký user mới
    Returns: (success: bool, message: str, user_id: int)
    """
    connection = get_db_connection()
    if not connection:
        return False, "Lỗi kết nối database", None
    
    try:
        cursor = connection.cursor()
        
        # Kiểm tra email đã tồn tại chưa
        check_email_query = "SELECT id FROM users WHERE email = %s"
        cursor.execute(check_email_query, (email,))
        if cursor.fetchone():
            return False, "Email đã được sử dụng", None
        
        # Hash password và lưu user mới
        # Use pbkdf2 to avoid hashlib.scrypt dependency on some Windows builds
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        insert_query = """
            INSERT INTO users (fullname, email, password) 
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (fullname, email, hashed_password))
        connection.commit()
        
        user_id = cursor.lastrowid
        return True, "Đăng ký thành công", user_id
        
    except Exception as e:
        connection.rollback()
        return False, f"Lỗi khi đăng ký: {str(e)}", None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def login_user(email, password):
    """
    Đăng nhập user
    Returns: (success: bool, message: str, user: dict)
    """
    connection = get_db_connection()
    if not connection:
        return False, "Lỗi kết nối database", None
    
    try:
        cursor = connection.cursor(dictionary=True)
        
        # Tìm user theo email
        query = "SELECT id, fullname, email, password FROM users WHERE email = %s"
        cursor.execute(query, (email,))
        user = cursor.fetchone()
        
        if not user:
            return False, "Email hoặc mật khẩu không đúng", None
        
        # Kiểm tra password
        if check_password_hash(user["password"], password):
            # Xóa password khỏi user dict trước khi trả về
            user.pop("password")
            return True, "Đăng nhập thành công", user
        else:
            return False, "Email hoặc mật khẩu không đúng", None
            
    except Exception as e:
        return False, f"Lỗi khi đăng nhập: {str(e)}", None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_user_by_id(user_id):
    """
    Lấy thông tin user theo ID
    Returns: user dict hoặc None
    """
    connection = get_db_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        query = "SELECT id, fullname, email, created_at FROM users WHERE id = %s"
        cursor.execute(query, (user_id,))
        user = cursor.fetchone()
        return user
    except Exception as e:
        print(f"Lỗi khi lấy user: {e}")
        return None
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

