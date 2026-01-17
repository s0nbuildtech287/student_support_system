# GGCloud/services/auth_service.py
from database import fetch_one

class AdminAuthService:
    
    @staticmethod
    def is_admin(user_id):
        """Kiểm tra user có phải admin không"""
        try:
            query = """
                SELECT u.email, a.role
                FROM users u
                JOIN admin_users a ON u.id = a.user_id
                WHERE u.id = %s AND u.email = 'admin@gmail.com'
            """
            
            result = fetch_one(query, (user_id,))
            return result is not None
            
        except Exception as e:
            print(f"Error checking admin: {e}")
            return False