# GGCloud/services/umami_service.py
import requests
from config import Config
from datetime import datetime, timedelta

class UmamiService:
    """
    Service để tương tác với Umami Analytics API
    """
    
    BASE_URL = f"{Config.UMAMI_URL}/api"
    
    @staticmethod
    def get_auth_token(username='admin', password='umami'):
        """Lấy auth token từ Umami"""
        try:
            response = requests.post(
                f"{UmamiService.BASE_URL}/auth/login",
                json={
                    "username": username,
                    "password": password
                },
                timeout=5
            )

            if response.status_code != 200:
                print(f"Login failed: {response.status_code}, {response.text}")
                return None

            # Response should be JSON — be defensive in case Umami returns HTML or empty body
            try:
                data = response.json()
            except ValueError:
                print(f"Login response is not JSON: {response.text}")
                return None

            return data.get('token')
            
        except Exception as e:
            print(f"Error getting Umami auth token: {e}")
            return None
    
    @staticmethod
    def get_website_stats(days=30):
        """Lấy thống kê website từ Umami"""
        try:
            token = UmamiService.get_auth_token()
            if not token:
                print("No token, returning default stats")
                return UmamiService.get_default_stats()
            
            headers = {"Authorization": f"Bearer {token}"}
            
            # Tính toán start và end date
            end_date = int(datetime.now().timestamp() * 1000)
            start_date = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
            
            # Gọi API để lấy stats
            response = requests.get(
                f"{UmamiService.BASE_URL}/websites/{Config.UMAMI_WEBSITE_ID}/stats",
                headers=headers,
                params={
                    "startAt": start_date,
                    "endAt": end_date
                },
                timeout=8
            )
            
            print(f"Stats API response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                except ValueError:
                    print(f"Stats response is not JSON: {response.text}")
                    return UmamiService.get_default_stats()
                print(f"Stats data structure: {data}")
                
                # Umami trả về cấu trúc khác nhau tùy version
                # Chuẩn hóa data structure
                return {
                    'pageviews': data.get('pageviews', {}) if isinstance(data.get('pageviews'), dict) else {'value': data.get('pageviews', 0)},
                    'uniques': data.get('visitors', {}) if isinstance(data.get('visitors'), dict) else {'value': data.get('visitors', 0)},
                    'visits': data.get('visits', {}) if isinstance(data.get('visits'), dict) else {'value': data.get('visits', 0)},
                    'totaltime': {'value': data.get('totaltime', 0)},
                    'bounces': {'value': data.get('bounces', 0)}
                }
            
            print(f"API error: {response.text}")
            return UmamiService.get_default_stats()
            
        except Exception as e:
            print(f"Error getting Umami stats: {e}")
            return UmamiService.get_default_stats()
    
    @staticmethod
    def get_default_stats():
        """Trả về stats mặc định khi không kết nối được Umami"""
        return {
            'pageviews': {'value': 0},
            'uniques': {'value': 0},
            'visits': {'value': 0},
            'totaltime': {'value': 0},
            'bounces': {'value': 0}
        }
    
    @staticmethod
    def get_page_views(days=30, limit=10):
        """Lấy top pages được xem nhiều nhất"""
        try:
            token = UmamiService.get_auth_token()
            if not token:
                return []
            
            headers = {"Authorization": f"Bearer {token}"}
            
            end_date = int(datetime.now().timestamp() * 1000)
            start_date = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
            
            response = requests.get(
                f"{UmamiService.BASE_URL}/websites/{Config.UMAMI_WEBSITE_ID}/metrics",
                headers=headers,
                params={
                    "startAt": start_date,
                    "endAt": end_date,
                    "type": "url",
                    "limit": limit
                },
                timeout=8
            )
            
            if response.status_code == 200:
                return response.json()
            return []
            
        except Exception as e:
            print(f"Error getting page views: {e}")
            return []
    
    @staticmethod
    def get_events(days=30):
        """Lấy custom events từ Umami"""
        try:
            token = UmamiService.get_auth_token()
            if not token:
                return []
            
            headers = {"Authorization": f"Bearer {token}"}
            
            end_date = int(datetime.now().timestamp() * 1000)
            start_date = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
            
            response = requests.get(
                    f"{UmamiService.BASE_URL}/websites/{Config.UMAMI_WEBSITE_ID}/metrics",
                    headers=headers,
                    params={
                        "startAt": start_date,
                        "endAt": end_date,
                        "type": "event"
                    },
                    timeout=8
                )
            
            if response.status_code == 200:
                return response.json()
            return []
            
        except Exception as e:
            print(f"Error getting events: {e}")
            return []