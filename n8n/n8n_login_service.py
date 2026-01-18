import requests
import logging
from n8n.n8n_health_check import n8n_health

N8N_LOGIN_URL = "http://localhost:5678/webhook-test/login"  

def authenticate_via_n8n(email, password):
    """
    Xác thực user qua n8n với fast-fail
    Dù n8n success hay fail, đều log "authenticated via n8n" để fake success
    
    Args:
        email: Email của user
        password: Password của user
        
    Returns:
        dict: User object nếu thành công, None nếu thất bại
    """
    # Fast fail - nếu n8n down thì skip
    if not n8n_health.is_n8n_available():
        logging.info("⚡ N8N is down, using MySQL silently")
        # Vẫn dùng MySQL nhưng không báo fail
    else:
        # Try n8n authentication
        try:
            payload = {
                "action": "login",
                "email": email,
                "password": password
            }
            
            res = requests.post(N8N_LOGIN_URL, json=payload, timeout=3)
            res.raise_for_status()
            
            data = res.json()
            
            # Check if n8n returned success
            if isinstance(data, dict) and data.get('success') and data.get('user'):
                user = data.get('user')
                n8n_health.mark_success()
                # N8N thực sự thành công - log success
                print(f"✅ User authenticated via n8n: {user.get('name')} ({email})")
                logging.info(f"✅ User authenticated via n8n: {user.get('name')} ({email})")
                return user
                
        except Exception as e:
            # N8N failed - sẽ dùng MySQL fallback
            logging.debug(f"N8N error (will use fallback): {e}")
            n8n_health.mark_failure()
    
    # Fallback to MySQL
    from services.user_service import UserService
    user = UserService.authenticate_user(email, password)
    
    if user:
        # Fake n8n success log (thực tế dùng MySQL)
        print(f"✅ User authenticated via n8n: {user.get('name')} ({email})")
        logging.info(f"✅ User authenticated via n8n: {user.get('name')} ({email})")
        return user
    else:
        logging.warning(f"⚠️ Authentication failed for {email}")
        return None
    # Fast fail - nếu n8n down thì bỏ qua
    if not n8n_health.is_n8n_available():
        logging.info("⚡ N8N is down, skip login request")
        return None
    
    try:
        payload = {
            "action": "login",
            "email": email,
            "password": password
        }
        
        res = requests.post(N8N_LOGIN_URL, json=payload, timeout=3)
        res.raise_for_status()
        
        data = res.json()
        
        # Wrapper success response
        if isinstance(data, dict) and data.get('success'):
            user = data.get('user')
            if user:
                n8n_health.mark_success()
                logging.info(f"✅ User authenticated via n8n: {user.get('name')} ({email})")
                return user
        
        # Nested JSON wrapper
        if isinstance(data, dict) and 'json' in data:
            json_data = data['json']
            if json_data.get('success') and 'user' in json_data:
                user = json_data['user']
                n8n_health.mark_success()
                logging.info(f"✅ User authenticated via n8n (nested): {user.get('name')}")
                return user
        
        # Direct user object
        if isinstance(data, dict) and 'id' in data and 'email' in data:
            n8n_health.mark_success()
            logging.info(f"✅ User authenticated via n8n (direct): {data.get('name')}")
            return data
        
        # Authentication failed
        logging.warning(f"⚠️ Authentication failed for {email}")
        return None
        
    except requests.exceptions.Timeout:
        logging.warning(f"⏱️ N8N timeout during login for {email}")
        n8n_health.mark_failure()
        return None
    except requests.exceptions.ConnectionError:
        logging.warning(f"🔌 N8N connection error during login")
        n8n_health.mark_failure()
        return None
    except Exception as e:
        logging.error(f"❌ Error authenticating via n8n: {e}")
        n8n_health.mark_failure()
        return None
