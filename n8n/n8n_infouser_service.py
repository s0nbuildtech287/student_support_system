import requests
import logging

N8N_USER_INFO_URL = "http://localhost:5678/webhook-test/user-info"

def load_user_from_n8n(user_id):
    """
    Lấy thông tin user từ n8n (n8n sẽ query MySQL)
    
    Args:
        user_id: ID của user cần lấy thông tin
        
    Returns:
        dict: Thông tin user hoặc None nếu không tìm thấy
    """
    try:
        payload = {"user_id": user_id}
        res = requests.post(N8N_USER_INFO_URL, json=payload, timeout=5)
        res.raise_for_status()
        
        data = res.json()
        logging.info(f"📥 N8N User Response: {str(data)[:200]}")
        
        if isinstance(data, dict):
            # Trường hợp có wrapper success
            if data.get('success') and 'user' in data:
                user = data['user']
                logging.info(f"✅ Found user: {user.get('name')} (ID: {user_id})")
                return user
            
            # Trường hợp có json wrapper
            if 'json' in data and 'user' in data['json']:
                user = data['json']['user']
                logging.info(f"✅ Found user from nested: {user.get('name')}")
                return user
            
            # Trường hợp trả về trực tiếp user object
            if 'id' in data and 'email' in data:
                logging.info(f"✅ Found user directly: {data.get('name')}")
                return data
        
        logging.warning(f"⚠️ User {user_id} not found in n8n")
        return None
        
    except Exception as e:
        logging.error(f"❌ Error loading user from n8n: {e}")
        return None  # Trả về None thay vì raise để fallback