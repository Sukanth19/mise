#!/usr/bin/env python
"""
Simple script to run MySQL query property tests.
"""
import subprocess
import sys

def main():
    """Run the property tests with reduced examples for faster execution."""
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/test_mysql_query_properties.py",
        "-v",
        "--hypothesis-max-examples=100",
        "--tb=short"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
