#!/usr/bin/env python3
"""
Test Creao API Integration
===========================

Simulates how Creao app would send data and get analytics/charts.

Usage:
    python test_creao_api.py
"""

import requests
import json

API_BASE = "http://localhost:8000"

def test_send_data():
    """Test sending farmer data (Step 1)"""
    print("="*60)
    print("TEST 1: Send Farmer Data to API")
    print("="*60)
    
    # Sample data from Creao
    data = {
        "farmer_id": "farmer123",
        "farmer_name": "John's Farm",
        "data": [
            {
                "week_start": "2025-09-01",
                "crop": "tomato",
                "total_supplied_kg": 500,
                "total_sold_kg": 450,
                "avg_delivery_delay_min": 20
            },
            {
                "week_start": "2025-09-08",
                "crop": "tomato",
                "total_supplied_kg": 520,
                "total_sold_kg": 480,
                "avg_delivery_delay_min": 25
            },
            {
                "week_start": "2025-09-15",
                "crop": "tomato",
                "total_supplied_kg": 480,
                "total_sold_kg": 430,
                "avg_delivery_delay_min": 40
            },
            {
                "week_start": "2025-09-22",
                "crop": "tomato",
                "total_supplied_kg": 600,
                "total_sold_kg": 560,
                "avg_delivery_delay_min": 15
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/data/send",
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Data sent successfully!")
            print(f"   Farmer: {result['message']}")
            print(f"   Records: {result['records_received']}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Make sure API server is running: python dashboard_api.py")
        return False

def test_generate_analytics():
    """Test generating analytics and charts (Step 2)"""
    print("\n" + "="*60)
    print("TEST 2: Generate Analytics & Charts")
    print("="*60)
    
    request = {
        "farmer_id": "farmer123",
        "crop_filter": None,
        "weeks": 12
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/analytics/generate",
            json=request,
            timeout=30
        )
        
        if response.status_code == 200:
            analytics = response.json()
            
            print("✅ Analytics generated successfully!")
            print(f"   Source: {analytics['source']}")
            print(f"   Farmer: {analytics['farmer_name']}")
            
            # Show insights
            print("\n💡 AI Insights:")
            for i, insight in enumerate(analytics['insights'], 1):
                print(f"   {i}. {insight['title']}")
                print(f"      {insight['explanation']}")
            
            # Show forecast
            print("\n📈 2-Week Forecast:")
            for forecast in analytics['forecast'][:3]:
                print(f"   {forecast['week_start']}: {forecast['kg']} kg of {forecast['crop']}")
            
            # Show recommendations
            print("\n🎯 Top Recommendation:")
            print(f"   {analytics['recommendations'][0]}")
            
            # Show charts available
            print("\n📊 Charts Available:")
            for chart_name, chart_data in analytics['charts'].items():
                print(f"   • {chart_name}: {chart_data['title']} ({chart_data['chart_type']})")
                print(f"     Data points: {len(chart_data['data'])}")
            
            return analytics
            
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def show_chart_data(analytics):
    """Show how to use chart data"""
    print("\n" + "="*60)
    print("TEST 3: Chart Data Structure")
    print("="*60)
    
    # Supply trend example
    supply_chart = analytics['charts']['supply_trend']
    print(f"\n📈 {supply_chart['title']} ({supply_chart['chart_type']})")
    print("   Sample data points:")
    for point in supply_chart['data'][:3]:
        print(f"   - Week {point['x']}: {point['y']} kg ({point.get('crop', 'N/A')})")
    
    # Pie chart example
    pie_chart = analytics['charts']['distribution']
    print(f"\n🥧 {pie_chart['title']} ({pie_chart['chart_type']})")
    print("   Distribution:")
    for item in pie_chart['data']:
        print(f"   - {item['label']}: {item['value']} kg")
    
    print("\n💡 These data structures are ready for:")
    print("   • react-native-chart-kit")
    print("   • Chart.js")
    print("   • Any charting library!")

def show_integration_code():
    """Show example integration code for Creao"""
    print("\n" + "="*60)
    print("INTEGRATION CODE FOR CREAO APP")
    print("="*60)
    
    code = '''
// In your Creao React Native app:

async function syncAndShowAnalytics(farmerId, farmerData) {
  // Step 1: Send farmer data
  await fetch('http://your-api.com/api/data/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      farmer_id: farmerId,
      farmer_name: farmerData.name,
      data: farmerData.weeklyRecords
    })
  });
  
  // Step 2: Get analytics with charts
  const response = await fetch('http://your-api.com/api/analytics/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ farmer_id: farmerId })
  });
  
  const analytics = await response.json();
  
  // Step 3: Display in your app
  displayInsights(analytics.insights);
  renderCharts(analytics.charts);
  showRecommendations(analytics.recommendations);
}
'''
    print(code)

def main():
    """Run all tests"""
    print("\n🧪 TESTING CREAO API INTEGRATION\n")
    
    # Test 1: Send data
    success1 = test_send_data()
    if not success1:
        print("\n⚠️  API server not running. Start with:")
        print("   python dashboard_api.py")
        return
    
    # Test 2: Generate analytics
    analytics = test_generate_analytics()
    if not analytics:
        return
    
    # Test 3: Show chart structure
    show_chart_data(analytics)
    
    # Show integration code
    show_integration_code()
    
    # Summary
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\n🎉 Your API is ready for Creao integration!")
    print("\nNext Steps:")
    print("1. Deploy API: render.com or railway.app")
    print("2. Share API URL with Creao team")
    print("3. Creao app follows the integration code above")
    print("4. Farmers see beautiful analytics! 🚀")
    print("\n📖 Full guide: CREAO_API_INTEGRATION.md")

if __name__ == "__main__":
    main()

