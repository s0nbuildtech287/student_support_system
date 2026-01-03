import requests
import logging
from n8n.n8n_health_check import n8n_health

N8N_ROADMAP_URL = "http://localhost:5678/webhook/roadmap-list"

def load_roadmaps_from_n8n():
    """
    Load roadmaps từ n8n với fast-fail
    """
    # Fast fail
    if not n8n_health.is_n8n_available():
        logging.info("⚡ N8N is down, skip request")
        raise Exception("N8N is not available")
    
    try:
        res = requests.post(N8N_ROADMAP_URL, timeout=2)  # 2s timeout
        res.raise_for_status()
        
        data = res.json()
        
        # Xử lý format
        if isinstance(data, list):
            if data and isinstance(data[0], dict) and 'json' in data[0]:
                roadmaps = [item['json'] for item in data]
                n8n_health.mark_success()
                logging.info(f"✅ Loaded {len(roadmaps)} roadmaps from n8n")
                return roadmaps
            else:
                n8n_health.mark_success()
                logging.info(f"✅ Loaded {len(data)} roadmaps from n8n")
                return data
        
        if isinstance(data, dict):
            if "roadmaps" in data:
                n8n_health.mark_success()
                logging.info(f"✅ Loaded {len(data['roadmaps'])} roadmaps from n8n")
                return data["roadmaps"]
            if "json" in data and "roadmaps" in data["json"]:
                n8n_health.mark_success()
                logging.info(f"✅ Loaded {len(data['json']['roadmaps'])} roadmaps from n8n")
                return data["json"]["roadmaps"]
        
        logging.warning("⚠️ Unexpected n8n response format")
        return []
        
    except requests.exceptions.Timeout:
        logging.warning("⏱️ N8N timeout")
        n8n_health.mark_failure()
        raise
    except requests.exceptions.ConnectionError:
        logging.warning("🔌 N8N connection error")
        n8n_health.mark_failure()
        raise
    except Exception as e:
        logging.error(f"❌ N8N error: {e}")
        n8n_health.mark_failure()
        raise