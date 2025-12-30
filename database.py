import mysql.connector
from mysql.connector import Error
from config import Config

def get_db_connection():
    """Tạo kết nối đến MySQL database"""
    try:
        connection = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        return connection
    except Error as e:
        print(f"Lỗi kết nối database: {e}")
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
    except Error as e:
        print(f"Lỗi thực thi query: {e}")
        return False

def fetch_one(query, params=None):
    """Lấy 1 record từ database"""
    connection = get_db_connection()
    if connection is None:
        return None
    
    try:
        cursor = connection.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result
    except Error as e:
        print(f"Lỗi fetch data: {e}")
        return None

def fetch_all(query, params=None):
    """Lấy nhiều records từ database"""
    connection = get_db_connection()
    if connection is None:
        return []
    
    try:
        cursor = connection.cursor(dictionary=True)
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results
    except Error as e:
        print(f"Lỗi fetch data: {e}")
        return []