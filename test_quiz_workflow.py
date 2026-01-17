#!/usr/bin/env python3
"""
Test complete quiz workflow
"""
from database import fetch_one, fetch_all
from services.quiz_service import get_random_quiz_questions, submit_quiz
from services.yourplan_service import get_user_plans

def test_complete_quiz_workflow():
    """Test complete quiz workflow"""
    print("=== Complete Quiz Workflow Test ===\n")
    
    # 1. Check user exists
    user = fetch_one("SELECT id FROM users LIMIT 1")
    if not user:
        print("❌ No users found in database")
        return False
    user_id = user['id']
    print(f"✅ Using user_id: {user_id}")
    
    # 2. Check user plans
    plans = get_user_plans(user_id)
    if not plans:
        print("❌ User has no study plans")
        return False
    
    # Try plan_id 1 first
    plan_id = None
    for plan in plans:
        plan_subjects = fetch_all("SELECT subject_id FROM plan_subjects WHERE plan_id = %s", (plan['id'],))
        if plan_subjects:
            plan_id = plan['id']
            break
    
    if not plan_id:
        print("❌ No plans with subjects found")
        return False
    
    print(f"✅ Using plan_id: {plan_id}")
    
    # 3. Check plan subjects
    plan_subjects = fetch_all("SELECT subject_id FROM plan_subjects WHERE plan_id = %s", (plan_id,))
    if not plan_subjects:
        print("❌ Plan has no subjects")
        return False
    subject_id = plan_subjects[0]['subject_id']
    print(f"✅ Using subject_id: {subject_id}")
    
    # 4. Test get quiz questions
    try:
        questions = get_random_quiz_questions(subject_id, 3)
        if not questions:
            print(f"❌ No questions found for subject {subject_id}")
            return False
        print(f"✅ Got {len(questions)} quiz questions")
        
        # 5. Simulate quiz submission
        answers = {}
        for q in questions:
            answers[q['id']] = 'a'  # Select first option for all
        
        result = submit_quiz(user_id, subject_id, answers, plan_id)
        if result.get('success'):
            print(f"✅ Quiz submitted successfully: {result['score']}/{result['total']}")
            return True
        else:
            print(f"❌ Quiz submission failed: {result.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ Quiz workflow error: {e}")
        return False

if __name__ == "__main__":
    test_complete_quiz_workflow()