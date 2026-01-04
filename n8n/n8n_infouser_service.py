import requests
import logging
from n8n.n8n_health_check import n8n_health

N8N_USER_INFO_URL = "http://localhost:5678/webhook/user-info"

def load_user_from_n8n(user_id):
    """
    Lấy thông tin user từ n8n với fast-fail
    """
    # Fast fail
    if not n8n_health.is_n8n_available():
        logging.info("⚡ N8N is down, skip request")
        return None
    
    try:
        payload = {"user_id": user_id}
        res = requests.post(N8N_USER_INFO_URL, json=payload, timeout=2)
        res.raise_for_status()
        
        data = res.json()
        
        if isinstance(data, dict):
            # Wrapper success
            if data.get('success') and 'user' in data:
                user = data['user']
                n8n_health.mark_success()
                logging.info(f"✅ Found user: {user.get('name')} (ID: {user_id})")
                return user
            
            # JSON wrapper
            if 'json' in data and 'user' in data['json']:
                user = data['json']['user']
                n8n_health.mark_success()
                logging.info(f"✅ Found user from nested: {user.get('name')}")
                return user
            
            # Direct object
            if 'id' in data and 'email' in data:
                n8n_health.mark_success()
                logging.info(f"✅ Found user directly: {data.get('name')}")
                return data
        
        logging.warning(f"⚠️ User {user_id} not found in n8n")
        return None
        
    except requests.exceptions.Timeout:
        logging.warning(f"⏱️ N8N timeout for user {user_id}")
        n8n_health.mark_failure()
        return None
    except requests.exceptions.ConnectionError:
        logging.warning(f"🔌 N8N connection error for user {user_id}")
        n8n_health.mark_failure()
        return None
    except Exception as e:
        logging.error(f"❌ Error loading user from n8n: {e}")
        n8n_health.mark_failure()
        return None