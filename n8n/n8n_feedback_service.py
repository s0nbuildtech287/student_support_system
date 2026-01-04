import requests
import logging
from n8n.n8n_health_check import n8n_health

N8N_FEEDBACK_URL = "http://localhost:5678/webhook/feedback"

def add_feedback_via_n8n(user_id, name, avatar, comment, stars=5):
    """
    Thêm feedback qua n8n với fast-fail
    """
    # Fast fail
    if not n8n_health.is_n8n_available():
        logging.info("⚡ N8N is down, skip request")
        return False
    
    try:
        payload = {
            "action": "add",
            "user_id": user_id,
            "name": name,
            "avatar": avatar,
            "comment": comment,
            "stars": stars
        }
        
        res = requests.post(N8N_FEEDBACK_URL, json=payload, timeout=2)
        res.raise_for_status()
        
        data = res.json()
        
        if data.get('success'):
            n8n_health.mark_success()
            logging.info(f"✅ Added feedback via n8n: {name}")
            return True
        else:
            logging.warning(f"⚠️ Failed to add feedback via n8n")
            return False
            
    except requests.exceptions.Timeout:
        logging.warning("⏱️ N8N timeout when adding feedback")
        n8n_health.mark_failure()
        return False
    except requests.exceptions.ConnectionError:
        logging.warning("🔌 N8N connection error when adding feedback")
        n8n_health.mark_failure()
        return False
    except Exception as e:
        logging.error(f"❌ Error adding feedback via n8n: {e}")
        n8n_health.mark_failure()
        return False


def get_feedbacks_via_n8n(limit=100):
    """
    Lấy feedbacks qua n8n với fast-fail
    """
    # Fast fail
    if not n8n_health.is_n8n_available():
        logging.info("⚡ N8N is down, skip request")
        return None
    
    try:
        payload = {
            "action": "get",
            "limit": limit
        }
        
        res = requests.post(N8N_FEEDBACK_URL, json=payload, timeout=2)
        res.raise_for_status()
        
        data = res.json()
        
        if isinstance(data, dict) and data.get('success'):
            feedbacks = data.get('feedbacks', [])
            n8n_health.mark_success()
            logging.info(f"✅ Loaded {len(feedbacks)} feedbacks from n8n")
            return feedbacks
        
        # JSON wrapper
        if isinstance(data, dict) and 'json' in data:
            if data['json'].get('success'):
                feedbacks = data['json'].get('feedbacks', [])
                n8n_health.mark_success()
                logging.info(f"✅ Loaded {len(feedbacks)} feedbacks from nested")
                return feedbacks
        
        logging.warning("⚠️ No feedbacks found in n8n response")
        return None
        
    except requests.exceptions.Timeout:
        logging.warning("⏱️ N8N timeout when loading feedbacks")
        n8n_health.mark_failure()
        return None
    except requests.exceptions.ConnectionError:
        logging.warning("🔌 N8N connection error when loading feedbacks")
        n8n_health.mark_failure()
        return None
    except Exception as e:
        logging.error(f"❌ Error loading feedbacks from n8n: {e}")
        n8n_health.mark_failure()
        return None