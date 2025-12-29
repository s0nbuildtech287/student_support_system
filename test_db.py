#!/usr/bin/env python
"""Test database connection"""

import sys
import os
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    """Test MariaDB connection"""
    print("\n" + "="*60)
    print("🔍 Testing MariaDB Connection")
    print("="*60 + "\n")
    
    # Check environment variables
    print("📋 Configuration:")
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_user = os.getenv('DB_USER')
    db_name = os.getenv('DB_NAME')
    
    print(f"   Host: {db_host}")
    print(f"   Port: {db_port}")
    print(f"   User: {db_user}")
    print(f"   Database: {db_name}")
    print()
    
    try:
        # Test direct connection
        print("🔗 Attempting direct connection...")
        import pymysql
        
        connection = pymysql.connect(
            host=db_host,
            port=int(db_port),
            user=db_user,
            password=os.getenv('DB_PASSWORD'),
            database=db_name,
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"✅ Direct connection successful!")
            print(f"   MariaDB Version: {version[0]}\n")
        
        connection.close()
        
        # Test Flask connection
        print("🔗 Testing Flask-SQLAlchemy connection...")
        from app import create_app
        from models import db, User
        
        app = create_app()
        
        with app.app_context():
            # Test database
            result = db.session.execute(db.text("SELECT COUNT(*) as count FROM users"))
            count = result.fetchone()[0]
            print(f"✅ Flask-SQLAlchemy connection successful!")
            print(f"   Users in database: {count}\n")
            
            # List tables
            result = db.session.execute(db.text(
                "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = DATABASE()"
            ))
            tables = result.fetchall()
            print(f"📊 Tables in database ({len(tables)}):")
            for table in tables:
                print(f"   ✓ {table[0]}")
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60 + "\n")
        
        return True
        
    except pymysql.Error as e:
        print(f"❌ MySQL Connection Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Check if MariaDB is running")
        print("   2. Check .env credentials")
        print("   3. Check if database exists: CREATE DATABASE studywithai;")
        return False
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
