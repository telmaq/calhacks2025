#!/usr/bin/env python3
"""
Quick API Test Script
=====================

Tests the analytics API endpoints to ensure everything is working.

Usage:
    python test_api.py
"""

import requests
import json
import base64
import os
from pathlib import Path

API_BASE = "http://localhost:8001"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server not reachable: {e}")
        print("💡 Start server with: python app.py")
        return False

def test_analytics_status():
    """Test analytics status endpoint"""
    print("\n🔍 Testing analytics status...")
    try:
        response = requests.get(f"{API_BASE}/api/v1/analytics/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Analytics status retrieved")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"❌ Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_csv_analytics():
    """Test CSV analytics endpoint"""
    print("\n🔍 Testing CSV analytics...")
    
    # Read sample CSV
    if not os.path.exists("sample_weekly.csv"):
        print("❌ sample_weekly.csv not found")
        return False
    
    with open("sample_weekly.csv", "r") as f:
        csv_data = f.read()
    
    payload = {
        "farmer_id": "test_farmer_123",
        "csv_data": csv_data,
        "crop_filter": None
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/analytics/csv",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ CSV analytics successful")
            print(f"   Source: {data['source']}")
            print(f"   Insights: {len(data['analytics']['insights'])}")
            print(f"   Forecast entries: {len(data['analytics']['forecast'])}")
            print(f"   Recommendations: {len(data['analytics']['recommendations'])}")
            
            # Print first insight
            if data['analytics']['insights']:
                print(f"\n   First insight:")
                print(f"   📌 {data['analytics']['insights'][0]['title']}")
            
            return True
        else:
            print(f"❌ CSV analytics failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_image_analytics():
    """Test image analytics endpoint"""
    print("\n🔍 Testing image analytics...")
    
    # Look for sample images
    image_files = list(Path('.').glob('*.jpg')) + list(Path('.').glob('*.jpeg')) + list(Path('.').glob('*.png'))
    
    if not image_files:
        print("⚠️  No image files found for testing")
        print("   Add a .jpg or .png file to test image analytics")
        return None
    
    image_path = image_files[0]
    print(f"   Using image: {image_path}")
    
    # Read and encode image
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode('utf-8')
    
    payload = {
        "farmer_id": "test_farmer_123",
        "image_base64": image_b64,
        "produce_type": "mixed"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/analytics/image",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Image analytics successful")
            print(f"   Source: {data['source']}")
            print(f"   Crate count: {data['analytics']['crate_count']}")
            print(f"   Total weight: {data['analytics']['estimated_total_weight_kg']} kg")
            print(f"   Quality: {data['analytics']['quality_score']}")
            print(f"   Confidence: {data['analytics']['confidence']:.1%}")
            return True
        else:
            print(f"❌ Image analytics failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("API TEST SUITE".center(60))
    print("="*60)
    
    results = []
    
    # Test health
    results.append(("Health Check", test_health()))
    
    if not results[0][1]:
        print("\n❌ Server is not running. Start it with: python app.py")
        return
    
    # Test analytics status
    results.append(("Analytics Status", test_analytics_status()))
    
    # Test CSV analytics
    results.append(("CSV Analytics", test_csv_analytics()))
    
    # Test image analytics
    image_result = test_image_analytics()
    if image_result is not None:
        results.append(("Image Analytics", image_result))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY".center(60))
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:30} {status}")
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your API is ready for the demo.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

if __name__ == "__main__":
    main()

