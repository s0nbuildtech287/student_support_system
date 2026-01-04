import requests
import logging

N8N_BASE_URL = "http://localhost:5678/webhook"
TIMEOUT = 5


def load_user_plans_from_n8n(user_id):
    """
    Lấy danh sách lộ trình của user từ n8n
    """
    try:
        res = requests.get(
            f"{N8N_BASE_URL}/yourplan-get",
            params={"user_id": user_id},
            timeout=TIMEOUT
        )

        if res.status_code != 200:
            logging.error("❌ n8n yourplan-get failed: %s", res.text)
            return None

        data = res.json()

        if not data.get("success"):
            return None

        return data.get("plans", [])

    except Exception as e:
        logging.error("❌ n8n yourplan-get error: %s", e)
        return None
