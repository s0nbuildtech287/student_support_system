from database import fetch_one, fetch_all, execute_query


def get_subject_learning_progress(user_id, subject_id):
    """
    Lấy thông tin tiến độ học tập của user cho một môn học cụ thể
    QUAN TRỌNG: Trả về thông tin từ LỘ TRÌNH ĐANG XEM (qua URL param)
    hoặc lộ trình đang học đầu tiên tìm thấy
    """
    query = """
        SELECT 
            sp.id as plan_id,
            sp.name as plan_name,
            ps.progress,
            ps.status
        FROM study_plans sp
        JOIN plan_subjects ps ON sp.id = ps.plan_id
        WHERE sp.user_id = %s 
            AND ps.subject_id = %s
            AND sp.is_started = 1
        ORDER BY sp.created_at DESC
        LIMIT 1
    """
    
    return fetch_one(query, (user_id, subject_id))


def get_subject_progress_in_plan(plan_id, subject_id):
    """
    Lấy tiến độ của môn học trong một lộ trình cụ thể
    """
    query = """
        SELECT ps.progress, ps.status
        FROM plan_subjects ps
        WHERE ps.plan_id = %s AND ps.subject_id = %s
    """
    
    return fetch_one(query, (plan_id, subject_id))


def update_subject_progress(user_id, subject_id, progress, status, plan_id=None):
    """
    Cập nhật tiến độ học tập cho một môn học
    Nếu có plan_id thì update cho plan đó, nếu không thì tìm plan đang học
    """
    # Validate
    if progress < 0 or progress > 100:
        return {'success': False, 'message': 'Tiến độ phải từ 0-100%'}
    
    if status not in ['not_started', 'studying', 'completed']:
        return {'success': False, 'message': 'Trạng thái không hợp lệ'}
    
    # Nếu có plan_id cụ thể
    if plan_id:
        query_find = """
            SELECT ps.id, sp.id as plan_id
            FROM study_plans sp
            JOIN plan_subjects ps ON sp.id = ps.plan_id
            WHERE sp.id = %s 
                AND ps.subject_id = %s
                AND sp.user_id = %s
            LIMIT 1
        """
        result = fetch_one(query_find, (plan_id, subject_id, user_id))
    else:
        # Tìm plan đang học của user có chứa subject này
        query_find = """
            SELECT ps.id, sp.id as plan_id
            FROM study_plans sp
            JOIN plan_subjects ps ON sp.id = ps.plan_id
            WHERE sp.user_id = %s 
                AND ps.subject_id = %s
                AND sp.is_started = 1
            LIMIT 1
        """
        result = fetch_one(query_find, (user_id, subject_id))
    
    if not result:
        return {'success': False, 'message': 'Môn học này không có trong lộ trình đang học của bạn'}
    
    # Update progress
    query_update = """
        UPDATE plan_subjects
        SET progress = %s, status = %s
        WHERE id = %s
    """
    
    if execute_query(query_update, (progress, status, result['id'])):
        return {'success': True, 'message': 'Cập nhật tiến độ thành công'}
    
    return {'success': False, 'message': 'Lỗi khi cập nhật tiến độ'}


def mark_subject_completed(user_id, subject_id, plan_id=None):
    """
    Đánh dấu môn học đã hoàn thành (progress = 100, status = completed)
    Nếu có plan_id thì mark cho plan đó
    """
    # Kiểm tra đã pass quiz chưa (quiz theo subject, không theo plan)
    from services.quiz_service import has_passed_quiz_in_plan
    
    if not has_passed_quiz_in_plan(user_id, subject_id, plan_id):
        return {'success': False, 'message': 'Bạn cần đạt 80% bài test trước khi hoàn thành môn học'}
    
    return update_subject_progress(user_id, subject_id, 100, 'completed', plan_id)


def get_plan_overall_progress(plan_id, user_id):
    """
    Tính tiến độ tổng thể của một lộ trình
    """
    # Kiểm tra plan thuộc về user
    query_check = """
        SELECT id FROM study_plans
        WHERE id = %s AND user_id = %s
    """
    
    if not fetch_one(query_check, (plan_id, user_id)):
        return None
    
    # Lấy thống kê
    query = """
        SELECT 
            COUNT(*) as total_subjects,
            SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_subjects,
            SUM(CASE WHEN status = 'studying' THEN 1 ELSE 0 END) as studying_subjects,
            SUM(CASE WHEN status = 'not_started' THEN 1 ELSE 0 END) as not_started_subjects,
            AVG(progress) as overall_progress
        FROM plan_subjects
        WHERE plan_id = %s
    """
    
    result = fetch_one(query, (plan_id,))
    
    if result:
        return {
            'total_subjects': result['total_subjects'] or 0,
            'completed_subjects': result['completed_subjects'] or 0,
            'studying_subjects': result['studying_subjects'] or 0,
            'not_started_subjects': result['not_started_subjects'] or 0,
            'overall_progress': round(result['overall_progress'] or 0, 1)
        }
    
    return None


def get_user_all_progress(user_id):
    """
    Lấy tiến độ tất cả lộ trình của user
    """
    query = """
        SELECT 
            sp.id,
            sp.name,
            sp.is_started,
            COUNT(ps.id) as total_subjects,
            SUM(CASE WHEN ps.status = 'completed' THEN 1 ELSE 0 END) as completed_subjects,
            AVG(ps.progress) as overall_progress
        FROM study_plans sp
        LEFT JOIN plan_subjects ps ON sp.id = ps.plan_id
        WHERE sp.user_id = %s
        GROUP BY sp.id
        ORDER BY sp.created_at DESC
    """
    
    plans = fetch_all(query, (user_id,))
    
    for plan in plans:
        plan['overall_progress'] = round(plan['overall_progress'] or 0, 1)
        plan['completed_subjects'] = plan['completed_subjects'] or 0
        plan['total_subjects'] = plan['total_subjects'] or 0
    
    return plans