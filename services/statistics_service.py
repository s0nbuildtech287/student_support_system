"""
Statistics Service - Lấy dữ liệu thống kê học tập từ database
Hỗ trợ 2 mode: Direct (query trực tiếp) và Superset (qua Superset API)
"""

from database import fetch_one, fetch_all
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Flag để chọn mode: 'direct' hoặc 'superset'
STATISTICS_MODE = 'superset'  # Thay đổi thành 'superset' để dùng Superset API


class StatisticsService:
    """Service để lấy các thống kê học tập của user"""
    
    @staticmethod
    def get_user_overview(user_id):
        """
        Lấy tổng quan thống kê của user:
        - Số khóa học đang học
        - Số bài học hoàn thành
        - Tổng thời gian học
        - Điểm trung bình quiz
        """
        stats = {
            'total_courses': 0,
            'completed_lessons': 0,
            'total_study_hours': 0,
            'average_score': 0
        }
        
        # Số khóa học đang học (số môn trong các plan đang started)
        query_courses = """
            SELECT COUNT(DISTINCT ps.subject_id) as total
            FROM study_plans sp
            JOIN plan_subjects ps ON sp.id = ps.plan_id
            WHERE sp.user_id = %s AND sp.is_started = 1
        """
        result = fetch_one(query_courses, (user_id,))
        if result:
            stats['total_courses'] = result['total'] or 0
        
        # Số bài học hoàn thành (môn có status = completed)
        query_completed = """
            SELECT COUNT(*) as total
            FROM study_plans sp
            JOIN plan_subjects ps ON sp.id = ps.plan_id
            WHERE sp.user_id = %s AND ps.status = 'completed'
        """
        result = fetch_one(query_completed, (user_id,))
        if result:
            stats['completed_lessons'] = result['total'] or 0
        
        # Tổng thời gian học (sum of study_hours từ completed subjects)
        query_hours = """
            SELECT COALESCE(SUM(s.study_hours), 0) as total_hours
            FROM study_plans sp
            JOIN plan_subjects ps ON sp.id = ps.plan_id
            JOIN subjects s ON ps.subject_id = s.id
            WHERE sp.user_id = %s 
                AND (ps.status = 'completed' OR ps.status = 'studying')
        """
        result = fetch_one(query_hours, (user_id,))
        if result:
            stats['total_study_hours'] = result['total_hours'] or 0
        
        # Điểm trung bình quiz
        query_avg = """
            SELECT AVG(percentage) as avg_score
            FROM quiz_attempts
            WHERE user_id = %s
        """
        result = fetch_one(query_avg, (user_id,))
        if result and result['avg_score']:
            # Chuyển sang thang điểm 4.0
            stats['average_score'] = round(float(result['avg_score']) / 25, 1)  # 100% = 4.0
        
        return stats
    
    @staticmethod
    def get_weekly_progress(user_id):
        """
        Lấy tiến độ học tập theo ngày trong tuần (7 ngày gần nhất)
        Dựa trên số activities/quiz attempts mỗi ngày
        """
        # Lấy 7 ngày gần nhất
        weekly_data = []
        labels = ['T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'CN']
        
        # Query số hoạt động mỗi ngày trong 7 ngày qua
        query = """
            SELECT 
                DAYOFWEEK(created_at) as day_of_week,
                COUNT(*) as activity_count
            FROM user_activities
            WHERE user_id = %s 
                AND created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
            GROUP BY DAYOFWEEK(created_at)
            ORDER BY day_of_week
        """
        results = fetch_all(query, (user_id,))
        
        # Tạo dict từ kết quả
        day_counts = {r['day_of_week']: r['activity_count'] for r in results}
        
        # DAYOFWEEK: 1=Sunday, 2=Monday, ..., 7=Saturday
        # Map to T2-CN
        day_mapping = {2: 0, 3: 1, 4: 2, 5: 3, 6: 4, 7: 5, 1: 6}  # T2-CN
        
        for i in range(7):
            # Tìm DAYOFWEEK tương ứng
            dow = [k for k, v in day_mapping.items() if v == i][0]
            weekly_data.append(day_counts.get(dow, 0))
        
        return {
            'labels': labels,
            'data': weekly_data
        }
    
    @staticmethod
    def get_favorite_subjects(user_id):
        """
        Lấy top môn học yêu thích (dựa trên số lần xem và quiz attempts)
        """
        query = """
            SELECT 
                s.subject_name,
                COUNT(ua.id) as view_count
            FROM user_activities ua
            JOIN subjects s ON ua.target_id = s.id
            WHERE ua.user_id = %s 
                AND ua.activity_type = 'view_subject'
            GROUP BY s.id, s.subject_name
            ORDER BY view_count DESC
            LIMIT 5
        """
        results = fetch_all(query, (user_id,))
        
        if not results:
            # Fallback: lấy từ plan_subjects
            query_fallback = """
                SELECT 
                    s.subject_name,
                    ps.progress as view_count
                FROM study_plans sp
                JOIN plan_subjects ps ON sp.id = ps.plan_id
                JOIN subjects s ON ps.subject_id = s.id
                WHERE sp.user_id = %s
                ORDER BY ps.progress DESC
                LIMIT 5
            """
            results = fetch_all(query_fallback, (user_id,))
        
        labels = [r['subject_name'] for r in results] if results else ['Chưa có dữ liệu']
        data = [r['view_count'] for r in results] if results else [0]
        
        return {
            'labels': labels,
            'data': data
        }
    
    @staticmethod
    def get_monthly_trend(user_id):
        """
        Lấy xu hướng học tập hàng tháng (4 tuần gần nhất)
        """
        labels = ['Tuần 1', 'Tuần 2', 'Tuần 3', 'Tuần 4']
        data = []
        
        for i in range(4):
            start_week = 28 - (i * 7)
            end_week = start_week - 7
            
            query = """
                SELECT COUNT(*) as count
                FROM user_activities
                WHERE user_id = %s 
                    AND created_at BETWEEN 
                        DATE_SUB(CURDATE(), INTERVAL %s DAY)
                        AND DATE_SUB(CURDATE(), INTERVAL %s DAY)
            """
            result = fetch_one(query, (user_id, start_week, end_week))
            data.insert(0, result['count'] if result else 0)
        
        return {
            'labels': labels,
            'data': data
        }
    
    @staticmethod
    def get_quiz_statistics(user_id):
        """
        Lấy thống kê về quiz
        """
        query = """
            SELECT 
                COUNT(*) as total_attempts,
                SUM(CASE WHEN passed = TRUE THEN 1 ELSE 0 END) as passed_count,
                AVG(percentage) as avg_percentage,
                MAX(percentage) as best_score,
                MIN(percentage) as worst_score
            FROM quiz_attempts
            WHERE user_id = %s
        """
        result = fetch_one(query, (user_id,))
        
        if result:
            return {
                'total_attempts': result['total_attempts'] or 0,
                'passed_count': result['passed_count'] or 0,
                'avg_percentage': round(float(result['avg_percentage'] or 0), 1),
                'best_score': float(result['best_score'] or 0),
                'worst_score': float(result['worst_score'] or 0)
            }
        
        return {
            'total_attempts': 0,
            'passed_count': 0,
            'avg_percentage': 0,
            'best_score': 0,
            'worst_score': 0
        }
    
    @staticmethod
    def get_study_plans_progress(user_id):
        """
        Lấy tiến độ các lộ trình học tập
        """
        query = """
            SELECT 
                sp.id,
                sp.name as plan_name,
                COUNT(ps.id) as total_subjects,
                SUM(CASE WHEN ps.status = 'completed' THEN 1 ELSE 0 END) as completed_subjects,
                AVG(ps.progress) as avg_progress,
                sp.is_started,
                sp.created_at
            FROM study_plans sp
            LEFT JOIN plan_subjects ps ON sp.id = ps.plan_id
            WHERE sp.user_id = %s
            GROUP BY sp.id, sp.name, sp.is_started, sp.created_at
            ORDER BY sp.is_started DESC, sp.created_at DESC
        """
        results = fetch_all(query, (user_id,))
        
        plans = []
        for r in results:
            plans.append({
                'id': r['id'],
                'name': r['plan_name'],
                'total_subjects': r['total_subjects'] or 0,
                'completed_subjects': r['completed_subjects'] or 0,
                'progress': round(float(r['avg_progress'] or 0), 1),
                'is_started': r['is_started'],
                'created_at': r['created_at']
            })
        
        return plans
    
    @staticmethod
    def get_recent_activities(user_id, limit=10):
        """
        Lấy các hoạt động gần đây của user
        """
        query = """
            SELECT 
                activity_type,
                target_name,
                created_at
            FROM user_activities
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """
        results = fetch_all(query, (user_id, limit))
        
        activities = []
        for r in results:
            activities.append({
                'type': r['activity_type'],
                'target': r['target_name'],
                'time': r['created_at']
            })
        
        return activities
    
    @staticmethod
    def get_achievements(user_id):
        """
        Lấy thành tích của user dựa trên dữ liệu thực
        """
        achievements = []
        
        # Kiểm tra số môn hoàn thành
        query_completed = """
            SELECT COUNT(*) as count
            FROM study_plans sp
            JOIN plan_subjects ps ON sp.id = ps.plan_id
            WHERE sp.user_id = %s AND ps.status = 'completed'
        """
        result = fetch_one(query_completed, (user_id,))
        completed_count = result['count'] if result else 0
        
        if completed_count >= 5:
            achievements.append({
                'icon': '🏆',
                'title': 'Người học chăm chỉ',
                'description': f'Đã hoàn thành {completed_count} khóa học',
                'unlocked': True
            })
        else:
            achievements.append({
                'icon': '📚',
                'title': 'Người học chăm chỉ',
                'description': f'Hoàn thành 5 khóa học ({completed_count}/5)',
                'unlocked': False
            })
        
        # Kiểm tra quiz pass
        query_quiz = """
            SELECT COUNT(DISTINCT subject_id) as count
            FROM quiz_attempts
            WHERE user_id = %s AND passed = TRUE
        """
        result = fetch_one(query_quiz, (user_id,))
        quiz_passed = result['count'] if result else 0
        
        if quiz_passed >= 3:
            achievements.append({
                'icon': '🎯',
                'title': 'Bậc thầy Quiz',
                'description': f'Vượt qua quiz của {quiz_passed} môn học',
                'unlocked': True
            })
        else:
            achievements.append({
                'icon': '🎯',
                'title': 'Bậc thầy Quiz',
                'description': f'Vượt qua quiz của 3 môn ({quiz_passed}/3)',
                'unlocked': False
            })
        
        # Kiểm tra số lộ trình
        query_plans = """
            SELECT COUNT(*) as count
            FROM study_plans
            WHERE user_id = %s AND is_started = 1
        """
        result = fetch_one(query_plans, (user_id,))
        plan_count = result['count'] if result else 0
        
        if plan_count >= 1:
            achievements.append({
                'icon': '🚀',
                'title': 'Người khởi đầu',
                'description': 'Đã bắt đầu lộ trình học tập đầu tiên',
                'unlocked': True
            })
        else:
            achievements.append({
                'icon': '🚀',
                'title': 'Người khởi đầu',
                'description': 'Bắt đầu lộ trình học tập đầu tiên',
                'unlocked': False
            })
        
        # Điểm cao nhất
        query_score = """
            SELECT MAX(percentage) as max_score
            FROM quiz_attempts
            WHERE user_id = %s
        """
        result = fetch_one(query_score, (user_id,))
        max_score = float(result['max_score']) if result and result['max_score'] else 0
        
        if max_score >= 90:
            achievements.append({
                'icon': '⭐',
                'title': 'Xuất sắc',
                'description': f'Đạt điểm {max_score}% trong quiz',
                'unlocked': True
            })
        else:
            achievements.append({
                'icon': '⭐',
                'title': 'Xuất sắc',
                'description': f'Đạt điểm 90%+ trong quiz ({max_score}%)',
                'unlocked': False
            })
        
        # Số hoạt động
        query_activities = """
            SELECT COUNT(*) as count
            FROM user_activities
            WHERE user_id = %s
        """
        result = fetch_one(query_activities, (user_id,))
        activity_count = result['count'] if result else 0
        
        if activity_count >= 50:
            achievements.append({
                'icon': '🔥',
                'title': 'Hoạt động tích cực',
                'description': f'{activity_count} hoạt động trên hệ thống',
                'unlocked': True
            })
        else:
            achievements.append({
                'icon': '🔥',
                'title': 'Hoạt động tích cực',
                'description': f'50 hoạt động trên hệ thống ({activity_count}/50)',
                'unlocked': False
            })
        
        # Số môn đang học
        if completed_count >= 1:
            achievements.append({
                'icon': '✅',
                'title': 'Hoàn thành đầu tiên',
                'description': 'Hoàn thành môn học đầu tiên',
                'unlocked': True
            })
        else:
            achievements.append({
                'icon': '✅',
                'title': 'Hoàn thành đầu tiên',
                'description': 'Hoàn thành môn học đầu tiên',
                'unlocked': False
            })
        
        return achievements
    
    @staticmethod
    def get_all_statistics(user_id):
        """
        Lấy tất cả thống kê cho một user
        """
        return {
            'overview': StatisticsService.get_user_overview(user_id),
            'weekly_progress': StatisticsService.get_weekly_progress(user_id),
            'favorite_subjects': StatisticsService.get_favorite_subjects(user_id),
            'monthly_trend': StatisticsService.get_monthly_trend(user_id),
            'quiz_stats': StatisticsService.get_quiz_statistics(user_id),
            'study_plans': StatisticsService.get_study_plans_progress(user_id),
            'recent_activities': StatisticsService.get_recent_activities(user_id),
            'achievements': StatisticsService.get_achievements(user_id)
        }
