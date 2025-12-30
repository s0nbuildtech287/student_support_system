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