from database import fetch_one, execute_query
from datetime import datetime

class UserService:
    
    @staticmethod
    def create_user(name, email, password, phone=None):
        """Tạo user mới"""
        # Kiểm tra email đã tồn tại chưa
        if UserService.get_user_by_email(email):
            return {"success": False, "message": "Email đã được sử dụng"}
        
        # Lưu password plaintext (không hash)
        
        # Insert vào database
        query = """
            INSERT INTO users (name, email, password, phone, created_at) 
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (name, email, password, phone, datetime.now())
        
        if execute_query(query, params):
            return {"success": True, "message": "Đăng ký thành công"}
        else:
            return {"success": False, "message": "Lỗi khi tạo tài khoản"}
    
    @staticmethod
    def authenticate_user(email, password):
        """Xác thực user khi đăng nhập"""
        user = UserService.get_user_by_email(email)
        
        if not user:
            return None
        
        # Kiểm tra password plaintext
        if user['password'] == password:
            return user
        
        return None
    
    @staticmethod
    def get_user_by_email(email):
        """Lấy thông tin user theo email"""
        query = "SELECT * FROM users WHERE email = %s"
        return fetch_one(query, (email,))
    
    @staticmethod
    def get_user_by_id(user_id):
        """Lấy thông tin user theo ID"""
        query = "SELECT * FROM users WHERE id = %s"
        return fetch_one(query, (user_id,))
    
    @staticmethod
    def update_user(user_id, data):
        """Cập nhật thông tin user"""
        fields = []
        params = []
        
        allowed_fields = ['name', 'age', 'year', 'major', 'career_goal', 'status', 
                         'study_level', 'study_goal', 'study_style', 'preferred_language']
        
        for field in allowed_fields:
            if field in data:
                fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not fields:
            return False
        
        params.append(user_id)
        query = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"
        
        return execute_query(query, tuple(params))
    
    @staticmethod
    def update_avatar(user_id, avatar_path):
        """Cập nhật avatar"""
        query = "UPDATE users SET avatar = %s WHERE id = %s"
        return execute_query(query, (avatar_path, user_id))
    
    @staticmethod
    def change_password(user_id, old_password, new_password):
        """Đổi mật khẩu"""
        user = UserService.get_user_by_id(user_id)
        
        if not user:
            return {"success": False, "message": "Không tìm thấy user"}
        
        # Kiểm tra mật khẩu cũ (plaintext)
        if user['password'] != old_password:
            return {"success": False, "message": "Mật khẩu hiện tại không đúng"}
        
        # Lưu mật khẩu mới (plaintext)
        query = "UPDATE users SET password = %s WHERE id = %s"
        
        if execute_query(query, (new_password, user_id)):
            return {"success": True, "message": "Đổi mật khẩu thành công"}
        else:
            return {"success": False, "message": "Lỗi khi đổi mật khẩu"}