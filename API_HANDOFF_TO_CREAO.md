# 📤 API Handoff to Creao Team

Everything Creao needs to integrate the analytics API.

---

## 🎯 What Creao Gets

**API Endpoint:** `https://farm-analytics-api.onrender.com`

**One endpoint to call:** `POST /api/analytics/generate`

That's it! Send farmer ID, get analytics + chart data back.

---

## 🔑 The Only Call Creao Needs

```javascript
// In Creao app - when farmer views analytics
const response = await fetch(
  'https://farm-analytics-api.onrender.com/api/analytics/generate',
  {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      farmer_id: farmerId,  // From Creao database
      crop_filter: null,    // Optional: filter by crop
      weeks: 12             // Optional: time period
    })
  }
);

const analytics = await response.json();

// Now Creao has everything:
// - analytics.analytics.insights
// - analytics.analytics.forecast
// - analytics.analytics.recommendations
// - analytics.charts (all chart data)
```

---

## 📊 What They Get Back

```json
{
  "status": "success",
  "farmer_id": "100019a1edcbeed766ea9c19842fdcfa5f1",
  "analytics": {
    "insights": [
      {
        "title": "Strong Tomato Demand",
        "explanation": "Tomato sales consistently above 90% of supply, indicating strong market demand."
      },
      {
        "title": "Delivery Performance Improving",
        "explanation": "Average delivery time decreased by 15 minutes over the past month."
      }
    ],
    "forecast": [
      {
        "week_start": "2025-10-29",
        "crop": "tomato",
        "kg": 610
      },
      {
        "week_start": "2025-11-05",
        "crop": "tomato",
        "kg": 620
      }
    ],
    "recommendations": [
      "Focus on tomato production - demand is consistently high with 93% sell-through rate",
      "Consider increasing tomato supply by 10% to meet growing demand",
      "Maintain current delivery efficiency to sustain low delay times"
    ]
  },
  "charts": {
    "supply_trend": {
      "chart_type": "line",
      "title": "Supply Trend Over Time",
      "data": [
        {"x": "2025-09-01", "y": 500, "crop": "tomato"},
        {"x": "2025-09-08", "y": 520, "crop": "tomato"},
        {"x": "2025-09-15", "y": 485, "crop": "tomato"}
        // ... more data points
      ]
    },
    "sales_performance": {
      "chart_type": "bar",
      "title": "Sales Performance by Crop",
      "data": [
        {"label": "tomato", "value": 4560},
        {"label": "mango", "value": 1800},
        {"label": "lettuce", "value": 2340}
      ]
    },
    "forecast": {
      "chart_type": "line",
      "title": "Historical + Forecast",
      "data": [
        // Combined historical and forecast data
      ]
    },
    "distribution": {
      "chart_type": "pie",
      "title": "Crop Distribution",
      "data": [
        {"label": "tomato", "value": 2020},
        {"label": "mango", "value": 756},
        {"label": "lettuce", "value": 1128}
      ]
    }
  },
  "source": "gemini"  // or "mock" if Gemini unavailable
}
```

---

## 🎨 How Creao Uses This

### Option 1: Show Insights + Charts

```javascript
// Display AI insights
analytics.analytics.insights.forEach(insight => {
  showInsightCard(insight.title, insight.explanation);
});

// Display charts (Creao's charting library)
showLineChart(analytics.charts.supply_trend.data);
showBarChart(analytics.charts.sales_performance.data);
showPieChart(analytics.charts.distribution.data);

// Show forecast
analytics.analytics.forecast.forEach(f => {
  showForecast(f.week_start, f.crop, f.kg);
});

// Show recommendations
analytics.analytics.recommendations.forEach(rec => {
  showRecommendation(rec);
});
```

### Option 2: Just Show the Charts

```javascript
// If Creao only wants charts, ignore the insights
const chartData = analytics.charts;

// Use your own charting library
renderCharts(chartData);
```

### Option 3: Custom Mix

```javascript
// Pick and choose what to display
const supplyData = analytics.charts.supply_trend.data;
const insights = analytics.analytics.insights;
const forecast = analytics.analytics.forecast;

// Display however Creao wants
```

