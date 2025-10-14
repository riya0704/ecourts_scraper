#!/usr/bin/env python3
"""
test_scraper.py - Simple test script for the eCourts scraper

This script tests various functionalities of the scraper to ensure it works correctly.
"""

import subprocess
import sys
import os
import json
from datetime import datetime

def run_command(cmd):
    """Run a command and return the result"""
    print(f"[TEST] Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        print(f"   Exit code: {result.returncode}")
        if result.stdout:
            print(f"   Output: {result.stdout.strip()}")
        if result.stderr:
            print(f"   Error: {result.stderr.strip()}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("   [ERROR] Command timed out")
        return False
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False

def test_help():
    """Test help functionality"""
    print("\n" + "="*50)
    print("Testing Help Functionality")
    print("="*50)
    return run_command([sys.executable, "scraper.py", "--help"])

def test_cnr_today():
    """Test CNR lookup for today"""
    print("\n" + "="*50)
    print("Testing CNR Lookup (Today)")
    print("="*50)
    return run_command([sys.executable, "scraper.py", "--cnr", "TEST123456789012", "--today"])

def test_case_type_tomorrow():
    """Test case type lookup for tomorrow"""
    print("\n" + "="*50)
    print("Testing Case Type Lookup (Tomorrow)")
    print("="*50)
    return run_command([sys.executable, "scraper.py", "--type", "CR", "--number", "123", "--year", "2024", "--tomorrow"])

def test_causelist():
    """Test cause list download"""
    print("\n" + "="*50)
    print("Testing Cause List Download")
    print("="*50)
    return run_command([sys.executable, "scraper.py", "--causelist", "--today"])

def test_invalid_input():
    """Test invalid input handling"""
    print("\n" + "="*50)
    print("Testing Invalid Input Handling")
    print("="*50)
    # This should fail gracefully
    result = run_command([sys.executable, "scraper.py"])
    return not result  # Should return False (failure) which means our test passes

def test_api():
    """Test API functionality"""
    print("\n" + "="*50)
    print("Testing API Import")
    print("="*50)
    try:
        import api_app
        print("[SUCCESS] API module imported successfully")
        return True
    except Exception as e:
        print(f"[ERROR] API import failed: {e}")
        return False

def check_output_files():
    """Check if output files are being created"""
    print("\n" + "="*50)
    print("Checking Output Files")
    print("="*50)
    
    if not os.path.exists("outputs"):
        print("[ERROR] Outputs directory not found")
        return False
    
    files = os.listdir("outputs")
    if not files:
        print("[ERROR] No output files found")
        return False
    
    print(f"[SUCCESS] Found {len(files)} output files:")
    for file in files:
        if file.endswith('.json'):
            filepath = os.path.join("outputs", file)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                print(f"   {file} - Valid JSON with {len(data)} keys")
            except Exception as e:
                print(f"   [ERROR] {file} - Invalid JSON: {e}")
                return False
    return True

def main():
    """Run all tests"""
    print("Starting eCourts Scraper Tests")
    print(f"Test run: {datetime.now().isoformat()}")
    
    tests = [
        ("Help Functionality", test_help),
        ("CNR Lookup", test_cnr_today),
        ("Case Type Lookup", test_case_type_tomorrow),
        ("Cause List Download", test_causelist),
        ("Invalid Input Handling", test_invalid_input),
        ("API Import", test_api),
        ("Output Files Check", check_output_files)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("All tests passed! The scraper is working correctly.")
        return 0
    else:
        print("Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())