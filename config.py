import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MySQL Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'student_support')
    
    # Flask Configuration - đơn giản thôi
    SECRET_KEY = 'my-secret-key-123456'  # Hardcode luôn cho đơn giản

    # Groq API
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')

    # Dify Chatbot
    DIFY_CHAT_URL = os.getenv('DIFY_CHAT_URL', '')
    DIFY_API_KEY = os.getenv('DIFY_API_KEY', '')
    DIFY_API_URL = os.getenv('DIFY_API_URL', 'https://api.dify.ai/v1')

    # Umami Analytics
    UMAMI_WEBSITE_ID = os.getenv('UMAMI_WEBSITE_ID', '91d08d66-491e-4dc0-bf82-78d9db867f88')
    UMAMI_URL = os.getenv('UMAMI_URL', 'http://localhost:3000')

    # Superset Configuration
    SUPERSET_URL = os.getenv('SUPERSET_URL', 'http://localhost:8088')
    SUPERSET_USERNAME = os.getenv('SUPERSET_USERNAME', 'admin')
    SUPERSET_PASSWORD = os.getenv('SUPERSET_PASSWORD', 'admin')