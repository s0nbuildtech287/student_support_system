#!/usr/bin/env python3
"""
Test PostgreSQL compatibility
"""
from database import fetch_one, fetch_all

def test_db_connection():
    """Test basic database connection"""
    try:
        result = fetch_one("SELECT 1 as test")
        print("✅ Database connection: OK")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_quizzes_table():
    """Test quizzes table"""
    try:
        result = fetch_one("SELECT COUNT(*) as count FROM quizzes")
        print(f"✅ Quizzes table: {result['count']} records")
        return True
    except Exception as e:
        print(f"❌ Quizzes table error: {e}")
        return False

def test_quiz_for_subject():
    """Test getting quiz for a subject"""
    try:
        result = fetch_all("SELECT COUNT(*) as count FROM quizzes WHERE subject_id = %s", (1,))
        if result:
            count = result[0]['count']
            print(f"✅ Quiz for subject 1: {count} questions")
            return count > 0
        else:
            print("❌ No quiz data returned")
            return False
    except Exception as e:
        print(f"❌ Quiz query error: {e}")
        return False

def test_random_query():
    """Test RANDOM() function"""
    try:
        result = fetch_all("SELECT id FROM quizzes ORDER BY RANDOM() LIMIT 3")
        print(f"✅ Random query: Got {len(result)} random records")
        return True
    except Exception as e:
        print(f"❌ Random query error: {e}")
        return False

def test_quiz_distribution():
    """Check quiz distribution by subject"""
    try:
        result = fetch_all("SELECT subject_id, COUNT(*) as count FROM quizzes GROUP BY subject_id ORDER BY subject_id LIMIT 20")
        print("✅ Quiz distribution by subject:")
        for r in result:
            print(f"  Subject {r['subject_id']}: {r['count']} questions")
        return True
    except Exception as e:
        print(f"❌ Quiz distribution error: {e}")
        return False

if __name__ == "__main__":
    print("=== PostgreSQL Compatibility Test ===\n")
    
    tests = [
        test_db_connection,
        test_quizzes_table, 
        test_quiz_for_subject,
        test_random_query,
        test_quiz_distribution
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    passed = sum(results)
    total = len(results)
    
    print(f"=== Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("🎉 All tests passed! PostgreSQL compatibility OK")
    else:
        print("⚠️ Some tests failed. Check database configuration.")