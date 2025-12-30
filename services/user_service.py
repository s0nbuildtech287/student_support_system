import csv
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

USER_DATA_FILE = r"e:\xuanson_2\student_support_system\data\users.csv"

class UserService:
    @staticmethod
    def load_users():
        users = []
        if not os.path.exists(USER_DATA_FILE):
             return users
        
        with open(USER_DATA_FILE, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                users.append(row)
        return users

    @staticmethod
    def save_users(users):
        if not users:
            return
        
        fieldnames = list(users[0].keys())
        with open(USER_DATA_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(users)

    @staticmethod
    def get_user_by_email(email):
        users = UserService.load_users()
        for user in users:
            if user['email'] == email:
                return user
        return None

    @staticmethod
    def get_user_by_id(user_id):
        users = UserService.load_users()
        for user in users:
            if str(user['id']) == str(user_id):
                return user
        return None

    @staticmethod
    def register_user(fullname, email, password, phone):
        if UserService.get_user_by_email(email):
            return False, "Email already exists"

        users = UserService.load_users()
        new_id = len(users) + 1
        
        # Default values for new user
        new_user = {
            "id": new_id,
            "fullname": fullname,
            "email": email,
            "password_hash": generate_password_hash(password),
            "phone": phone,
            "age": 0,
            "height": 0,
            "weight": 0,
            "goal": "Not set",
            "experience": "Beginner",
            "avatar": "/static/images/avatar.jpg",
            "joined_date": datetime.now().strftime("%Y-%m-%d"),
            "total_workouts": 0
        }
        
        users.append(new_user)
        UserService.save_users(users)
        return True, "User registered successfully"

    @staticmethod
    def login_user(email, password):
        user = UserService.get_user_by_email(email)
        if user and check_password_hash(user['password_hash'], password):
            return user
        return None
