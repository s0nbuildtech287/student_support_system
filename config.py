import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MySQL Configuration
    # Ưu tiên DATABASE_URL nếu có (PlanetScale/Railway)
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Fallback: MySQL connection thông thường
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'student_support')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Groq API
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')

    # Dify Chatbot
    DIFY_CHAT_URL = os.getenv('DIFY_CHAT_URL', '')
    DIFY_API_KEY = os.getenv('DIFY_API_KEY', '')
    DIFY_API_URL = os.getenv('DIFY_API_URL', 'https://api.dify.ai/v1')

    # Umami Analytics
    UMAMI_WEBSITE_ID = os.getenv('UMAMI_WEBSITE_ID', '')
    UMAMI_URL = os.getenv('UMAMI_URL', '')

    # Superset Configuration
    SUPERSET_URL = os.getenv('SUPERSET_URL', '')
    SUPERSET_USERNAME = os.getenv('SUPERSET_USERNAME', '')
    SUPERSET_PASSWORD = os.getenv('SUPERSET_PASSWORD', '')