"""
Service xử lý quiz và bài kiểm tra
"""

import random
from database import fetch_all, fetch_one, execute_query


def get_random_quiz_questions(subject_id, limit=10):
    """
    Lấy ngẫu nhiên N câu hỏi cho một môn học
    """
    query = """
        SELECT id, question, option_a, option_b, option_c, option_d, correct_answer
        FROM quizzes
        WHERE subject_id = %s
        ORDER BY RAND()
        LIMIT %s
    """
    
    questions = fetch_all(query, (subject_id, limit))
    
    # Shuffle options cho mỗi câu hỏi
    for q in questions:
        options = [
            {'label': 'A', 'text': q['option_a']},
            {'label': 'B', 'text': q['option_b']},
            {'label': 'C', 'text': q['option_c']},
            {'label': 'D', 'text': q['option_d']}
        ]
        q['options'] = options
    
    return questions


def submit_quiz(user_id, subject_id, answers):
    """
    Chấm bài quiz
    
    answers: dict {question_id: selected_answer}
    Ví dụ: {1: 'a', 2: 'b', 3: 'c', ...}
    
    Returns: {
        'success': True,
        'score': 8,
        'total': 10,
        'percentage': 80.0,
        'passed': True,
        'correct_answers': {...}
    }
    """
    if not answers:
        return {'success': False, 'message': 'Chưa có câu trả lời'}
    
    # Lấy đáp án đúng
    question_ids = list(answers.keys())
    placeholders = ','.join(['%s'] * len(question_ids))
    
    query = f"""
        SELECT id, correct_answer
        FROM quizzes
        WHERE id IN ({placeholders})
    """
    
    correct_answers_db = fetch_all(query, tuple(question_ids))
    
    # Tạo dict đáp án đúng
    correct_answers = {row['id']: row['correct_answer'] for row in correct_answers_db}
    
    # Chấm điểm
    score = 0
    total = len(answers)
    
    for question_id, user_answer in answers.items():
        if str(user_answer).lower() == str(correct_answers.get(question_id, '')).lower():
            score += 1
    
    percentage = (score / total * 100) if total > 0 else 0
    passed = percentage >= 80
    
    # Lưu lịch sử làm bài
    save_query = """
        INSERT INTO quiz_attempts 
        (user_id, subject_id, score, total_questions, percentage, passed, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
    """
    
    execute_query(save_query, (user_id, subject_id, score, total, percentage, 1 if passed else 0))
    
    return {
        'success': True,
        'score': score,
        'total': total,
        'percentage': round(percentage, 1),
        'passed': passed,
        'correct_answers': correct_answers
    }


def get_user_quiz_history(user_id, subject_id):
    """
    Lấy lịch sử làm bài của user cho một môn
    """
    query = """
        SELECT score, total_questions, percentage, passed, created_at
        FROM quiz_attempts
        WHERE user_id = %s AND subject_id = %s
        ORDER BY created_at DESC
    """
    
    return fetch_all(query, (user_id, subject_id))


def has_passed_quiz(user_id, subject_id):
    """
    Kiểm tra user đã pass quiz của môn này chưa (>= 80%)
    """
    query = """
        SELECT id
        FROM quiz_attempts
        WHERE user_id = %s AND subject_id = %s AND passed = 1
        LIMIT 1
    """
    
    result = fetch_one(query, (user_id, subject_id))
    return result is not None


def get_best_attempt(user_id, subject_id):
    """
    Lấy lần làm bài tốt nhất
    """
    query = """
        SELECT score, total_questions, percentage, passed, created_at
        FROM quiz_attempts
        WHERE user_id = %s AND subject_id = %s
        ORDER BY percentage DESC, created_at DESC
        LIMIT 1
    """
    
    return fetch_one(query, (user_id, subject_id))