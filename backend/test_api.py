"""
Test script for AI Road Risk Prediction API
Run this after starting your FastAPI server to verify all endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_endpoint(name, url, method="GET", data=None):
    print(f"\n📍 Testing: {name}")
    print(f"   URL: {url}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        else:
            response = requests.post(url, json=data)
        
        if response.status_code == 200:
            print(f"   ✅ Status: {response.status_code} - SUCCESS")
            result = response.json()
            
            # Print preview of response
            if isinstance(result, dict):
                print(f"   📊 Keys: {list(result.keys())}")
                if 'total_accidents' in result:
                    print(f"   📈 Total Accidents: {result['total_accidents']}")
                if 'severity_distribution' in result:
                    print(f"   📈 Severity Distribution: {result['severity_distribution']}")
            elif isinstance(result, list):
                print(f"   📊 Results count: {len(result)}")
                if len(result) > 0:
                    print(f"   📋 First item keys: {list(result[0].keys())}")
            
            return True
        else:
            print(f"   ❌ Status: {response.status_code} - FAILED")
            print(f"   Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
        return False

def main():
    print("\n" + "🚀"*30)
    print("  AI ROAD RISK PREDICTION API - TESTING SUITE")
    print("🚀"*30)
    
    results = []
    
    # Test Health Check
    print_section("HEALTH CHECK")
    results.append(test_endpoint("Root endpoint", f"{BASE_URL}/"))
    
    # Test Dashboard Endpoints
    print_section("DASHBOARD ENDPOINTS")
    results.append(test_endpoint("Dashboard Statistics", f"{BASE_URL}/dashboard/statistics"))
    results.append(test_endpoint("Risk Factors", f"{BASE_URL}/dashboard/risk-factors"))
    results.append(test_endpoint("Risky Locations", f"{BASE_URL}/dashboard/risky-locations?limit=5"))
    results.append(test_endpoint("Severity Analysis", f"{BASE_URL}/dashboard/severity-analysis"))
    results.append(test_endpoint("Geo Distribution", f"{BASE_URL}/dashboard/geo-distribution"))
    results.append(test_endpoint("Time Trends", f"{BASE_URL}/dashboard/time-trends"))
    
    # Test Heatmap Endpoints
    print_section("HEATMAP ENDPOINTS")
    results.append(test_endpoint("Risk Heatmap", f"{BASE_URL}/risk_heatmap?sample_size=100"))
    results.append(test_endpoint("Risk Heatmap (Fatal only)", f"{BASE_URL}/risk_heatmap?sample_size=50&severity=0"))
    results.append(test_endpoint("Clustered Heatmap", f"{BASE_URL}/risk_heatmap_clustered"))
    
    # Test Prediction Endpoints
    print_section("PREDICTION ENDPOINTS")
    
    # Test location-based prediction
    test_data_location = {
        "lat": 78.5204,
        "lon": 14.7240
    }
    results.append(test_endpoint(
        "Location Prediction", 
        f"{BASE_URL}/predict_location?lat={test_data_location['lat']}&lon={test_data_location['lon']}",
        method="POST"
    ))
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100
    
    print(f"\n   ✅ Passed: {passed}/{total} ({percentage:.1f}%)")
    print(f"   ❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n   🎉 ALL TESTS PASSED! API is ready for frontend integration.")
    else:
        print("\n   ⚠️  Some tests failed. Check the output above for details.")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()