#!/usr/bin/env python3
"""
Test script for the eCourts UI API endpoints
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_endpoint(endpoint, description):
    """Test a GET endpoint"""
    print(f"\n🧪 Testing: {description}")
    print(f"📡 Endpoint: {endpoint}")
    print("-" * 50)
    
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Status: {response.status_code}")
            print(f"📊 Data count: {len(data) if isinstance(data, list) else 'N/A'}")
            
            if isinstance(data, list) and data:
                print(f"📋 Sample data: {data[0]}")
            elif isinstance(data, dict):
                print(f"📋 Response: {data}")
            
            return data
        else:
            print(f"❌ Failed! Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"🔌 Connection error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_post_endpoint(endpoint, data, description):
    """Test a POST endpoint"""
    print(f"\n🧪 Testing: {description}")
    print(f"📡 Endpoint: {endpoint}")
    print(f"📤 Data: {json.dumps(data, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(
            f"{BASE_URL}{endpoint}", 
            json=data, 
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success! Status: {response.status_code}")
            print(f"📋 Response: {json.dumps(result, indent=2)}")
            return result
        else:
            print(f"❌ Failed! Status: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"🔌 Connection error: {e}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def main():
    print("🚀 eCourts UI API Test Suite")
    print("=" * 60)
    print(f"🕒 Test started at: {datetime.now().isoformat()}")
    print(f"🌐 Base URL: {BASE_URL}")
    print("=" * 60)
    
    # Test 1: Get States
    states = test_endpoint("/api/states", "Fetch all states")
    
    if not states:
        print("\n❌ Cannot proceed without states data")
        return
    
    # Use first state for further testing
    test_state = states[0]
    state_code = test_state['value']
    
    # Test 2: Get Districts
    districts = test_endpoint(f"/api/districts/{state_code}", f"Fetch districts for {test_state['text']}")
    
    if not districts:
        print(f"\n⚠️ No districts found for {test_state['text']}")
        return
    
    # Use first district for further testing
    test_district = districts[0]
    district_code = test_district['value']
    
    # Test 3: Get Court Complexes
    complexes = test_endpoint(
        f"/api/complexes/{state_code}/{district_code}", 
        f"Fetch complexes for {test_district['text']}"
    )
    
    if not complexes:
        print(f"\n⚠️ No complexes found for {test_district['text']}")
        return
    
    # Use first complex for further testing
    test_complex = complexes[0]
    complex_code = test_complex['value']
    
    # Test 4: Get Courts
    courts = test_endpoint(
        f"/api/courts/{state_code}/{district_code}/{complex_code}", 
        f"Fetch courts for {test_complex['text']}"
    )
    
    if courts:
        test_court = courts[0]
        court_code = test_court['value']
        
        # Test 5: Download Single Court (simulation)
        download_data = {
            "state_code": state_code,
            "district_code": district_code,
            "complex_code": complex_code,
            "court_code": court_code,
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        test_post_endpoint("/api/download_single", download_data, "Download single court cause list")
    
    # Test 6: Download Complex (simulation)
    complex_download_data = {
        "state_code": state_code,
        "district_code": district_code,
        "complex_code": complex_code,
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    
    test_post_endpoint("/api/download_complex", complex_download_data, "Download complex cause lists")
    
    print("\n" + "=" * 60)
    print("🏁 Test Suite Complete!")
    print("=" * 60)
    print("📊 Summary:")
    print(f"   • States API: {'✅' if states else '❌'}")
    print(f"   • Districts API: {'✅' if districts else '❌'}")
    print(f"   • Complexes API: {'✅' if complexes else '❌'}")
    print(f"   • Courts API: {'✅' if courts else '❌'}")
    print("\n💡 Note: Download tests may fail if eCourts doesn't have data for the test parameters")
    print("🌐 Open http://localhost:5000 in your browser to use the UI")

if __name__ == "__main__":
    main()