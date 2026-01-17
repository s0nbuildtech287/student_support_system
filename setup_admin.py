#!/usr/bin/env python3
"""
Script to add admin role to admin@gmail.com user
Run this if you can't access /admin/ dashboard
"""
from database import fetch_one, execute_query

def setup_admin():
    print("=== Setting up Admin User ===\n")
    
    # 1. Check if admin@gmail.com exists
    user = fetch_one("SELECT id, email FROM users WHERE email = %s", ('admin@gmail.com',))
    
    if not user:
        print("❌ User admin@gmail.com not found!")
        print("Please register with admin@gmail.com first")
        return False
    
    user_id = user['id']
    print(f"✅ Found user: {user['email']} (ID: {user_id})")
    
    # 2. Check if already admin
    admin = fetch_one("SELECT role FROM admin_users WHERE user_id = %s", (user_id,))
    
    if admin:
        print(f"✅ User already has admin role: {admin['role']}")
        return True
    
    # 3. Add admin role
    print("\n🔧 Adding admin role...")
    success = execute_query(
        "INSERT INTO admin_users (user_id, role) VALUES (%s, %s)",
        (user_id, 'admin')
    )
    
    if success:
        print("✅ Admin role added successfully!")
        print(f"\n🎉 You can now access /admin/ with admin@gmail.com")
        return True
    else:
        print("❌ Failed to add admin role")
        return False

if __name__ == "__main__":
    setup_admin()