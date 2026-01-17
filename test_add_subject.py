"""Test add_subject_to_plan to debug issue"""
from services.yourplan_service import add_subject_to_plan
from database import fetch_all, fetch_one

# Test case
user_id = 3  # admin user
plan_id = 8  # existing plan

print("=== DEBUG: Add Subject Issue ===\n")

# Check plan exists
plan = fetch_one("SELECT * FROM study_plans WHERE id = %s", (plan_id,))
print(f"Plan {plan_id}:")
print(f"  - Exists: {plan is not None}")
if plan:
    print(f"  - Name: {plan.get('name')}")
    print(f"  - is_started: {plan.get('is_started')}")

# Check subjects in database
subjects = fetch_all("SELECT id, subject_name FROM subjects LIMIT 5")
print(f"\nSubjects in database (first 5):")
for s in subjects:
    print(f"  - ID {s['id']}: {s['subject_name']}")

# Check what's currently in plan
current = fetch_all("SELECT subject_id FROM plan_subjects WHERE plan_id = %s", (plan_id,))
print(f"\nCurrent subjects in plan {plan_id}:")
if current:
    for c in current:
        print(f"  - Subject ID: {c['subject_id']}")
else:
    print("  - (empty)")

# Try to add subject
print(f"\n--- Testing add_subject_to_plan ---")
print(f"Trying to add subject_uid=1 (should be Python)")

result = add_subject_to_plan(plan_id, user_id, 1, allow_edit=False)
print(f"Result: {result}")

# Check if it was actually added
after = fetch_all("SELECT subject_id FROM plan_subjects WHERE plan_id = %s", (plan_id,))
print(f"\nSubjects in plan after add:")
if after:
    for a in after:
        print(f"  - Subject ID: {a['subject_id']}")
else:
    print("  - (empty)")

print("\n=== Analysis ===")
if len(after) > len(current):
    print("✅ Subject was added successfully")
else:
    print("❌ Subject was NOT added")
    print("Possible reasons:")
    print("  1. Subject ID 1 doesn't exist in subjects table")
    print("  2. Subject already in plan (duplicate check)")
    print("  3. Plan is_started=TRUE and allow_edit=FALSE")
    print("  4. Query logic error in WITH clause")
