import requests
import logging

N8N_FEEDBACK_URL = "http://localhost:5678/webhook/feedback"

def add_feedback_via_n8n(user_id, name, avatar, comment, stars=5):
    """
    Thêm feedback mới qua n8n
    
    Args:
        user_id: ID của user (hoặc None nếu guest)
        name: Tên người đánh giá
        avatar: URL avatar
        comment: Nội dung đánh giá
        stars: Số sao (1-5)
        
    Returns:
        bool: True nếu thành công, False nếu thất bại
    """
    try:
        payload = {
            "action": "add",
            "user_id": user_id,
            "name": name,
            "avatar": avatar,
            "comment": comment,
            "stars": stars
        }
        
        res = requests.post(N8N_FEEDBACK_URL, json=payload, timeout=5)
        res.raise_for_status()
        
        data = res.json()
        
        if data.get('success'):
            logging.info(f"✅ Added feedback via n8n: {name}")
            return True
        else:
            logging.warning(f"⚠️ Failed to add feedback via n8n")
            return False
            
    except Exception as e:
        logging.error(f"❌ Error adding feedback via n8n: {e}")
        return False


def get_feedbacks_via_n8n(limit=100):
    """
    Lấy danh sách feedbacks qua n8n
    
    Args:
        limit: Số lượng feedback tối đa
        
    Returns:
        list: Danh sách feedbacks hoặc None nếu lỗi
    """
    try:
        payload = {
            "action": "get",
            "limit": limit
        }
        
        res = requests.post(N8N_FEEDBACK_URL, json=payload, timeout=5)
        res.raise_for_status()
        
        data = res.json()
        
        if isinstance(data, dict) and data.get('success'):
            feedbacks = data.get('feedbacks', [])
            logging.info(f"✅ Loaded {len(feedbacks)} feedbacks from n8n")
            return feedbacks
        
        # Trường hợp có json wrapper
        if isinstance(data, dict) and 'json' in data:
            if data['json'].get('success'):
                feedbacks = data['json'].get('feedbacks', [])
                logging.info(f"✅ Loaded {len(feedbacks)} feedbacks from nested")
                return feedbacks
        
        logging.warning("⚠️ No feedbacks found in n8n response")
        return None
        
    except Exception as e:
        logging.error(f"❌ Error loading feedbacks from n8n: {e}")
        return None