import requests
import logging

# ==============================
# CONFIG
# ==============================
N8N_BASE_URL = "http://localhost:5678/webhook"
TIMEOUT = 5  # seconds


# ==============================
# GET QUIZ QUESTIONS
# ==============================
def get_quiz_from_n8n(subject_uid, plan_id=None):
    """
    Lấy danh sách câu hỏi quiz từ n8n
    """
    try:
        params = {
            "uid": subject_uid
        }

        # plan_id chỉ để log / validate (trá hình)
        if plan_id:
            params["plan_id"] = plan_id

        res = requests.get(
            f"{N8N_BASE_URL}/quiz-get",
            params=params,
            timeout=TIMEOUT
        )

        if res.status_code != 200:
            logging.error("❌ n8n quiz-get failed: %s", res.text)
            return None

        data = res.json()

        if not data.get("success"):
            return None

        return data.get("questions", [])

    except Exception as e:
        logging.error("❌ n8n quiz-get error: %s", e)
        return None


# ==============================
# SUBMIT QUIZ
# ==============================
def submit_quiz_to_n8n(user_id, subject_uid, answers, plan_id):
    """
    Gửi bài làm quiz sang n8n để chấm điểm
    """
    try:
        payload = {
            "user_id": user_id,
            "subject_uid": subject_uid,
            "plan_id": plan_id,
            "answers": answers
        }

        res = requests.post(
            f"{N8N_BASE_URL}/quiz-submit",
            json=payload,
            timeout=TIMEOUT
        )

        if res.status_code != 200:
            logging.error("❌ n8n quiz-submit failed: %s", res.text)
            return {
                "success": False,
                "message": "Không thể chấm bài quiz"
            }

        data = res.json()

        return data

    except Exception as e:
        logging.error("❌ n8n quiz-submit error: %s", e)
        return {
            "success": False,
            "message": "Lỗi kết nối n8n"
        }
