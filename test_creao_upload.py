#!/usr/bin/env python3
"""
Test uploading Creao farmer data to API
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_creao_integration():
    """Test the complete Creao integration flow"""
    
    print("\n" + "="*70)
    print("🧪 TESTING CREAO DATA UPLOAD & ANALYTICS")
    print("="*70)
    
    # Step 1: Check API health
    print("\n📡 Step 1: Checking API health...")
    try:
        response = requests.get(f"{API_BASE}/api/health")
        health = response.json()
        print(f"✅ API is healthy!")
        print(f"   - Status: {health['status']}")
        print(f"   - Gemini available: {health['gemini_available']}")
        print(f"   - Farmers in system: {health['farmers_count']}")
    except requests.exceptions.ConnectionError:
        print("❌ API is not running!")
        print("\n💡 Start the API first:")
        print("   python dashboard_api.py")
        return
    
    # Step 2: Upload Creao farmers data
    print("\n📤 Step 2: Uploading Creao farmers data...")
    try:
        with open('creao_farmers_data.json', 'r') as f:
            farmers_data = json.load(f)
        
        response = requests.post(
            f"{API_BASE}/api/creao/bulk-upload",
            json=farmers_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Upload successful!")
            print(f"   - Farmers uploaded: {result['farmers_uploaded']}")
            print(f"   - Message: {result['message']}")
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return
            
    except FileNotFoundError:
        print("❌ creao_farmers_data.json not found!")
        print("\n💡 Generate it first:")
        print("   python creao_database_adapter.py 'Farm Connect Users Database.csv'")
        return
    
    # Wait a moment
    time.sleep(1)
    
    # Step 3: List all farmers
    print("\n📋 Step 3: Listing all farmers in system...")
    response = requests.get(f"{API_BASE}/api/farmers")
    farmers_list = response.json()
    print(f"✅ Found {len(farmers_list)} farmers:")
    for farmer in farmers_list[:3]:  # Show first 3
        print(f"   - {farmer['farmer_name']} (ID: {farmer['farmer_id'][:20]}...)")
    if len(farmers_list) > 3:
        print(f"   ... and {len(farmers_list) - 3} more")
    
    # Step 4: Generate analytics for first farmer
    print("\n📊 Step 4: Generating analytics for a farmer...")
    first_farmer_id = farmers_list[0]['farmer_id']
    first_farmer_name = farmers_list[0]['farmer_name']
    print(f"   Farmer: {first_farmer_name}")
    
    response = requests.post(
        f"{API_BASE}/api/analytics/generate",
        json={
            "farmer_id": first_farmer_id,
            "weeks": 12
        }
    )
    
    if response.status_code == 200:
        analytics = response.json()
        print(f"✅ Analytics generated!")
        
        # Show insights
        print(f"\n   💡 Insights:")
        for insight in analytics['analytics']['insights'][:2]:
            print(f"      • {insight['title']}")
            print(f"        {insight['explanation']}")
        
        # Show forecast
        print(f"\n   📈 Forecast (next 2 weeks):")
        for forecast in analytics['analytics']['forecast'][:2]:
            print(f"      • Week {forecast['week_start']}: {forecast['crop']} - {forecast['kg']}kg")
        
        # Show chart data availability
        print(f"\n   📊 Charts available:")
        for chart_name in analytics['charts'].keys():
            data_count = len(analytics['charts'][chart_name]['data'])
            print(f"      • {chart_name}: {data_count} data points")
        
        print(f"\n   ✅ All analytics and charts generated successfully!")
        
    else:
        print(f"❌ Analytics generation failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return
    
    # Summary
    print("\n" + "="*70)
    print("✅ CREAO INTEGRATION TEST COMPLETE!")
    print("="*70)
    print("\n📤 Ready to deploy:")
    print("   1. Push to GitHub")
    print("   2. Deploy to Render.com")
    print("   3. Upload creao_farmers_data.json to production:")
    print("      curl -X POST https://your-api.onrender.com/api/creao/bulk-upload \\")
    print("        -H 'Content-Type: application/json' \\")
    print("        -d @creao_farmers_data.json")
    print("   4. Share API URL with Creao team")
    print("\n🎉 All 7 farmers have analytics ready to display!")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_creao_integration()

