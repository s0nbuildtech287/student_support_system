#!/usr/bin/env python
"""Database initialization script"""

from app import create_app
from models import db
from seed import seed_database

def init_database():
    """Initialize database"""
    app = create_app()
    
    with app.app_context():
        try:
            print("\n📊 Creating tables...")
            db.create_all()
            print("✅ Tables created successfully!")
            
            # Ask to seed data
            response = input("\n❓ Do you want to seed initial data? (y/n): ").strip().lower()
            if response == 'y':
                seed_database()
                print("\n✅ Database seeded successfully!")
            else:
                print("\n⏭️  Skipping seed data")
            
            print("\n🎉 Database initialization completed!")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            exit(1)

if __name__ == "__main__":
    init_database()
