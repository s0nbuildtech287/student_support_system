#!/usr/bin/env python
"""Quick database initialization"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    from app import create_app
    from models import db
    
    print("\n" + "="*50)
    print("📊 Study With AI - Database Initialization")
    print("="*50 + "\n")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Drop all tables and recreate (for development only)
            print("⚠️  Dropping existing tables...")
            db.drop_all()
            
            print("📋 Creating new tables...")
            db.create_all()
            print("✅ Tables created successfully!")
            
            # Seed data
            print("\n📝 Seeding initial data...")
            from seed import seed_database
            seed_database()
            
            print("\n✅ Database initialization completed!")
            print("\n🎯 Test Account:")
            print("   Email: khang@example.com")
            print("   Name: Khang Nguyen")
            print("   Password: (set during registration)\n")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    main()
