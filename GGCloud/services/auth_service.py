# GGCloud/services/auth_service.py
from database import get_db_connection

class AdminAuthService:
    
    @staticmethod
    def is_admin(user_id):
        """Kiểm tra user có phải admin không"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT u.email, a.role
                FROM users u
                JOIN admin_users a ON u.id = a.user_id
                WHERE u.id = %s AND u.email = 'admin@gmail.com'
            """
            
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return result is not None
            
        except Exception as e:
            print(f"Error checking admin: {e}")
            return False