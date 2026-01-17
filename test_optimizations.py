"""
Test script for optimized add_subject_to_plan and apply_roadmap_to_user_plan
Measures performance improvement from batch queries
"""

import time
from services.roadmap_service import apply_roadmap_to_user_plan, get_all_roadmaps
from services.yourplan_service import add_subject_to_plan, get_user_plans
from database import execute_query, fetch_one

def cleanup_test_data(user_id):
    """Clean up test plans"""
    execute_query("DELETE FROM plan_subjects WHERE plan_id IN (SELECT id FROM study_plans WHERE user_id = %s)", (user_id,))
    execute_query("DELETE FROM study_plans WHERE user_id = %s", (user_id,))
    print("✓ Cleaned up test data")

def test_apply_roadmap_performance():
    """Test apply roadmap with batch inserts"""
    user_id = 3  # Admin user
    
    # Get first roadmap
    roadmaps = get_all_roadmaps()
    if not roadmaps:
        print("❌ No roadmaps found")
        return
    
    roadmap_id = roadmaps[0]['roadmap_id']
    
    print(f"\n{'='*60}")
    print(f"TEST 1: Apply Roadmap (ID={roadmap_id}) - Batch Insert")
    print(f"{'='*60}")
    
    # Clean up first
    cleanup_test_data(user_id)
    
    # Measure performance
    start = time.time()
    result = apply_roadmap_to_user_plan(user_id, roadmap_id)
    elapsed = time.time() - start
    
    if result['success']:
        print(f"✅ {result['message']}")
        print(f"⏱️  Time: {elapsed:.3f}s")
        
        # Verify data
        plans = get_user_plans(user_id)
        if plans:
            subjects_count = len(plans[0].get('subjects', []))
            print(f"📊 Verified: {subjects_count} subjects in plan")
    else:
        print(f"❌ {result['message']}")
    
    return elapsed

def test_add_subject_performance():
    """Test add single subject with optimized query"""
    user_id = 3
    
    print(f"\n{'='*60}")
    print(f"TEST 2: Add Single Subject - Optimized Query")
    print(f"{'='*60}")
    
    # Get or create a plan
    plans = get_user_plans(user_id)
    if not plans:
        print("❌ No plans found. Run test 1 first.")
        return
    
    plan_id = plans[0]['id']
    
    # Try adding subject ID 1 (should be fast)
    start = time.time()
    result = add_subject_to_plan(plan_id, user_id, 1)
    elapsed = time.time() - start
    
    print(f"{'✅' if result['success'] else '⚠️'} {result['message']}")
    print(f"⏱️  Time: {elapsed:.3f}s (single query)")
    
    return elapsed

def test_add_multiple_subjects():
    """Test adding multiple subjects sequentially"""
    user_id = 3
    
    print(f"\n{'='*60}")
    print(f"TEST 3: Add 5 Subjects Sequentially")
    print(f"{'='*60}")
    
    # Clean and create new plan
    cleanup_test_data(user_id)
    execute_query(
        "INSERT INTO study_plans (user_id, name, description, is_started, created_at) VALUES (%s, %s, %s, FALSE, NOW())",
        (user_id, "Test Plan", "For performance testing")
    )
    
    plan = fetch_one("SELECT id FROM study_plans WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
    plan_id = plan['id']
    
    subject_ids = [1, 2, 3, 4, 5]
    
    start = time.time()
    success_count = 0
    
    for sid in subject_ids:
        result = add_subject_to_plan(plan_id, user_id, sid)
        if result['success']:
            success_count += 1
    
    elapsed = time.time() - start
    
    print(f"✅ Added {success_count}/{len(subject_ids)} subjects")
    print(f"⏱️  Total time: {elapsed:.3f}s")
    print(f"⏱️  Average per subject: {elapsed/len(subject_ids):.3f}s")
    
    return elapsed

def main():
    print("\n" + "="*60)
    print("🚀 PERFORMANCE OPTIMIZATION TESTS")
    print("="*60)
    
    try:
        # Test 1: Apply roadmap (batch insert)
        time1 = test_apply_roadmap_performance()
        
        # Test 2: Add single subject (optimized)
        time2 = test_add_subject_performance()
        
        # Test 3: Add multiple subjects
        time3 = test_add_multiple_subjects()
        
        print(f"\n{'='*60}")
        print("📊 SUMMARY")
        print(f"{'='*60}")
        print(f"Apply Roadmap (batch):     {time1:.3f}s")
        print(f"Add Single Subject:        {time2:.3f}s")
        print(f"Add 5 Subjects Sequential: {time3:.3f}s")
        print(f"\n💡 Expected improvement on production:")
        print(f"   - Batch insert reduces network round trips from N to 2-3")
        print(f"   - Single subject from 3 queries → 1 query")
        print(f"   - Should see 50-70% speed improvement on Vercel")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        print("\n" + "="*60)
        print("🧹 Cleaning up test data...")
        cleanup_test_data(3)
        print("✓ Done!")

if __name__ == "__main__":
    main()
