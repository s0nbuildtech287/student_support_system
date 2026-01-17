"""Quick test to verify add_subject works now"""
from services.yourplan_service import add_subject_to_plan, create_user_plan, get_user_plans
from database import execute_query

user_id = 3  # admin

print("=== Test Add Subject (Fixed Version) ===\n")

# Clean up
execute_query("DELETE FROM plan_subjects WHERE plan_id IN (SELECT id FROM study_plans WHERE user_id = %s)", (user_id,))
execute_query("DELETE FROM study_plans WHERE user_id = %s", (user_id,))

# Create new plan
print("1. Creating test plan...")
result = create_user_plan(user_id, "Test Plan", "For testing")
print(f"   Result: {result['message']}")

# Get plan_id
plans = get_user_plans(user_id)
if not plans:
    print("❌ No plans created!")
    exit(1)

plan_id = plans[0]['id']
print(f"   Plan ID: {plan_id}")

# Add subject 1 (Nhập môn lập trình)
print("\n2. Adding subject ID 1...")
result = add_subject_to_plan(plan_id, user_id, 1, allow_edit=False)
print(f"   Result: {result}")

# Verify
plans = get_user_plans(user_id)
subjects_count = len(plans[0].get('subjects', []))
print(f"\n3. Verification:")
print(f"   Subjects in plan: {subjects_count}")

if subjects_count == 1:
    print("   ✅ SUCCESS: Subject was added!")
    subject = plans[0]['subjects'][0]
    print(f"   Added subject: {subject.get('subject_name')}")
else:
    print("   ❌ FAILED: Subject was NOT added")

# Try adding duplicate
print("\n4. Testing duplicate prevention...")
result = add_subject_to_plan(plan_id, user_id, 1, allow_edit=False)
print(f"   Result: {result}")
if not result['success']:
    print("   ✅ Duplicate check works!")

# Add another subject
print("\n5. Adding subject ID 2...")
result = add_subject_to_plan(plan_id, user_id, 2, allow_edit=False)
print(f"   Result: {result}")

plans = get_user_plans(user_id)
subjects_count = len(plans[0].get('subjects', []))
print(f"   Total subjects now: {subjects_count}")

if subjects_count == 2:
    print("   ✅ SUCCESS: Can add multiple subjects!")
else:
    print("   ❌ FAILED: Multiple add not working")

# Cleanup
print("\n6. Cleaning up...")
execute_query("DELETE FROM plan_subjects WHERE plan_id = %s", (plan_id,))
execute_query("DELETE FROM study_plans WHERE id = %s", (plan_id,))
print("   ✓ Done")

print("\n=== Test Complete ===")
