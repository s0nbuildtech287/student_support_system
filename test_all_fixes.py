#!/usr/bin/env python3
"""
Test all PostgreSQL fixes
"""
from database import fetch_one, fetch_all

def test_all_fixes():
    print("=== Testing All PostgreSQL Fixes ===\n")
    
    # Test 1: Boolean queries
    print("1. Testing boolean queries...")
    try:
        # Test passed = TRUE
        result = fetch_all("SELECT COUNT(*) as count FROM quiz_attempts WHERE passed = TRUE")
        passed_count = result[0]['count'] if result else 0
        print(f"   ✅ passed = TRUE works: {passed_count} records")
        
        # Test passed = FALSE  
        result = fetch_all("SELECT COUNT(*) as count FROM quiz_attempts WHERE passed = FALSE")
        failed_count = result[0]['count'] if result else 0
        print(f"   ✅ passed = FALSE works: {failed_count} records")
        
    except Exception as e:
        print(f"   ❌ Boolean query failed: {e}")
        return False
    
    # Test 2: Check study plans
    print("\n2. Testing study plans...")
    try:
        result = fetch_all("SELECT COUNT(*) as count FROM study_plans WHERE is_started = TRUE")
        started = result[0]['count'] if result else 0
        print(f"   ✅ is_started = TRUE works: {started} started plans")
        
        result = fetch_all("SELECT COUNT(*) as count FROM study_plans WHERE is_started = FALSE")
        not_started = result[0]['count'] if result else 0
        print(f"   ✅ is_started = FALSE works: {not_started} not started plans")
        
    except Exception as e:
        print(f"   ❌ Study plans query failed: {e}")
        return False
    
    # Test 3: CASE statements
    print("\n3. Testing CASE statements...")
    try:
        query = """
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN passed = TRUE THEN 1 ELSE 0 END) as passed,
                SUM(CASE WHEN passed = FALSE THEN 1 ELSE 0 END) as failed
            FROM quiz_attempts
        """
        result = fetch_one(query)
        if result:
            print(f"   ✅ CASE statements work: {result['total']} total, {result['passed']} passed, {result['failed']} failed")
        else:
            print("   ⚠️  No quiz attempts found")
            
    except Exception as e:
        print(f"   ❌ CASE statement failed: {e}")
        return False
    
    # Test 4: Random query
    print("\n4. Testing RANDOM() function...")
    try:
        result = fetch_all("SELECT id FROM quizzes ORDER BY RANDOM() LIMIT 3")
        print(f"   ✅ RANDOM() works: Got {len(result)} random records")
    except Exception as e:
        print(f"   ❌ RANDOM() failed: {e}")
        return False
    
    print("\n=== All Tests Passed! ✅ ===")
    return True

if __name__ == "__main__":
    test_all_fixes()