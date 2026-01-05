"""
Superset API Service - Kết nối với Apache Superset để lấy dữ liệu chart
"""

import requests
import json
import logging
from config import Config

logger = logging.getLogger(__name__)


class SupersetService:
    """Service để tương tác với Superset API"""
    
    def __init__(self):
        self.base_url = Config.SUPERSET_URL
        self.username = Config.SUPERSET_USERNAME
        self.password = Config.SUPERSET_PASSWORD
        self.access_token = None
        self.refresh_token = None
        self.csrf_token = None
        self.session = requests.Session()
    
    def login(self):
        """
        Đăng nhập vào Superset và lấy access token
        """
        try:
            # Login để lấy access token
            login_url = f"{self.base_url}/api/v1/security/login"
            payload = {
                "username": self.username,
                "password": self.password,
                "provider": "db",
                "refresh": True
            }
            
            response = self.session.post(
                login_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                logger.info("✅ Superset login successful")
                return True
            else:
                logger.error(f"❌ Superset login failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Superset login error: {e}")
            return False
    
    def get_headers(self):
        """Lấy headers với authorization"""
        if not self.access_token:
            self.login()
        
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def get_databases(self):
        """Lấy danh sách databases trong Superset"""
        try:
            url = f"{self.base_url}/api/v1/database/"
            response = self.session.get(url, headers=self.get_headers())
            
            if response.status_code == 200:
                return response.json().get("result", [])
            logger.error(f"Get databases failed: {response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Error getting databases: {e}")
            return []
    
    def get_datasets(self):
        """Lấy danh sách datasets trong Superset"""
        try:
            url = f"{self.base_url}/api/v1/dataset/"
            response = self.session.get(url, headers=self.get_headers())
            
            if response.status_code == 200:
                return response.json().get("result", [])
            logger.error(f"Get datasets failed: {response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Error getting datasets: {e}")
            return []
    
    def get_charts(self):
        """Lấy danh sách charts trong Superset"""
        try:
            url = f"{self.base_url}/api/v1/chart/"
            response = self.session.get(url, headers=self.get_headers())
            
            if response.status_code == 200:
                return response.json().get("result", [])
            logger.error(f"Get charts failed: {response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Error getting charts: {e}")
            return []
    
    def get_chart_by_id(self, chart_id):
        """
        Lấy thông tin chi tiết của một chart
        """
        try:
            url = f"{self.base_url}/api/v1/chart/{chart_id}"
            response = self.session.get(url, headers=self.get_headers())
            
            if response.status_code == 200:
                return response.json().get("result", {})
            logger.error(f"Get chart {chart_id} failed: {response.status_code}")
            return None
        except Exception as e:
            logger.error(f"Error getting chart: {e}")
            return None
    
    def get_chart_data(self, chart_id):
        """
        Lấy dữ liệu của một chart cụ thể bằng cách gọi explore_json
        """
        try:
            # Lấy thông tin chart trước
            chart_info = self.get_chart_by_id(chart_id)
            if not chart_info:
                return None
            
            # Lấy form_data từ chart
            form_data = chart_info.get("params", "{}")
            if isinstance(form_data, str):
                form_data = json.loads(form_data)
            
            # Thêm datasource info
            datasource_id = chart_info.get("datasource_id")
            datasource_type = chart_info.get("datasource_type", "table")
            
            form_data["datasource"] = f"{datasource_id}__{datasource_type}"
            
            # Gọi API explore_json để lấy data
            url = f"{self.base_url}/api/v1/chart/data"
            
            payload = {
                "datasource": {
                    "id": datasource_id,
                    "type": datasource_type
                },
                "queries": [{
                    "columns": form_data.get("groupby", []),
                    "metrics": form_data.get("metrics", []),
                    "orderby": form_data.get("orderby", []),
                    "row_limit": form_data.get("row_limit", 100)
                }]
            }
            
            response = self.session.post(
                url,
                json=payload,
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            
            # Fallback: thử endpoint khác
            url_alt = f"{self.base_url}/superset/explore_json/"
            params = {
                "form_data": json.dumps(form_data),
                "datasource_id": datasource_id,
                "datasource_type": datasource_type
            }
            
            response = self.session.get(url_alt, params=params, headers=self.get_headers())
            
            if response.status_code == 200:
                return response.json()
            
            logger.error(f"Get chart data failed: {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting chart data: {e}")
            return None
    
    def get_chart_data_simple(self, chart_id):
        """
        Lấy dữ liệu chart đơn giản hơn bằng warm up cache
        """
        try:
            # Warm up cache để có data
            url = f"{self.base_url}/api/v1/chart/warm_up_cache"
            payload = {"chart_id": chart_id}
            
            response = self.session.put(
                url,
                json=payload,
                headers=self.get_headers()
            )
            
            if response.status_code == 200:
                return response.json()
            
            return {"error": f"Failed with status {response.status_code}"}
        except Exception as e:
            logger.error(f"Error warming up chart: {e}")
            return {"error": str(e)}
    
    def get_dashboards(self):
        """Lấy danh sách dashboards"""
        try:
            url = f"{self.base_url}/api/v1/dashboard/"
            response = self.session.get(url, headers=self.get_headers())
            
            if response.status_code == 200:
                return response.json().get("result", [])
            return []
        except Exception as e:
            logger.error(f"Error getting dashboards: {e}")
            return []
    
    def get_dashboard_charts(self, dashboard_id):
        """
        Lấy danh sách charts trong một dashboard
        """
        try:
            url = f"{self.base_url}/api/v1/dashboard/{dashboard_id}/charts"
            response = self.session.get(url, headers=self.get_headers())
            
            if response.status_code == 200:
                return response.json().get("result", [])
            return []
        except Exception as e:
            logger.error(f"Error getting dashboard charts: {e}")
            return []
    
    def execute_query(self, database_id, sql_query):
        """
        Thực thi SQL query trực tiếp qua Superset SQL Lab API
        """
        try:
            # Lấy CSRF token nếu cần
            csrf_url = f"{self.base_url}/api/v1/security/csrf_token/"
            csrf_response = self.session.get(csrf_url, headers=self.get_headers())
            
            csrf_token = ""
            if csrf_response.status_code == 200:
                csrf_token = csrf_response.json().get("result", "")
            
            headers = self.get_headers()
            if csrf_token:
                headers["X-CSRFToken"] = csrf_token
            
            url = f"{self.base_url}/api/v1/sqllab/execute/"
            payload = {
                "database_id": database_id,
                "sql": sql_query,
                "runAsync": False,
                "select_as_cta": False
            }
            
            response = self.session.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Query failed: {response.status_code} - {response.text[:200]}")
                return {"error": response.text[:200]}
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return {"error": str(e)}
    
    def get_all_chart_data_for_web(self):
        """
        Lấy tất cả dữ liệu charts để hiển thị trên web
        Trả về format phù hợp với Chart.js
        """
        result = {
            "charts": [],
            "error": None
        }
        
        try:
            charts = self.get_charts()
            
            for chart in charts:
                chart_id = chart.get("id")
                chart_name = chart.get("slice_name", "Unknown")
                viz_type = chart.get("viz_type", "bar")
                
                # Lấy data của chart
                chart_data = self.get_chart_data(chart_id)
                
                if chart_data:
                    result["charts"].append({
                        "id": chart_id,
                        "name": chart_name,
                        "type": viz_type,
                        "data": chart_data
                    })
            
            return result
            
        except Exception as e:
            result["error"] = str(e)
            return result


# Global instance
superset_service = SupersetService()
