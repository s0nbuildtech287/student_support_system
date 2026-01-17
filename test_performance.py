#!/usr/bin/env python3
"""
Test YourPlan performance improvements
"""
import time
from services.yourplan_service import get_user_plans, get_all_subjects_for_modal

def test_yourplan_performance():
    print("=== Testing YourPlan Performance ===\n")
    
    # Test 1: get_user_plans (with caching)
    print("1. Testing get_user_plans...")
    start = time.time()
    plans = get_user_plans(1)
    duration1 = time.time() - start
    print(f"   First call: {duration1:.3f}s ({len(plans)} plans)")
    
    # Second call should be faster (cached)
    start = time.time()
    plans = get_user_plans(1)
    duration2 = time.time() - start
    print(f"   Second call: {duration2:.3f}s (cached)")
    
    if duration2 < duration1:
        print(f"   ✅ Improved by {((duration1 - duration2) / duration1 * 100):.1f}%")
    
    # Test 2: get_all_subjects_for_modal (with caching)
    print("\n2. Testing get_all_subjects_for_modal...")
    start = time.time()
    subjects = get_all_subjects_for_modal()
    duration1 = time.time() - start
    print(f"   First call: {duration1:.3f}s ({len(subjects)} subjects)")
    
    # Second call should be much faster
    start = time.time()
    subjects = get_all_subjects_for_modal()
    duration2 = time.time() - start
    print(f"   Second call: {duration2:.3f}s (cached)")
    
    if duration2 < duration1:
        print(f"   ✅ Improved by {((duration1 - duration2) / duration1 * 100):.1f}%")
    
    print("\n=== Performance Test Complete ===")

if __name__ == "__main__":
    test_yourplan_performance()