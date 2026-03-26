#!/usr/bin/env python3
"""Run repository property tests and report results."""

import subprocess
import sys

def run_tests():
    """Run all repository property tests."""
    test_files = [
        "tests/test_user_repository_properties.py",
        "tests/test_recipe_repository_properties.py",
        "tests/test_join_equivalence_property.py"
    ]
    
    print("=" * 80)
    print("Running Repository Property Tests")
    print("=" * 80)
    print()
    
    all_passed = True
    results = {}
    
    for test_file in test_files:
        print(f"\nRunning {test_file}...")
        print("-" * 80)
        
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            results[test_file] = {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            if result.returncode != 0:
                all_passed = False
                print(f"❌ {test_file} FAILED")
            else:
                print(f"✅ {test_file} PASSED")
                
        except subprocess.TimeoutExpired:
            print(f"⏱️  {test_file} TIMEOUT")
            all_passed = False
        except Exception as e:
            print(f"❌ {test_file} ERROR: {e}")
            all_passed = False
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    for test_file, result in results.items():
        status = "✅ PASSED" if result["returncode"] == 0 else "❌ FAILED"
        print(f"{status}: {test_file}")
    
    print()
    if all_passed:
        print("🎉 All repository tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Review output above.")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
