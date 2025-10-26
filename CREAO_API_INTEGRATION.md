# 🔗 Creao → Analytics API Integration

Complete guide for Creao to send data and display analytics/charts.

---

## 🎯 How It Works

```
Creao App → Sends farmer data → Your API → Generates analytics → Returns charts
```

**Two-Step Process:**
1. **Send Data**: Creao sends farmer's weekly sales data
2. **Get Analytics**: Creao requests analytics + chart data

---

## 🚀 Quick Start

### Start the API Server

```bash
python dashboard_api.py
```

Server runs at: `http://localhost:8000`  
API Docs: `http://localhost:8000/docs`

---

## 📤 Step 1: Creao Sends Data

### Endpoint

```
POST http://your-api.com/api/data/send
```

### Request from Creao App

```javascript
// In your Creao app (JavaScript/React Native)

async function sendFarmerData(farmerId, farmerName, salesData) {
  const response = await fetch('http://your-api.com/api/data/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      farmer_id: farmerId,
      farmer_name: farmerName,
      data: salesData,
      metadata: {
        source: 'creao_app',
        version: '1.0'
      }
    })
  });
  
  return await response.json();
}

// Example usage
const salesData = [
  {
    week_start: "2025-09-01",
    crop: "tomato",
    total_supplied_kg: 500,
    total_sold_kg: 450,
    avg_delivery_delay_min: 20
  },
  {
    week_start: "2025-09-08",
    crop: "tomato",
    total_supplied_kg: 520,
    total_sold_kg: 480,
    avg_delivery_delay_min: 25
  }
  // ... more weeks
];

await sendFarmerData("farmer123", "John's Farm", salesData);
```

### Example with cURL

```bash
curl -X POST http://localhost:8000/api/data/send \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "farmer123",
    "farmer_name": "Johns Farm",
    "data": [
      {
        "week_start": "2025-09-01",
        "crop": "tomato",
        "total_supplied_kg": 500,
        "total_sold_kg": 450,
        "avg_delivery_delay_min": 20
      }
    ]
  }'
```

### Response

```json
{
  "status": "success",
  "message": "Data received for John's Farm",
  "farmer_id": "farmer123",
  "records_received": 1
}
```

---

## 📊 Step 2: Get Analytics & Charts

### Endpoint

```
POST http://your-api.com/api/analytics/generate
```

### Request from Creao App

```javascript
async function getAnalytics(farmerId, cropFilter = null) {
  const response = await fetch('http://your-api.com/api/analytics/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      farmer_id: farmerId,
      crop_filter: cropFilter,
      weeks: 12
    })
  });
  
  const analytics = await response.json();
  return analytics;
}

// Usage
const analytics = await getAnalytics("farmer123", "tomato");

// Now you have:
console.log(analytics.insights);        // AI insights
console.log(analytics.forecast);        // 2-week forecast
console.log(analytics.recommendations); // Recommendations
console.log(analytics.charts);          // Chart data!
```

### Response Structure

```json
{
  "status": "success",
  "farmer_id": "farmer123",
  "farmer_name": "John's Farm",
  "insights": [
    {
      "title": "Strong Tomato Demand",
      "explanation": "Sales consistently above 90% of supply"
    }
  ],
  "forecast": [
    {"week_start": "2025-10-01", "crop": "tomato", "kg": 610}
  ],
  "recommendations": [
    "Focus on tomato production - demand is high"
  ],
  "charts": {
    "supply_trend": {
      "chart_type": "line",
      "title": "Supply Trend",
      "data": [
        {"x": "2025-09-01", "y": 500, "crop": "tomato"},
        {"x": "2025-09-08", "y": 520, "crop": "tomato"}
      ]
    },
    "sales_performance": {
      "chart_type": "bar",
      "title": "Sales Performance",
      "data": [...]
    },
    "forecast": {
      "chart_type": "line",
      "title": "2-Week Forecast",
      "data": [...]
    },
    "distribution": {
      "chart_type": "pie",
      "title": "Supply Distribution",
      "data": [
        {"label": "tomato", "value": 2020},
        {"label": "mango", "value": 890}
      ]
    }
  },
  "source": "gemini"
}
```

---

## 📱 Complete Creao Integration Example

### React Native Component

