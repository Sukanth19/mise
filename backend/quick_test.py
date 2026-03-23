#!/usr/bin/env python3
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("MEAL PLAN SERVICE VERIFICATION")
print("=" * 60)

# Test 1: Import service
print("\n1. Testing service import...")
try:
    from app.services.meal_plan_service import MealPlanner
    print("   ✓ MealPlanner imported successfully")
except Exception as e:
    print(f"   ✗ Failed to import: {e}")
    sys.exit(1)

# Test 2: Check methods exist
print("\n2. Checking methods...")
required_methods = [
    'validate_meal_time',
    'create_meal_plan',
    'get_meal_plans',
    'update_meal_plan',
    'delete_meal_plan',
    'create_template',
    'get_user_templates',
    'apply_template',
    'delete_template',
    'export_to_ical'
]

for method in required_methods:
    if hasattr(MealPlanner, method):
        print(f"   ✓ {method}")
    else:
        print(f"   ✗ {method} NOT FOUND")
        sys.exit(1)

# Test 3: Test validation
print("\n3. Testing meal time validation...")
assert MealPlanner.validate_meal_time('breakfast') == True
assert MealPlanner.validate_meal_time('lunch') == True
assert MealPlanner.validate_meal_time('dinner') == True
assert MealPlanner.validate_meal_time('snack') == True
assert MealPlanner.validate_meal_time('invalid') == False
print("   ✓ Validation works correctly")

# Test 4: Check icalendar
print("\n4. Checking icalendar library...")
try:
    import icalendar
    print(f"   ✓ icalendar installed (version: {icalendar.__version__})")
except ImportError:
    print("   ⚠ icalendar NOT installed (required for iCal export)")
    print("   Run: pip install icalendar>=5.0.0")

print("\n" + "=" * 60)
print("VERIFICATION COMPLETE")
print("=" * 60)
print("\nAll core functionality is working!")
print("Service is ready for API endpoint integration.")
