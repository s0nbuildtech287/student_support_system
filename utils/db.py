import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

def get_db_connection():
    """Tạo kết nối đến MySQL database"""
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )
        return connection
    except Error as e:
        # Avoid non-ASCII to prevent Windows console encoding errors
        print(f"Database connection error: {e}")
        return None

def init_database():
    """Khởi tạo bảng users nếu chưa tồn tại"""
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            create_table_query = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fullname VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_query)
            connection.commit()
            print("Users table created or already exists.")
        except Error as e:
            print(f"Error when creating table: {e}")
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