```javascript
// screens/FarmerAnalytics.js

import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ScrollView, ActivityIndicator } from 'react-native';
import { LineChart, BarChart, PieChart } from 'react-native-chart-kit';

const API_BASE = 'https://your-api.com';

export default function FarmerAnalytics({ farmerId, farmerName }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);

  // Send farmer data
  async function sendData(salesData) {
    setLoading(true);
    try {
      await fetch(`${API_BASE}/api/data/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          farmer_id: farmerId,
          farmer_name: farmerName,
          data: salesData
        })
      });
    } catch (error) {
      console.error('Error sending data:', error);
    }
  }

  // Generate analytics
  async function generateAnalytics() {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/analytics/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          farmer_id: farmerId,
          crop_filter: null,
          weeks: 12
        })
      });
      
      const data = await response.json();
      setAnalytics(data);
    } catch (error) {
      console.error('Error generating analytics:', error);
    } finally {
      setLoading(false);
    }
  }

  // Auto-load on mount
  useEffect(() => {
    // First send any new data
    const farmerSalesData = getFarmerSalesFromDatabase();
    sendData(farmerSalesData);
    
    // Then generate analytics
    generateAnalytics();
  }, []);

  if (loading) {
    return <ActivityIndicator size="large" color="#4CAF50" />;
  }

  if (!analytics) {
    return <Text>Loading analytics...</Text>;
  }

  return (
    <ScrollView style={{ flex: 1, padding: 16 }}>
      {/* Header */}
      <Text style={{ fontSize: 24, fontWeight: 'bold', marginBottom: 16 }}>
        📊 Farm Analytics
      </Text>

      {/* Refresh Button */}
      <TouchableOpacity 
        onPress={generateAnalytics}
        style={{
          backgroundColor: '#4CAF50',
          padding: 12,
          borderRadius: 8,
          marginBottom: 16
        }}
      >
        <Text style={{ color: 'white', textAlign: 'center', fontWeight: 'bold' }}>
          🔄 Refresh Analytics
        </Text>
      </TouchableOpacity>

      {/* AI Insights */}
      <Text style={{ fontSize: 18, fontWeight: 'bold', marginTop: 16 }}>
        💡 Insights
      </Text>
      {analytics.insights.map((insight, i) => (
        <View key={i} style={{ 
          padding: 12, 
          backgroundColor: '#f5f5f5', 
          borderRadius: 8,
          marginTop: 8 
        }}>
          <Text style={{ fontWeight: 'bold' }}>{insight.title}</Text>
          <Text style={{ color: '#666' }}>{insight.explanation}</Text>
        </View>
      ))}

      {/* Supply Trend Chart */}
      <Text style={{ fontSize: 18, fontWeight: 'bold', marginTop: 24 }}>
        📈 Supply Trend
      </Text>
      <LineChart
        data={{
          labels: analytics.charts.supply_trend.data.map(d => d.x),
          datasets: [{
            data: analytics.charts.supply_trend.data.map(d => d.y)
          }]
        }}
        width={350}
        height={220}
        chartConfig={{
          backgroundColor: '#fff',
          backgroundGradientFrom: '#fff',
          backgroundGradientTo: '#fff',
          color: (opacity = 1) => `rgba(76, 175, 80, ${opacity})`,
        }}
        bezier
        style={{ marginTop: 8, borderRadius: 8 }}
      />

      {/* Forecast Chart */}
      <Text style={{ fontSize: 18, fontWeight: 'bold', marginTop: 24 }}>
        🔮 2-Week Forecast
      </Text>
      <LineChart
        data={{
          labels: analytics.charts.forecast.data.map(d => d.x),
          datasets: [{
            data: analytics.charts.forecast.data.map(d => d.y)
          }]
        }}
        width={350}
        height={220}
        chartConfig={{
          backgroundColor: '#fff',
          backgroundGradientFrom: '#fff',
          backgroundGradientTo: '#fff',
          color: (opacity = 1) => `rgba(255, 193, 7, ${opacity})`,
        }}
        style={{ marginTop: 8, borderRadius: 8 }}
      />

      {/* Recommendations */}
      <Text style={{ fontSize: 18, fontWeight: 'bold', marginTop: 24 }}>
        🎯 Recommendations
      </Text>
      {analytics.recommendations.map((rec, i) => (
        <View key={i} style={{
          padding: 12,
          backgroundColor: '#E8F5E9',
          borderRadius: 8,
          marginTop: 8
        }}>
          <Text>{i + 1}. {rec}</Text>
        </View>
      ))}
    </ScrollView>
  );
}
```

---

## 🔄 Complete Workflow

### 1. When Farmer Uses Creao App

```javascript
// Farmer creates a listing or updates sales
async function onFarmerActivity(farmerId) {
  // Get farmer's recent sales data from Creao database
  const salesData = await getRecentSalesData(farmerId);
  
  // Send to analytics API
  await fetch('http://your-api.com/api/data/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      farmer_id: farmerId,
      farmer_name: farmer.name,
      data: salesData
    })
  });
}
```

### 2. When Farmer Views Analytics

```javascript
// Farmer opens analytics screen
async function showAnalytics(farmerId) {
  // Generate analytics with charts
  const response = await fetch('http://your-api.com/api/analytics/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ farmer_id: farmerId })
  });
  
  const analytics = await response.json();
  
  // Display in UI
  displayInsights(analytics.insights);
  displayCharts(analytics.charts);
  displayRecommendations(analytics.recommendations);
}
```

---

## 🎨 Display Charts in Creao

### Using react-native-chart-kit

```bash
npm install react-native-chart-kit react-native-svg
```

```javascript
import { LineChart, BarChart, PieChart } from 'react-native-chart-kit';

