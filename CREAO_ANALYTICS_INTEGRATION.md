# 🔗 Creao + Gemini Analytics Integration Guide

This guide shows you how to integrate the new Gemini AI analytics features into your Creao farm marketplace app.

---

## 📋 Overview

**What You're Integrating:**
- ✅ CSV Analytics (insights, forecasts, recommendations) 
- ✅ Image Analysis (produce counting, quality assessment)
- ✅ Your existing weight capture system

**End Result:**
Farmers using Creao can:
1. Get AI insights from their historical sales data
2. Analyze produce photos for counting and quality
3. Capture weights from scale images (existing feature)

---

## 🎯 Integration Architecture

```
Creao App (Mobile/Web)
    ↓
    ↓ API Calls
    ↓
Your FastAPI Backend (app.py)
    ↓
    ├─→ Weight Capture (existing) → OCR → Creao DB
    ├─→ CSV Analytics (NEW!) → Gemini → Insights
    └─→ Image Analysis (NEW!) → Gemini Vision → Quality Score
```

---

## 🚀 Quick Start Integration

### Step 1: Add Helper Functions to app.py

Add these functions to connect analytics with Creao's data model:

```python
# Add to app.py after existing imports
from datetime import datetime, timedelta
import httpx

# Creao API Configuration
CREAO_API_BASE = os.getenv("CREAO_API_URL", "https://your-creao-api.com")
CREAO_API_KEY = os.getenv("CREAO_API_KEY", "your-api-key")

# ============================================================================
# CREAO INTEGRATION HELPERS
# ============================================================================

async def fetch_farmer_data(farmer_id: str, weeks: int = 12) -> dict:
    """
    Fetch farmer's historical sales data from Creao.
    Returns data in format ready for analytics.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{CREAO_API_BASE}/api/farmers/{farmer_id}/sales",
                headers={"Authorization": f"Bearer {CREAO_API_KEY}"},
                params={"weeks": weeks},
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        print(f"Error fetching Creao data: {e}")
        return None

async def save_analytics_to_creao(farmer_id: str, analytics: dict) -> bool:
    """
    Save analytics results to Creao database for farmer dashboard.
    """
    try:
        payload = {
            "farmer_id": farmer_id,
            "insights": analytics.get("insights", []),
            "forecast": analytics.get("forecast", []),
            "recommendations": analytics.get("recommendations", []),
            "generated_at": datetime.now().isoformat()
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{CREAO_API_BASE}/api/analytics/store",
                headers={"Authorization": f"Bearer {CREAO_API_KEY}"},
                json=payload,
                timeout=10.0
            )
            response.raise_for_status()
            return True
    except Exception as e:
        print(f"Error saving to Creao: {e}")
        return False

def creao_to_csv_format(creao_data: dict) -> str:
    """
    Convert Creao sales data to CSV format for analytics.
    
    Creao format:
    [
      {"date": "2025-09-01", "crop": "tomato", "supplied": 500, "sold": 450, "delay": 20},
      ...
    ]
    
    Returns CSV string ready for analyze_csv.py
    """
    if not creao_data or not creao_data.get("sales"):
        return None
    
    # Build CSV
    lines = ["week_start,crop,total_supplied_kg,total_sold_kg,avg_delivery_delay_min"]
    
    for sale in creao_data["sales"]:
        line = f"{sale['date']},{sale['crop']},{sale['supplied']},{sale['sold']},{sale.get('delay', 0)}"
        lines.append(line)
    
    return "\n".join(lines)
```

---

### Step 2: Add Creao-Specific Analytics Endpoint

Add this new endpoint to `app.py`:

```python
# ============================================================================
# CREAO-INTEGRATED ANALYTICS ENDPOINT
# ============================================================================

class CreaoAnalyticsRequest(BaseModel):
    farmer_id: str
    weeks: Optional[int] = 12  # Historical data to analyze
    crop_filter: Optional[str] = None

@app.post("/api/v1/creao/analytics",
          summary="Get Analytics for Creao Farmer",
          description="Fetch farmer data from Creao, analyze with Gemini, and return insights",
          tags=["Creao Integration"])
async def get_farmer_analytics(request: CreaoAnalyticsRequest):
    """
    Complete analytics workflow for Creao farmers:
    1. Fetch historical data from Creao
    2. Analyze with Gemini AI
    3. Save results back to Creao
    4. Return insights to app
    
    **Example Request:**
    ```json
    {
        "farmer_id": "farmer123",
        "weeks": 12,
        "crop_filter": "tomato"
    }
    ```
    """
    try:
        print(f"📊 Creao Analytics request for farmer: {request.farmer_id}")
        
        # Step 1: Fetch data from Creao
        print("🔄 Fetching farmer data from Creao...")
        creao_data = await fetch_farmer_data(request.farmer_id, request.weeks)
        
        if not creao_data:
            # Fallback: use sample data for demo
            print("⚠️  No Creao data, using sample for demo")
            with open("sample_weekly.csv", "r") as f:
                csv_string = f.read()
        else:
            # Convert Creao data to CSV format
            csv_string = creao_to_csv_format(creao_data)
        
        # Step 2: Write to temp file for analysis
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_string)
            temp_path = f.name
        
        try:
            # Step 3: Analyze with Gemini
            if GEMINI_AVAILABLE:
                analytics_result = analyze_csv(temp_path, crop=request.crop_filter)
                source = "gemini"
            else:
                analytics_result = _mock_csv_analytics()
                source = "mock"
            
            # Step 4: Save results to Creao
            saved = await save_analytics_to_creao(request.farmer_id, analytics_result)
            
            # Step 5: Return to app
            return {
                "status": "success",
                "farmer_id": request.farmer_id,
                "analytics": analytics_result,
                "source": source,
                "saved_to_creao": saved,
                "message": "Analytics generated successfully"
            }
            
        finally:
            # Cleanup
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        print(f"❌ Error in Creao analytics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/creao/analyze-produce",
          summary="Analyze Produce Photo for Creao Listing",
          description="Analyze produce image and suggest listing details",
          tags=["Creao Integration"])
async def analyze_produce_for_listing(request: AnalyticsImageRequest):
    """
    Analyze produce photo and suggest:
    - Quality grade
    - Estimated weight
    - Crate count
    - Recommended price (based on quality)
    
    Use this when farmer creates a new listing in Creao.
    """
    try:
        print(f"🖼️  Creao produce analysis for farmer: {request.farmer_id}")
        
        # Write image to temp file
        image_data = base64.b64decode(request.image_base64)
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            f.write(image_data)
            temp_path = f.name
        
        try:
            # Analyze with Gemini
            if GEMINI_AVAILABLE:
                analysis = analyze_image(temp_path)
                source = "gemini"
            else:
                analysis = _mock_image_analytics()
                source = "mock"
            
            # Add Creao-specific suggestions
            quality_score = analysis['quality_score']
            base_price = 3.50  # Base price per kg
            
            # Price multiplier based on quality
            quality_multipliers = {
                "excellent": 1.3,
                "good": 1.1,
                "average": 1.0,
                "fair": 0.9,
                "poor": 0.7
            }
            
            suggested_price = base_price * quality_multipliers.get(quality_score, 1.0)
            
            return {
                "status": "success",
                "farmer_id": request.farmer_id,
                "analysis": analysis,
                "source": source,
                "listing_suggestions": {
                    "quality_grade": quality_score,
                    "estimated_weight_kg": analysis['estimated_total_weight_kg'],
                    "crate_count": analysis['crate_count'],
                    "suggested_price_per_kg": round(suggested_price, 2),
                    "total_estimated_value": round(suggested_price * analysis['estimated_total_weight_kg'], 2),
                    "confidence": analysis['confidence']
                }
            }
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        print(f"❌ Error in produce analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 📱 Mobile App Integration

### Option 1: Analytics Dashboard

Add an "Insights" tab in your Creao farmer dashboard:

```javascript
// In your Creao mobile app

async function loadFarmerInsights(farmerId) {
  const response = await fetch('https://your-api.com/api/v1/creao/analytics', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      farmer_id: farmerId,
      weeks: 12
    })
  });
  
  const data = await response.json();
  
  // Display insights
  displayInsights(data.analytics.insights);
  displayForecast(data.analytics.forecast);
  displayRecommendations(data.analytics.recommendations);
}

function displayInsights(insights) {
  // Show in cards/list
  insights.forEach(insight => {
    addInsightCard({
      title: insight.title,
      description: insight.explanation,
      icon: '💡'
    });
  });
}
```

### Option 2: Smart Listing Creation

Enhance the "Create Listing" flow:

```javascript
// When farmer takes photo of produce

async function createListingWithAI() {
  // 1. Capture photo
  const photo = await capturePhoto();
  const base64 = await imageToBase64(photo);
  
  // 2. Analyze with AI
  showLoading("Analyzing produce...");
  
  const response = await fetch('https://your-api.com/api/v1/creao/analyze-produce', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      farmer_id: currentFarmerId,
      image_base64: base64,
      produce_type: selectedProduce
    })
  });
  
  const data = await response.json();
  const suggestions = data.listing_suggestions;
  
  // 3. Pre-fill listing form
  setFormValues({
    weight: suggestions.estimated_weight_kg,
    quality: suggestions.quality_grade,
    price_per_kg: suggestions.suggested_price_per_kg,
    crate_count: suggestions.crate_count
  });
  
  // 4. Show confidence indicator
  if (suggestions.confidence > 0.8) {
    showMessage("✅ High confidence detection!");
  } else {
    showMessage("⚠️ Please verify the values");
  }
}
```

### Option 3: Weekly Insights Notification

Send weekly analytics to farmers:

```javascript
// Server-side cron job (run weekly)

