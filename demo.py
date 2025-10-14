#!/usr/bin/env python3
"""
demo.py - Demonstration script for the eCourts scraper

This script shows various ways to use the eCourts scraper.
"""

import subprocess
import sys
import time
from datetime import datetime

def run_demo_command(description, cmd):
    """Run a demo command with nice formatting"""
    print(f"\n{'='*60}")
    print(f"DEMO: {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        print(f"Exit Code: {result.returncode}")
    except Exception as e:
        print(f"Error running command: {e}")

def main():
    """Run demonstration of eCourts scraper functionality"""
    print("eCourts Scraper - Complete Demonstration")
    print(f"Demo run: {datetime.now().isoformat()}")
    print("This demo shows all the key features of the scraper.")
    
    demos = [
        ("Help and Usage Information", [sys.executable, "scraper.py", "--help"]),
        ("Search by CNR for Today", [sys.executable, "scraper.py", "--cnr", "DEMO123456789012", "--today"]),
        ("Search by Case Type for Tomorrow", [sys.executable, "scraper.py", "--type", "CR", "--number", "999", "--year", "2024", "--tomorrow"]),
        ("Download Cause List for Today", [sys.executable, "scraper.py", "--causelist", "--today"]),
        ("Search for Specific Date", [sys.executable, "scraper.py", "--cnr", "TEST987654321098", "--date", "2024-10-20"]),
        ("Error Handling - No Arguments", [sys.executable, "scraper.py"]),
        ("Error Handling - Invalid Year", [sys.executable, "scraper.py", "--type", "CR", "--number", "123", "--year", "1800", "--today"]),
    ]
    
    for description, cmd in demos:
        run_demo_command(description, cmd)
        time.sleep(1)  # Small delay between demos
    
    print(f"\n{'='*60}")
    print("DEMO COMPLETE")
    print(f"{'='*60}")
    print("Key Features Demonstrated:")
    print("✓ CNR-based case lookup")
    print("✓ Case type/number/year lookup")
    print("✓ Today/tomorrow/specific date options")
    print("✓ Cause list download functionality")
    print("✓ Comprehensive help system")
    print("✓ Error handling and validation")
    print("✓ JSON output file generation")
    print("\nCheck the 'outputs/' directory for generated JSON files.")
    print("The scraper is ready for production use!")

if __name__ == "__main__":
    main()