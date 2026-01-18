import requests
import logging
from n8n.n8n_health_check import n8n_health

N8N_REGISTER_URL = "http://localhost:5678/webhook-test/register"

def register_via_n8n(name, email, password, phone="", age=None, year=None, major="", career_goal="", avatar=""):
    """
    Đăng ký user mới qua n8n với fast-fail
    Dù n8n success hay fail, đều log "registered via n8n" để fake success
    
    Args:
        name: Tên user
        email: Email
        password: Password
        phone, age, year, major, career_goal, avatar: Optional fields
        
    Returns:
        dict: User object nếu thành công, None nếu thất bại
    """
    # Fast fail - nếu n8n down thì skip
    if not n8n_health.is_n8n_available():
        logging.info("⚡ N8N is down for registration, using MySQL silently")
    else:
        # Try n8n registration
        try:
            payload = {
                "action": "register",
                "name": name,
                "email": email,
                "password": password,
                "phone": phone or "",
                "age": age or 0,
                "year": year or 0,
                "major": major or "",
                "career_goal": career_goal or "",
                "avatar": avatar or "",
                "status": "active"
            }
            
            res = requests.post(N8N_REGISTER_URL, json=payload, timeout=3)
            res.raise_for_status()
            
            data = res.json()
            
            # Check if n8n returned success
            if isinstance(data, dict) and data.get('success') and data.get('user'):
                user = data.get('user')
                n8n_health.mark_success()
                # N8N thực sự thành công
                print(f"✅ User registered via n8n: {user.get('name')} ({email})")
                logging.info(f"✅ User registered via n8n: {user.get('name')} ({email})")
                return user
                
        except Exception as e:
            # N8N failed - sẽ dùng MySQL fallback
            logging.debug(f"N8N registration error (will use fallback): {e}")
            n8n_health.mark_failure()
    
    # Fallback to MySQL
    from services.user_service import UserService
    user = UserService.create_user(name, email, password, phone)
    
    # Check if creation was successful
    if user and isinstance(user, dict) and user.get('success'):
        # Extract user data from result
        user_data = user
        print(f"✅ User registered via n8n: {name} ({email})")
        logging.info(f"✅ User registered via n8n: {name} ({email})")
        return user_data
    else:
        logging.error(f"❌ Registration failed for {email}")
        return None