async function sendWeeklyInsights() {
  const farmers = await getAllActiveFarmers();
  
  for (const farmer of farmers) {
    // Generate analytics
    const response = await fetch('https://your-api.com/api/v1/creao/analytics', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        farmer_id: farmer.id,
        weeks: 12
      })
    });
    
    const data = await response.json();
    
    // Send notification
    await sendPushNotification(farmer.id, {
      title: "📊 Your Weekly Farm Insights",
      body: data.analytics.insights[0].title,
      data: { screen: 'insights', analytics: data.analytics }
    });
  }
}
```

---

## 🔌 React Native Example

Complete integration example for React Native:

```javascript
// screens/FarmerInsightsScreen.js

import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, ActivityIndicator, TouchableOpacity } from 'react-native';

export default function FarmerInsightsScreen({ farmerId }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAnalytics();
  }, [farmerId]);

  async function loadAnalytics() {
    try {
      setLoading(true);
      
      const response = await fetch('https://your-api.com/api/v1/creao/analytics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          farmer_id: farmerId,
          weeks: 12
        })
      });
      
      const data = await response.json();
      setAnalytics(data.analytics);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return <ActivityIndicator size="large" color="#4CAF50" />;
  }

  if (error) {
    return (
      <View>
        <Text>Error: {error}</Text>
        <TouchableOpacity onPress={loadAnalytics}>
          <Text>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView style={{ padding: 16 }}>
      {/* Insights Section */}
      <Text style={{ fontSize: 20, fontWeight: 'bold', marginBottom: 12 }}>
        💡 Key Insights
      </Text>
      {analytics.insights.map((insight, index) => (
        <View key={index} style={{ 
          backgroundColor: '#f5f5f5', 
          padding: 16, 
          marginBottom: 12, 
          borderRadius: 8 
        }}>
          <Text style={{ fontWeight: 'bold', marginBottom: 4 }}>
            {insight.title}
          </Text>
          <Text style={{ color: '#666' }}>
            {insight.explanation}
          </Text>
        </View>
      ))}

      {/* Forecast Section */}
      <Text style={{ fontSize: 20, fontWeight: 'bold', marginTop: 24, marginBottom: 12 }}>
        📈 2-Week Forecast
      </Text>
      {analytics.forecast.map((item, index) => (
        <View key={index} style={{ 
          flexDirection: 'row', 
          justifyContent: 'space-between',
          padding: 12,
          borderBottomWidth: 1,
          borderBottomColor: '#eee'
        }}>
          <Text>{item.crop}</Text>
          <Text>{item.week_start}</Text>
          <Text style={{ fontWeight: 'bold' }}>{item.kg} kg</Text>
        </View>
      ))}

      {/* Recommendations Section */}
      <Text style={{ fontSize: 20, fontWeight: 'bold', marginTop: 24, marginBottom: 12 }}>
        🎯 Recommendations
      </Text>
      {analytics.recommendations.map((rec, index) => (
        <View key={index} style={{ 
          padding: 12,
          marginBottom: 8,
          backgroundColor: '#E8F5E9',
          borderRadius: 8
        }}>
          <Text>{index + 1}. {rec}</Text>
        </View>
      ))}

      {/* Refresh Button */}
      <TouchableOpacity 
        onPress={loadAnalytics}
        style={{
          backgroundColor: '#4CAF50',
          padding: 16,
          borderRadius: 8,
          marginTop: 24,
          alignItems: 'center'
        }}
      >
        <Text style={{ color: 'white', fontWeight: 'bold' }}>
          Refresh Insights
        </Text>
      </TouchableOpacity>
    </ScrollView>
  );
}
```

---

## 🧪 Testing the Integration

### Test 1: Analytics Endpoint

```bash
# Start your server
python app.py

# Test the Creao analytics endpoint
curl -X POST http://localhost:8001/api/v1/creao/analytics \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "farmer123",
    "weeks": 12
  }'
```

### Test 2: Produce Analysis

```bash
# Encode an image
base64 -i produce_photo.jpg -o photo.b64

# Test produce analysis
curl -X POST http://localhost:8001/api/v1/creao/analyze-produce \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "farmer123",
    "image_base64": "'$(cat photo.b64)'"
  }'
