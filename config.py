import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # PostgreSQL Configuration
    POSTGRES_HOST = os.getenv('POSTGRES_HOST', '')
    POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
    POSTGRES_USER = os.getenv('POSTGRES_USER', '')
    POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')
    POSTGRES_DB = os.getenv('POSTGRES_DB', '')
    POSTGRES_URL = os.getenv('POSTGRES_URL', '')
    
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