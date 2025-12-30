import sys
import os
sys.path.append(r"e:\xuanson_2\student_support_system")

from app import app
from services.user_service import UserService

def verify_auth():
    print("Starting verification...")
    
    # Clean up test user if exists
    users = UserService.load_users()
    users = [u for u in users if u['email'] != 'testAuth@example.com']
    UserService.save_users(users)
    
    with app.test_client() as client:
        # 1. Test Registration
        print("\nTest 1: Registration")
        res = client.post('/register', data={
            'fullname': 'Test User',
            'email': 'testAuth@example.com',
            'password': 'password123',
            'confirm_password': 'password123',
            'phone': '1234567890'
        }, follow_redirects=True)
        
        if b'User registered successfully' in res.data or b'Login' in res.data: 
             print("Registration successful.")
        else:
             print("Registration FAILED.")
             print(res.data)

        # 2. Test Login
        print("\nTest 2: Login")
        res = client.post('/login', data={
            'email': 'testAuth@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        
        if b'Study With AI' in res.data or b'home' in res.data or res.request.path == "/home":
            print("Login successful.")
        else:
            print("Login FAILED.")
            print(res.data) # might print a lot of html

        # 3. Test Protected Route (Logout then access profile)
        print("\nTest 3: Protected Route")
        client.get('/logout', follow_redirects=True)
        res = client.get('/profile', follow_redirects=True)
        
        if b'Login' in res.data or res.request.path == "/login":
            print("Access protected route blocked successfully (redirected to login).")
        else:
            print("Access protected route FAILED (did not redirect). heading to:", res.request.path)

    # Check CSV
    print("\nChecking CSV...")
    users = UserService.load_users()
    test_user = next((u for u in users if u['email'] == 'testAuth@example.com'), None)
    if test_user:
        print(f"User found in CSV: {test_user['fullname']}")
    else:
        print("User NOT found in CSV.")

if __name__ == "__main__":
    verify_auth()
