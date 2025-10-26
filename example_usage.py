#!/usr/bin/env python3
"""
Example Usage - How to integrate Gemini analytics into your code
=================================================================

This file shows practical examples of how to use the analytics modules
in your own code.
"""

import json
from pathlib import Path

# Example 1: Using CSV Analytics in Your Code
# ============================================

def example_csv_analytics():
    """Example: Analyze CSV data programmatically"""
    print("=" * 60)
    print("EXAMPLE 1: CSV Analytics Integration")
    print("=" * 60)
    
    from analyze_csv import analyze_csv
    
    # Analyze your CSV file
    csv_path = "sample_weekly.csv"
    result = analyze_csv(csv_path, crop="tomato")
    
    # Extract insights
    print("\n📊 Analytics Results:")
    print(f"   - Insights: {len(result['insights'])}")
    print(f"   - Forecast entries: {len(result['forecast'])}")
    print(f"   - Recommendations: {len(result['recommendations'])}")
    
    # Use the insights in your app
    for insight in result['insights']:
        print(f"\n   💡 {insight['title']}")
        print(f"      {insight['explanation']}")
    
    return result

# Example 2: Using Image Analytics in Your Code
# ==============================================

def example_image_analytics():
    """Example: Analyze images programmatically"""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Image Analytics Integration")
    print("=" * 60)
    
    # Find any image file for demo
    image_files = list(Path('.').glob('*.jpg')) + list(Path('.').glob('*.png'))
    
    if not image_files:
        print("\n⚠️  No image files found. Skipping image example.")
        return None
    
    from analyze_image import analyze_image
    
    image_path = str(image_files[0])
    result = analyze_image(image_path)
    
    print(f"\n🖼️  Analysis Results:")
    print(f"   - Crates detected: {result['crate_count']}")
    print(f"   - Total weight: {result['estimated_total_weight_kg']} kg")
    print(f"   - Quality: {result['quality_score']}")
    print(f"   - Confidence: {result['confidence']:.0%}")
    
    # Use in your inventory system
    if result['confidence'] > 0.7:
        print(f"\n   ✅ High confidence - ready to add to inventory")
    else:
        print(f"\n   ⚠️  Low confidence - manual verification recommended")
    
    return result

# Example 3: Making API Requests
# ================================

def example_api_requests():
    """Example: Call the analytics API from your code"""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: API Integration")
    print("=" * 60)
    
    try:
        import requests
    except ImportError:
        print("\n⚠️  'requests' not installed. Skipping API example.")
        print("   Install with: pip install requests")
        return
    
    base_url = "http://localhost:8001"
    
    # Check if server is running
    try:
        response = requests.get(f"{base_url}/api/v1/analytics/status", timeout=2)
        print(f"\n✅ API Server is running")
    except:
        print(f"\n⚠️  API Server not running. Start with: python app.py")
        return
    
    # Example: CSV analytics via API
    print("\n📤 Sending CSV data to API...")
    
    csv_data = """week_start,crop,total_supplied_kg,total_sold_kg
2025-09-01,tomato,500,450
2025-09-08,tomato,520,480"""
    
    payload = {
        "farmer_id": "example_farmer_001",
        "csv_data": csv_data
    }
    
    response = requests.post(
        f"{base_url}/api/v1/analytics/csv",
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Response received (source: {result['source']})")
        print(f"\n   First insight: {result['analytics']['insights'][0]['title']}")
    else:
        print(f"❌ Request failed: {response.status_code}")

# Example 4: Building a Simple Workflow
# ======================================

def example_workflow():
    """Example: Complete workflow from data to insights"""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Complete Workflow")
    print("=" * 60)
    
    print("\n📋 Workflow Steps:")
    print("   1. Farmer uploads weekly sales data")
    print("   2. System analyzes with Gemini AI")
    print("   3. Display insights on dashboard")
    print("   4. Send recommendations via SMS/email")
    
    # Step 1: Get data (simulated)
    print("\n🔄 Step 1: Processing farmer data...")
    from analyze_csv import analyze_csv
    
    result = analyze_csv("sample_weekly.csv")
    
    # Step 2: Format for display
    print("🔄 Step 2: Formatting insights...")
    
    insights_text = "\n".join([
        f"• {i['title']}: {i['explanation']}"
        for i in result['insights']
    ])
    
    # Step 3: Generate summary
    print("🔄 Step 3: Generating farmer summary...")
    
    summary = f"""
    📊 WEEKLY FARM INSIGHTS
    
    {insights_text}
    
    📈 NEXT WEEK FORECAST:
    {result['forecast'][0]['crop'].title()}: {result['forecast'][0]['kg']} kg
    
    💡 TOP RECOMMENDATION:
    {result['recommendations'][0]}
    """
    
    print(summary)
    
    # Step 4: In production, you would:
    print("\n✅ Workflow complete!")
    print("   → In production, send via:")
    print("      - SMS (Twilio)")
    print("      - Email (SendGrid)")
    print("      - Push notification (Firebase)")
    print("      - Dashboard widget")

# Example 5: Error Handling
# ==========================

def example_error_handling():
    """Example: Proper error handling"""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Error Handling Best Practices")
    print("=" * 60)
    
    from analyze_csv import analyze_csv
    
    try:
        # Attempt analysis
        result = analyze_csv("sample_weekly.csv")
        
        # Validate response
        if 'insights' not in result:
            raise ValueError("Invalid response format")
        
        # Check data quality
        if len(result['insights']) == 0:
            print("⚠️  Warning: No insights generated")
        else:
            print(f"✅ Analysis successful: {len(result['insights'])} insights")
        
    except FileNotFoundError:
        print("❌ Error: CSV file not found")
        print("   → Provide feedback to user: 'Please upload a valid CSV file'")
    
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("   → Fallback: Use cached analytics or show default insights")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("   → Log error and show user-friendly message")
        print("   → Consider using mock data as fallback")

# Example 6: Testing Your Integration
# ====================================

def example_testing():
    """Example: How to test the integration"""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Testing Your Integration")
    print("=" * 60)
    
    print("\n📝 Testing Checklist:")
    
    tests = [
        ("CSV file exists", Path("sample_weekly.csv").exists()),
        ("Gemini client imports", True),  # Would check import
        ("API server reachable", False),  # Would check with request
    ]
    
    for test_name, passed in tests:
        status = "✅" if passed else "❌"
        print(f"   {status} {test_name}")
    
    print("\n💡 Testing Tips:")
    print("   • Start with mock data (no API key needed)")
    print("   • Test error cases (missing files, bad data)")
    print("   • Verify JSON structure matches your expectations")
    print("   • Check response times (should be < 5 seconds)")
    print("   • Test with production-like data volumes")

# Main execution
# ==============

def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("GEMINI ANALYTICS - USAGE EXAMPLES")
    print("="*60)
    print("\nThese examples show how to integrate the analytics modules")
    print("into your own application code.\n")
    
    try:
        # Run examples
        example_csv_analytics()
        example_image_analytics()
        example_api_requests()
        example_workflow()
        example_error_handling()
        example_testing()
        
        # Summary
        print("\n" + "="*60)
        print("✅ EXAMPLES COMPLETE")
        print("="*60)
        print("\n📚 Next Steps:")
        print("   1. Review the code in this file")
        print("   2. Adapt examples for your use case")
        print("   3. Check SETUP.md for detailed documentation")
        print("   4. Run test_api.py to verify your setup")
        print()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Examples interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error running examples: {e}")
        print("💡 Make sure dependencies are installed: pip install -r requirements.txt")

if __name__ == "__main__":
    main()

