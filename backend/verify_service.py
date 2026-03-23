#!/usr/bin/env python3
"""Verify meal plan service can be imported."""

import sys

try:
    from app.services.meal_plan_service import MealPlanner
    print("SUCCESS: MealPlanner service imported successfully")
    print(f"Valid meal times: {MealPlanner.VALID_MEAL_TIMES}")
    print(f"Methods available: {[m for m in dir(MealPlanner) if not m.startswith('_')]}")
    sys.exit(0)
except Exception as e:
    print(f"ERROR: Failed to import MealPlanner: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
