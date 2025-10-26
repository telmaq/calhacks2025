#!/usr/bin/env python3
"""
Test Creao Integration Endpoints
=================================

Tests the new Creao-specific analytics endpoints.

Usage:
    python test_creao_integration.py
"""

import requests
import json
import base64
from pathlib import Path

API_BASE = "http://localhost:8001"

def test_server_health():
    """Test if server is running"""
    print("🔍 Testing server health...")
    try:
        response = requests.get(f"{API_BASE}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server not reachable: {e}")
        print("💡 Start server with: python app.py")
        return False

def test_creao_analytics():
    """Test Creao farmer analytics endpoint"""
    print("\n🧪 Testing Creao Farmer Analytics...")
    
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/creao/analytics",
            json={
                "farmer_id": "test_farmer_123",
                "weeks": 12,
                "crop_filter": None
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Analytics successful")
            print(f"   Source: {data.get('source', 'unknown')}")
            print(f"   Insights: {len(data['analytics']['insights'])}")
            print(f"   Forecast entries: {len(data['analytics']['forecast'])}")
            print(f"   Saved to Creao: {data.get('saved_to_creao', False)}")
            
            # Print first insight
            if data['analytics']['insights']:
                print(f"\n   First Insight:")
                print(f"   📌 {data['analytics']['insights'][0]['title']}")
                print(f"      {data['analytics']['insights'][0]['explanation']}")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_produce_analysis():
    """Test Creao produce analysis endpoint"""
    print("\n🧪 Testing Creao Produce Analysis...")
    
    # Look for any image file
    image_files = list(Path('.').glob('*.jpg')) + list(Path('.').glob('*.png'))
    
    if not image_files:
        print("⚠️  No image files found for testing")
        print("   Add a .jpg or .png file to test this endpoint")
        return None
    
    image_path = image_files[0]
    print(f"   Using image: {image_path}")
    
    try:
        # Read and encode image
        with open(image_path, "rb") as f:
            image_b64 = base64.b64encode(f.read()).decode('utf-8')
        
        response = requests.post(
            f"{API_BASE}/api/v1/creao/analyze-produce",
            json={
                "farmer_id": "test_farmer_123",
                "image_base64": image_b64,
                "produce_type": "tomatoes"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data.get('listing_suggestions', {})
            
            print("✅ Produce analysis successful")
            print(f"   Source: {data.get('source', 'unknown')}")
            print(f"\n   Listing Suggestions:")
            print(f"   Quality: {suggestions.get('quality_grade', 'N/A')}")
            print(f"   Weight: {suggestions.get('estimated_weight_kg', 0)} kg")
            print(f"   Crates: {suggestions.get('crate_count', 0)}")
            print(f"   Suggested Price: ${suggestions.get('suggested_price_per_kg', 0)}/kg")
            print(f"   Estimated Value: ${suggestions.get('total_estimated_value', 0)}")
            print(f"   Confidence: {suggestions.get('confidence', 0):.1%}")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_existing_weight_capture():
    """Test existing weight capture endpoint still works"""
    print("\n🧪 Testing Weight Capture (existing feature)...")
    
    # This tests that we didn't break existing functionality
    try:
        # Create a small test image (1x1 pixel)
        test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        
        response = requests.post(
            f"{API_BASE}/api/v1/capture/weight",
            json={
                "farmer_id": "test_farmer",
                "produce_name": "apples",
                "image_base64": test_image_b64
            },
            timeout=10
        )
        
        # We expect 400 or 200 (not 500)
        if response.status_code in [200, 400]:
            print("✅ Weight capture endpoint is working")
            return True
        else:
            print(f"⚠️  Unexpected status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all integration tests"""
    print("="*60)
    print("CREAO INTEGRATION TEST SUITE".center(60))
    print("="*60)
    
    results = []
    
    # Test 1: Server health
    if not test_server_health():
        print("\n❌ Server is not running. Start it with: python app.py")
        return
    
    # Test 2: Creao analytics
    results.append(("Creao Analytics", test_creao_analytics()))
    
    # Test 3: Produce analysis
    produce_result = test_produce_analysis()
    if produce_result is not None:
        results.append(("Produce Analysis", produce_result))
    
    # Test 4: Existing weight capture still works
    results.append(("Weight Capture", test_existing_weight_capture()))
    
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
        print("\n🎉 All Creao integration tests passed!")
        print("   Your analytics are ready to integrate with Creao app.")
    else:
        print("\n⚠️  Some tests failed. Check output above for details.")
    
    print("\n📚 Next Steps:")
    print("   1. Review CREAO_ANALYTICS_INTEGRATION.md")
    print("   2. Add the integration code to app.py")
    print("   3. Update your Creao mobile app")
    print("   4. Test end-to-end with real farmer data")

if __name__ == "__main__":
    main()

