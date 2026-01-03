import requests
import logging
import time
from threading import Lock

class N8NHealthCheck:
    """
    Singleton class để kiểm tra health của n8n service
    Tránh phải check timeout mỗi request
    """
    _instance = None
    _lock = Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.is_healthy = True  # Mặc định coi như n8n đang hoạt động
        self.last_check = 0
        self.check_interval = 10  # Check lại sau 10 giây
        self.failure_count = 0
        self.max_failures = 2  # Sau 2 lần fail thì đánh dấu down
        self._initialized = True
        
        logging.info("🔧 N8N Health Check initialized")
    
    def is_n8n_available(self):
        """
        Kiểm tra xem n8n có available không
        Sử dụng cache để tránh check liên tục
        
        Returns:
            bool: True nếu n8n available, False nếu down
        """
        current_time = time.time()
        
        # Nếu chưa đến lúc check lại, dùng cached result
        if current_time - self.last_check < self.check_interval:
            return self.is_healthy
        
        # Đã đến lúc check lại
        self.last_check = current_time
        return self._perform_health_check()
    
    def _perform_health_check(self):
        """
        Thực hiện health check thực sự
        """
        try:
            # Ping n8n với timeout ngắn
            res = requests.get("http://localhost:5678/healthz", timeout=1)
            
            if res.status_code == 200:
                if not self.is_healthy:
                    logging.info("✅ N8N is back online!")
                self.is_healthy = True
                self.failure_count = 0
                return True
            else:
                self._handle_failure()
                return False
                
        except requests.exceptions.Timeout:
            logging.warning("⏱️ N8N health check timeout")
            self._handle_failure()
            return False
        except requests.exceptions.ConnectionError:
            logging.warning("🔌 N8N connection refused")
            self._handle_failure()
            return False
        except Exception as e:
            logging.warning(f"⚠️ N8N health check error: {e}")
            self._handle_failure()
            return False
    
    def _handle_failure(self):
        """Xử lý khi health check thất bại"""
        self.failure_count += 1
        
        if self.failure_count >= self.max_failures:
            if self.is_healthy:
                logging.error("❌ N8N marked as DOWN after multiple failures")
            self.is_healthy = False
    
    def mark_success(self):
        """Đánh dấu một request thành công"""
        if not self.is_healthy:
            logging.info("✅ N8N connection restored")
        self.is_healthy = True
        self.failure_count = 0
    
    def mark_failure(self):
        """Đánh dấu một request thất bại"""
        self._handle_failure()


# Singleton instance
n8n_health = N8NHealthCheck()