// Line Chart
<LineChart
  data={{
    labels: analytics.charts.supply_trend.data.map(d => d.x),
    datasets: [{
      data: analytics.charts.supply_trend.data.map(d => d.y)
    }]
  }}
  width={350}
  height={220}
  chartConfig={{
    color: (opacity = 1) => `rgba(76, 175, 80, ${opacity})`,
  }}
  bezier
/>

// Bar Chart
<BarChart
  data={{
    labels: analytics.charts.sales_performance.data.map(d => d.x),
    datasets: [{
      data: analytics.charts.sales_performance.data.map(d => d.y)
    }]
  }}
  width={350}
  height={220}
/>

// Pie Chart
<PieChart
  data={analytics.charts.distribution.data.map((item, i) => ({
    name: item.label,
    population: item.value,
    color: COLORS[i],
    legendFontColor: '#7F7F7F',
  }))}
  width={350}
  height={220}
  chartConfig={{
    color: (opacity = 1) => `rgba(0, 0, 0, ${opacity})`,
  }}
  accessor="population"
/>
```

---

## 🌐 Deployment

### Deploy API Server

Same as dashboard - deploy to Render/Railway/Heroku:

```yaml
# render.yaml
services:
  - type: web
    name: farm-analytics-api
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn dashboard_api:app --host 0.0.0.0 --port $PORT"
```

Then update Creao app to use:
```javascript
const API_BASE = 'https://your-api.onrender.com';
```

---

## 🧪 Testing

### Test with cURL

```bash
# 1. Send data
curl -X POST http://localhost:8000/api/data/send \
  -H "Content-Type: application/json" \
  -d @test_data.json

# 2. Generate analytics
curl -X POST http://localhost:8000/api/analytics/generate \
  -H "Content-Type: application/json" \
  -d '{"farmer_id": "farmer123"}'

# 3. List all farmers
curl http://localhost:8000/api/farmers
```

### Test Data File (test_data.json)

```json
{
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
    }
  ]
}
```

---

## 📚 API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/data/send` | Send farmer data |
| POST | `/api/analytics/generate` | Generate analytics + charts |
| GET | `/api/farmers` | List all farmers |
| GET | `/api/farmers/{id}/data` | Get farmer's raw data |
| DELETE | `/api/farmers/{id}` | Delete farmer data |
| GET | `/api/health` | Health check |
| GET | `/docs` | Interactive API docs |

---

## 🎯 Summary

**What Creao Needs to Do:**

1. **Send Data** (once):
   ```javascript
   POST /api/data/send
   Body: { farmer_id, farmer_name, data: [...] }
   ```

2. **Get Analytics** (anytime):
   ```javascript
   POST /api/analytics/generate
   Body: { farmer_id, crop_filter }
   Response: { insights, forecast, recommendations, charts }
   ```

3. **Display Charts**:
   - Use `analytics.charts.supply_trend.data`
   - Use `analytics.charts.sales_performance.data`
   - Use `analytics.charts.forecast.data`
   - Use `analytics.charts.distribution.data`

**That's it!** 🎉

---

Ready to integrate? Start with:
```bash
python dashboard_api.py
```

Then test with the cURL examples above!

