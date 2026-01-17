import mysql.connector
from mysql.connector import Error as MySQLError
import psycopg2
import psycopg2.extras
from psycopg2 import Error as PostgreSQLError
from config import Config
import os

def get_db_connection():
    """Tạo kết nối database (MySQL local hoặc PostgreSQL production)"""
    # Kiểm tra environment hoặc có PostgreSQL config không
    use_postgres = (
        Config.ENVIRONMENT == 'production' or 
        os.getenv('POSTGRES_URL') or 
        os.getenv('VERCEL') or
        Config.POSTGRES_HOST
    )
    
    if use_postgres:
        return get_postgres_connection()
    else:
        return get_mysql_connection()

def get_mysql_connection():
    """Tạo kết nối đến MySQL database (Local)"""
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        return connection
    except MySQLError as e:
        print(f"Lỗi kết nối MySQL: {e}")
        return None

def get_postgres_connection():
    """Tạo kết nối đến PostgreSQL database (Production)"""
    try:
        # Ưu tiên dùng POSTGRES_URL nếu có
        if Config.POSTGRES_URL:
            connection = psycopg2.connect(Config.POSTGRES_URL)
        else:
            connection = psycopg2.connect(
                host=Config.POSTGRES_HOST,
                port=Config.POSTGRES_PORT,
                user=Config.POSTGRES_USER,
                password=Config.POSTGRES_PASSWORD,
                database=Config.POSTGRES_DB
            )
        return connection
    except PostgreSQLError as e:
        print(f"Lỗi kết nối PostgreSQL: {e}")
        return None

def execute_query(query, params=None):
    """Thực thi query INSERT, UPDATE, DELETE"""
    connection = get_db_connection()
    if connection is None:
        return False
    
    try:
        cursor = connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except (MySQLError, PostgreSQLError) as e:
        print(f"Lỗi thực thi query: {e}")
        return False

def fetch_one(query, params=None):
    """Lấy 1 record từ database"""
    connection = get_db_connection()
    if connection is None:
        return None
    
    try:
        # Check connection type để tạo cursor phù hợp
        if hasattr(connection, 'cursor') and 'mysql' in str(type(connection)):
            cursor = connection.cursor(dictionary=True)  # MySQL
        else:
            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  # PostgreSQL
            
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return dict(result) if result else None
    except (MySQLError, PostgreSQLError) as e:
        print(f"Lỗi fetch data: {e}")
        return None

def fetch_all(query, params=None):
    """Lấy nhiều records từ database"""
    connection = get_db_connection()
    if connection is None:
        return []
    
    try:
        # Check connection type để tạo cursor phù hợp
        if hasattr(connection, 'cursor') and 'mysql' in str(type(connection)):
            cursor = connection.cursor(dictionary=True)  # MySQL
        else:
            cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)  # PostgreSQL
            
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return [dict(row) for row in results] if results else []
    except (MySQLError, PostgreSQLError) as e:
        print(f"Lỗi fetch data: {e}")
        return []