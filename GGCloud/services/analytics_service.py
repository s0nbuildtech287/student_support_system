# GGCloud/services/analytics_service.py
from flask import request, session
from datetime import datetime, timedelta
from database import get_db_connection



class AnalyticsService:
    
    @staticmethod
    def track_activity(user_id, activity_type, target_id=None, target_name=None):
        """Ghi lại hoạt động của người dùng"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            session_id = session.get('session_id', 'anonymous')
            ip_address = request.remote_addr
            user_agent = request.headers.get('User-Agent', '')
            page_url = request.url
            
            query = """
                INSERT INTO user_activities 
                (user_id, session_id, activity_type, target_id, target_name, 
                 page_url, ip_address, user_agent)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            cursor.execute(query, (
                user_id, session_id, activity_type, target_id, 
                target_name, page_url, ip_address, user_agent
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"Error tracking activity: {e}")
    
    @staticmethod
    def get_most_viewed_subjects(days=30, limit=10):
        """Lấy danh sách môn học được xem nhiều nhất"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    target_id as subject_id,
                    target_name as subject_name,
                    COUNT(*) as view_count
                FROM user_activities
                WHERE activity_type = 'view_subject'
                    AND created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    AND target_id IS NOT NULL
                GROUP BY target_id, target_name
                ORDER BY view_count DESC
                LIMIT %s
            """
            
            cursor.execute(query, (days, limit))
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return results
            
        except Exception as e:
            print(f"Error getting most viewed subjects: {e}")
            return []
    
    @staticmethod
    def get_most_viewed_roadmaps(days=30, limit=10):
        """Lấy danh sách lộ trình được xem nhiều nhất"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    target_name as roadmap_name,
                    COUNT(*) as view_count
                FROM user_activities
                WHERE activity_type = 'view_roadmap'
                    AND created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY target_name
                ORDER BY view_count DESC
                LIMIT %s
            """
            
            cursor.execute(query, (days, limit))
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return results
            
        except Exception as e:
            print(f"Error getting most viewed roadmaps: {e}")
            return []
    
    @staticmethod
    def get_daily_active_users(days=30):
        """Lấy số lượng người dùng hoạt động theo ngày"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    DATE(created_at) as date,
                    COUNT(DISTINCT user_id) as active_users
                FROM user_activities
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                    AND user_id IS NOT NULL
                GROUP BY DATE(created_at)
                ORDER BY date ASC
            """
            
            cursor.execute(query, (days,))
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return results
            
        except Exception as e:
            print(f"Error getting daily active users: {e}")
            return []
    
    @staticmethod
    def get_user_journey(user_id, days=7):
        """Lấy hành trình học tập của người dùng"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            query = """
                SELECT 
                    activity_type,
                    target_name,
                    page_url,
                    created_at
                FROM user_activities
                WHERE user_id = %s
                    AND created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                ORDER BY created_at DESC
                LIMIT 100
            """
            
            cursor.execute(query, (user_id, days))
            results = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return results
            
        except Exception as e:
            print(f"Error getting user journey: {e}")
            return []
    
    @staticmethod
    def get_overview_stats():
        """Lấy tổng quan thống kê"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            
            # Tổng số người dùng
            cursor.execute("SELECT COUNT(*) as total FROM users")
            total_users = cursor.fetchone()['total']
            
            # Người dùng hoạt động trong 7 ngày
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) as active 
                FROM user_activities 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                    AND user_id IS NOT NULL
            """)
            active_users = cursor.fetchone()['active']
            
            # Tổng số hoạt động trong 7 ngày
            cursor.execute("""
                SELECT COUNT(*) as total 
                FROM user_activities 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
            """)
            total_activities = cursor.fetchone()['total']
            
            # Môn học phổ biến nhất
            cursor.execute("""
                SELECT target_name as name, COUNT(*) as count
                FROM user_activities
                WHERE activity_type = 'view_subject'
                    AND created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                GROUP BY target_name
                ORDER BY count DESC
                LIMIT 1
            """)
            top_subject = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return {
                'total_users': total_users,
                'active_users': active_users,
                'total_activities': total_activities,
                'top_subject': top_subject['name'] if top_subject else 'N/A'
            }
            
        except Exception as e:
            print(f"Error getting overview stats: {e}")
            return {
                'total_users': 0,
                'active_users': 0,
                'total_activities': 0,
                'top_subject': 'N/A'
            }