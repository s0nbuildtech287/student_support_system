import requests
import logging
from n8n.n8n_health_check import n8n_health

N8N_RANKING_URL = "http://localhost:5678/webhook/ranking"

def load_ranking_from_n8n():
    """
    Lấy dữ liệu ranking từ n8n với fast-fail
    
    Returns:
        dict: Ranking data hoặc None nếu lỗi
    """
    # Fast fail
    if not n8n_health.is_n8n_available():
        logging.info("⚡ N8N is down, skip request")
        return None
    
    try:
        res = requests.post(N8N_RANKING_URL, json={}, timeout=2)
        res.raise_for_status()
        
        data = res.json()
        
        # Trường hợp có wrapper success
        if isinstance(data, dict) and data.get('success'):
            ranking_data = data.get('data', {})
            n8n_health.mark_success()
            logging.info(f"✅ Loaded ranking data from n8n")
            return ranking_data
        
        # Trường hợp có json wrapper
        if isinstance(data, dict) and 'json' in data:
            if data['json'].get('success'):
                ranking_data = data['json'].get('data', {})
                n8n_health.mark_success()
                logging.info(f"✅ Loaded ranking data from nested")
                return ranking_data
        
        # Trường hợp trả về trực tiếp data
        if isinstance(data, dict) and 'roadmap_labels' in data:
            n8n_health.mark_success()
            logging.info(f"✅ Loaded ranking data directly")
            return data
        
        logging.warning("⚠️ No ranking data found in n8n response")
        return None
        
    except requests.exceptions.Timeout:
        logging.warning("⏱️ N8N timeout when loading ranking")
        n8n_health.mark_failure()
        return None
    except requests.exceptions.ConnectionError:
        logging.warning("🔌 N8N connection error when loading ranking")
        n8n_health.mark_failure()
        return None
    except Exception as e:
        logging.error(f"❌ Error loading ranking from n8n: {e}")
        n8n_health.mark_failure()
        return None