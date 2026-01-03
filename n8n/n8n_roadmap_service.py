import requests
import logging

N8N_ROADMAP_URL = "http://localhost:5678/webhook/roadmap-list"

def load_roadmaps_from_n8n():
    try:
        res = requests.post(N8N_ROADMAP_URL, timeout=5)
        res.raise_for_status()
        
        data = res.json()
        
        logging.info(f"📥 N8N Response type: {type(data)}")
        logging.info(f"📥 N8N Response sample: {str(data)[:200]}")
        
        # Trường hợp 1: n8n trả list trực tiếp
        if isinstance(data, list):
            # Nếu list chứa {json: {...}}
            if data and isinstance(data[0], dict) and 'json' in data[0]:
                roadmaps = [item['json'] for item in data]
                logging.info(f"✅ Extracted {len(roadmaps)} roadmaps from list")
                return roadmaps
            # Nếu list chứa roadmap trực tiếp
            else:
                logging.info(f"✅ Got {len(data)} roadmaps directly")
                return data
        
        # Trường hợp 2: n8n trả object với key 'roadmaps'
        if isinstance(data, dict):
            if "roadmaps" in data:
                logging.info(f"✅ Got {len(data['roadmaps'])} roadmaps from dict")
                return data["roadmaps"]
            # Trường hợp dict có json wrapper
            if "json" in data and "roadmaps" in data["json"]:
                logging.info(f"✅ Got {len(data['json']['roadmaps'])} roadmaps from nested dict")
                return data["json"]["roadmaps"]
        
        logging.warning("⚠️ Unexpected n8n response format")
        return []
        
    except Exception as e:
        logging.error(f"❌ N8N Error: {e}")
        raise