---

## 🔄 When to Call the API

**Option 1: When Farmer Opens Analytics**
- User clicks "Analytics" in Creao
- Creao calls API
- Shows loading spinner (30-60 sec first time, instant after)
- Displays results

**Option 2: Pre-fetch on Login**
- When farmer logs in
- Pre-fetch analytics in background
- Cache for quick display later

**Option 3: Periodic Refresh**
- Load once
- Refresh every 5 minutes if farmer is viewing analytics

---

## 🚨 Important: Cold Start

**First Request After Sleep:**
- Takes 30-60 seconds (free tier limitation)
- Show a loading message: "Generating AI analytics..."

**Subsequent Requests:**
- Instant (< 1 second)

**Recommendation:**
- Show loading spinner
- Maybe an animation: "🤖 AI is analyzing your farm data..."

---

## 📝 Farmer IDs Already Loaded

These farmers are already in the system:

```
100019a1edcbeed766ea9c19842fdcfa5f1 - Luis
100019a1efaa5937cc1b8ce823ec6e4ec4f - Luis
100019a1f37e91374c3869ee6d172d6d4cd - test
100019a1f4045b77553bf2d53ed934d8697 - (no name)
100019a203fae6372b0bb99f72d5cde1d24 - test
100019a204b913572f5b3499a34999c119c - t2
100019a20c7e91b717bb4861e02171f5fbe - M
```

Test with any of these IDs!

---

## 🧪 Test Endpoint

```bash
# Test with curl
curl -X POST https://farm-analytics-api.onrender.com/api/analytics/generate \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "100019a1edcbeed766ea9c19842fdcfa5f1",
    "weeks": 12
  }'

# Or in browser
# Visit: https://farm-analytics-api.onrender.com/docs
# Try the endpoint interactively
```

---

## 🔧 If Creao Needs to Send New Data

If Creao wants to send updated farmer data:

```javascript
// Optional: Update farmer data first
await fetch('https://farm-analytics-api.onrender.com/api/data/send', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    farmer_id: farmerId,
    farmer_name: farmerName,
    data: [
      {
        week_start: "2025-10-01",
        crop: "tomato",
        total_supplied_kg: 500,
        total_sold_kg: 450,
        avg_delivery_delay_min: 20
      }
      // ... more weekly records
    ]
  })
});

// Then generate analytics
const analytics = await fetch(...);
```

But this is optional - data is already loaded!

---

## 📚 Interactive Documentation

**For Creao developers:**

Visit: `https://farm-analytics-api.onrender.com/docs`

- Try all endpoints
- See request/response examples
- Test with real data
- Copy curl commands

---

## ⚡ Quick Integration Example

**Minimal Creao code:**

```javascript
// AnalyticsScreen.js
import React, { useEffect, useState } from 'react';

export default function AnalyticsScreen({ farmerId }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetch('https://farm-analytics-api.onrender.com/api/analytics/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ farmer_id: farmerId })
    })
    .then(r => r.json())
    .then(data => {
      setAnalytics(data);
      setLoading(false);
    });
  }, [farmerId]);
  
  if (loading) return <LoadingSpinner />;
  
  return (
    <View>
      {/* Creao's custom visualization */}
      <CreaoCharts data={analytics.charts} />
      <CreaoInsights insights={analytics.analytics.insights} />
      <CreaoForecast forecast={analytics.analytics.forecast} />
    </View>
  );
}
```

**That's it!** Creao handles visualization however they want.

---

## 🎯 Summary

**What Creao needs to know:**

1. **API URL:** `https://farm-analytics-api.onrender.com`
2. **Endpoint:** `POST /api/analytics/generate`
3. **Input:** `{"farmer_id": "..."}`
4. **Output:** Analytics + Chart data
5. **Visualization:** Creao handles it
6. **First call:** 30-60 sec (loading spinner recommended)
7. **After that:** Instant

**That's the whole integration!** 🎉

---

## 📧 Questions?

Creao team can:
- Visit `/docs` for interactive testing
- Check this document for examples
- Test with provided farmer IDs
- Contact you with questions

---

**API is production-ready and waiting for Creao!** 🚀