```

### Test 3: Complete Integration Test Script

Create `test_creao_integration.py`:

```python
#!/usr/bin/env python3
"""Test Creao integration endpoints"""

import requests
import json

API_BASE = "http://localhost:8001"

def test_farmer_analytics():
    """Test Creao analytics endpoint"""
    print("🧪 Testing Creao Analytics...")
    
    response = requests.post(
        f"{API_BASE}/api/v1/creao/analytics",
        json={
            "farmer_id": "test_farmer_123",
            "weeks": 12
        },
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Analytics successful")
        print(f"   Insights: {len(data['analytics']['insights'])}")
        print(f"   First insight: {data['analytics']['insights'][0]['title']}")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        return False

if __name__ == "__main__":
    test_farmer_analytics()
```

---

## 📊 Creao Dashboard UI Mockup

Add this to your Creao farmer dashboard:

```
┌────────────────────────────────────────────┐
│  🌾 Farmer Dashboard                       │
├────────────────────────────────────────────┤
│                                            │
│  📊 AI Insights                            │
│  ┌──────────────────────────────────────┐ │
│  │ 💡 Strong Tomato Demand              │ │
│  │ Your tomato sales are 93% of supply  │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  📈 Forecast (Next 2 Weeks)               │
│  ┌──────────────────────────────────────┐ │
│  │ Tomato:  610 kg  │  Oct 1            │ │
│  │ Mango:   260 kg  │  Oct 1            │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  🎯 Top Recommendation                     │
│  ┌──────────────────────────────────────┐ │
│  │ Focus on tomato production - high    │ │
│  │ demand and excellent sell-through    │ │
│  └──────────────────────────────────────┘ │
│                                            │
│  [Refresh Insights]  [View Details]       │
│                                            │
└────────────────────────────────────────────┘
```

---

## 🚀 Deployment Checklist

### Environment Variables

Add to your `.env`:

```bash
# Existing
API_KEY=your-secret-api-key
GEMINI_API_KEY=your-gemini-key

# New for Creao integration
CREAO_API_URL=https://your-creao-api.com
CREAO_API_KEY=your-creao-api-key
```

### Update requirements.txt

Already done! ✅ The dependencies are in your updated `requirements.txt`

### Deploy

```bash
# Install/update dependencies
pip install -r requirements.txt

# Test locally first
python app.py

# Deploy to your hosting (Railway, Render, etc.)
# Your existing deployment process
```

---

## 💡 Usage Examples for Farmers

### Example 1: Morning Insights Check

**Farmer's Flow:**
1. Opens Creao app
2. Taps "Insights" tab
3. Sees: "🎯 Focus on tomato production - demand is high!"
4. Adjusts daily harvest plan

### Example 2: Smart Listing Creation

**Farmer's Flow:**
1. Harvests 3 crates of tomatoes
2. Takes photo in Creao app
3. AI suggests: "Weight: 45kg, Quality: Good, Price: $3.85/kg"
4. Reviews and confirms listing
5. Goes live on marketplace

### Example 3: Weekly Review

**Farmer's Flow:**
1. Receives notification: "📊 Your weekly insights are ready!"
2. Opens analytics
3. Sees forecast: "Next week: supply 610kg tomatoes"
4. Plans harvest schedule accordingly

---

## 🎯 Success Metrics

Track these to measure success:

- **Farmer Engagement:** % of farmers viewing insights weekly
- **Listing Quality:** Accuracy of AI-suggested weights/prices
- **Time Saved:** Reduction in listing creation time
- **Revenue Impact:** Price optimization from quality detection
- **Forecast Accuracy:** How close predictions are to actual sales

---

## 🆘 Troubleshooting

### "No Creao data available"

**Solution:** System uses sample data automatically. Update `CREAO_API_URL` and `CREAO_API_KEY` when ready.

### "Analytics taking too long"

**Solution:** Gemini API calls can take 3-10 seconds. Add loading indicators in your UI.

### "Image analysis not accurate"

**Solution:** 
- Ensure good lighting
- Photo should be clear and focused
- Show confidence score to farmers
- Allow manual override

---

## 📚 Next Steps

1. ✅ Copy integration code to `app.py`
2. ✅ Test endpoints with `curl` or Postman
3. ✅ Add UI screens in Creao mobile app
4. ✅ Test end-to-end flow
5. ✅ Deploy and monitor

---

## 🎉 You're Ready!

The analytics are now integrated with your Creao platform. Farmers can get AI-powered insights to make better decisions!

**Questions?** Check:
- `SETUP.md` - General setup
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `example_usage.py` - Code examples

