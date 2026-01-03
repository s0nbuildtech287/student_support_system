import requests
import logging
from n8n.n8n_health_check import n8n_health

N8N_URL = "http://localhost:5678/webhook/subject-list"

def load_subjects_from_n8n(page=1, per_page=9, category="", level=""):
    """
    Load subjects từ n8n với fast-fail nếu n8n down
    """
    # Fast fail: Nếu n8n đã biết là down, return None ngay
    if not n8n_health.is_n8n_available():
        logging.info("⚡ N8N is down, skip request")
        return None
    
    try:
        payload = {
            "page": page,
            "per_page": per_page,
            "category": category,
            "level": level
        }

        res = requests.post(N8N_URL, json=payload, timeout=2)  # Giảm timeout xuống 2s
        res.raise_for_status()

        data = res.json()

        # Fix format
        if isinstance(data, list):
            data = data[0] if data else {}

        # Mark success
        n8n_health.mark_success()
        logging.info(f"✅ Loaded subjects from n8n (page {page})")
        
        return data
        
    except requests.exceptions.Timeout:
        logging.warning("⏱️ N8N timeout - switching to fallback")
        n8n_health.mark_failure()
        return None
    except requests.exceptions.ConnectionError:
        logging.warning("🔌 N8N connection error - switching to fallback")
        n8n_health.mark_failure()
        return None
    except Exception as e:
        logging.error(f"❌ N8N error: {e}")
        n8n_health.mark_failure()
        return None