#!/bin/bash
# Simple test runner script that avoids pager issues

export PAGER=cat
export MANPAGER=cat
export GIT_PAGER=cat

echo "================================================================================"
echo "MongoDB Repository Tests - Checkpoint 4"
echo "================================================================================"
echo ""

# Run the tests
python3 -m pytest \
  tests/test_user_repository_properties.py \
  tests/test_recipe_repository_properties.py \
  tests/test_join_equivalence_property.py \
  -v --tb=short 2>&1

exit_code=$?

echo ""
echo "================================================================================"
if [ $exit_code -eq 0 ]; then
  echo "✅ All repository tests PASSED!"
else
  echo "⚠️  Some tests FAILED (exit code: $exit_code)"
fi
echo "================================================================================"

exit $exit_code
