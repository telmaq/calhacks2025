# 📊 Displaying Gemini Analytics as Graphs in Creao

Complete guide to display AI-generated analytics as beautiful graphs in the Creao app.

---

## 🎯 How It Works

```
1. Creao Farmer Data → API
2. API → Gemini AI → Analytics Generated
3. API → Chart-Ready Data → Creao
4. Creao → Display Beautiful Graphs
```

---

## 📱 React Native Implementation

### Install Chart Library

```bash
npm install react-native-chart-kit react-native-svg
# or
npm install victory-native
```

---

## 📊 Example: Complete Analytics Screen

```javascript
import React, { useState, useEffect } from 'react';
import { 
  View, 
  Text, 
  ScrollView, 
  ActivityIndicator,
  StyleSheet,
  Dimensions 
} from 'react-native';
import { LineChart, BarChart, PieChart } from 'react-native-chart-kit';

const API_BASE = 'https://your-api.onrender.com';

export default function FarmerAnalytics({ farmerId }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, [farmerId]);

  async function loadAnalytics() {
    try {
      setLoading(true);
      
      // Call API to get analytics
      const response = await fetch(`${API_BASE}/api/analytics/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          farmer_id: farmerId,
          weeks: 12 
        })
      });
      
      const data = await response.json();
      setAnalytics(data);
      
    } catch (error) {
      console.error('Analytics error:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator size="large" color="#4CAF50" />
        <Text>Generating AI Analytics...</Text>
      </View>
    );
  }

  if (!analytics) return null;

  // Prepare data for charts
  const supplyTrendData = prepareLineChartData(analytics.charts.supply_trend);
  const salesBarData = prepareBarChartData(analytics.charts.sales_performance);
  const distributionData = preparePieChartData(analytics.charts.distribution);

  return (
    <ScrollView style={styles.container}>
      {/* AI Insights Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🤖 AI Insights</Text>
        {analytics.analytics.insights.map((insight, idx) => (
          <View key={idx} style={styles.insightCard}>
            <Text style={styles.insightTitle}>{insight.title}</Text>
            <Text style={styles.insightText}>{insight.explanation}</Text>
          </View>
        ))}
      </View>

      {/* Supply Trend Chart */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📈 Supply Trend (12 Weeks)</Text>
        <LineChart
          data={supplyTrendData}
          width={Dimensions.get('window').width - 40}
          height={220}
          chartConfig={{
            backgroundColor: '#ffffff',
            backgroundGradientFrom: '#4CAF50',
            backgroundGradientTo: '#81C784',
            decimalPlaces: 0,
            color: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
            labelColor: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
            style: { borderRadius: 16 },
            propsForDots: {
              r: '6',
              strokeWidth: '2',
              stroke: '#ffa726'
            }
          }}
          bezier
          style={styles.chart}
        />
      </View>

      {/* Sales Performance Chart */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📊 Sales by Crop</Text>
        <BarChart
          data={salesBarData}
          width={Dimensions.get('window').width - 40}
          height={220}
          chartConfig={{
            backgroundColor: '#ffffff',
            backgroundGradientFrom: '#2196F3',
            backgroundGradientTo: '#64B5F6',
            decimalPlaces: 0,
            color: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
            labelColor: (opacity = 1) => `rgba(255, 255, 255, ${opacity})`,
          }}
          style={styles.chart}
        />
      </View>

      {/* Distribution Pie Chart */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🥧 Crop Distribution</Text>
        <PieChart
          data={distributionData}
          width={Dimensions.get('window').width - 40}
          height={220}
          chartConfig={{
            color: (opacity = 1) => `rgba(76, 175, 80, ${opacity})`,
          }}
          accessor="value"
          backgroundColor="transparent"
          paddingLeft="15"
          style={styles.chart}
        />
      </View>

      {/* AI Forecast Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🔮 AI Forecast (Next 2 Weeks)</Text>
        {analytics.analytics.forecast.map((f, idx) => (
          <View key={idx} style={styles.forecastCard}>
            <Text style={styles.forecastWeek}>Week: {f.week_start}</Text>
            <Text style={styles.forecastCrop}>{f.crop}</Text>
            <Text style={styles.forecastAmount}>{f.kg} kg predicted</Text>
          </View>
        ))}
      </View>

      {/* Recommendations */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>💡 AI Recommendations</Text>
        {analytics.analytics.recommendations.map((rec, idx) => (
          <View key={idx} style={styles.recommendationCard}>
            <Text style={styles.recommendationText}>• {rec}</Text>
          </View>
        ))}
      </View>
    </ScrollView>
  );
}

// Helper functions to transform API data to chart format
function prepareLineChartData(chartData) {
  const data = chartData.data;
  
  return {
    labels: data.slice(0, 6).map(d => {
      const date = new Date(d.x);
      return `${date.getMonth() + 1}/${date.getDate()}`;
    }),
    datasets: [{
      data: data.slice(0, 6).map(d => d.y)
    }]
  };
}

function prepareBarChartData(chartData) {
  const data = chartData.data;
  
  return {
    labels: data.map(d => d.label || d.crop).slice(0, 4),
    datasets: [{
      data: data.map(d => d.value || d.y).slice(0, 4)
    }]
  };
}

function preparePieChartData(chartData) {
  const data = chartData.data;
  const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'];
  
  return data.slice(0, 5).map((d, idx) => ({
    name: d.label || d.crop,
    value: d.value || d.y,
    color: colors[idx],
    legendFontColor: '#7F7F7F',
    legendFontSize: 12
  }));
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  loading: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  section: {
    backgroundColor: 'white',
    margin: 10,
    padding: 15,
    borderRadius: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 15,
    color: '#333',
  },
  chart: {
    marginVertical: 8,
    borderRadius: 16,
  },
  insightCard: {
    backgroundColor: '#E8F5E9',
    padding: 12,
    borderRadius: 8,
    marginBottom: 10,
  },
  insightTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2E7D32',
    marginBottom: 5,
  },
  insightText: {
    fontSize: 14,
    color: '#555',
  },
  forecastCard: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    backgroundColor: '#E3F2FD',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  forecastWeek: {
    fontSize: 14,
    color: '#1976D2',
  },
  forecastCrop: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#0D47A1',
  },
  forecastAmount: {
    fontSize: 14,
    color: '#1565C0',
  },
  recommendationCard: {
    backgroundColor: '#FFF3E0',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  recommendationText: {
    fontSize: 14,
    color: '#E65100',
  },
});
```

---

## 🎨 Alternative: Victory Charts

If you prefer Victory (more customizable):

```javascript
import { VictoryLine, VictoryBar, VictoryPie, VictoryChart, VictoryTheme } from 'victory-native';

// Supply Trend with Victory
<VictoryChart theme={VictoryTheme.material}>
  <VictoryLine
    data={analytics.charts.supply_trend.data.map(d => ({
      x: new Date(d.x),
      y: d.y
    }))}
    style={{
      data: { stroke: "#4CAF50", strokeWidth: 3 }
    }}
  />
</VictoryChart>

// Bar Chart
<VictoryChart>
  <VictoryBar
    data={analytics.charts.sales_performance.data.map(d => ({
      x: d.crop,
      y: d.value
    }))}
    style={{
      data: { fill: "#2196F3" }
    }}
  />
</VictoryChart>

// Pie Chart
<VictoryPie
  data={analytics.charts.distribution.data.map(d => ({
    x: d.label,
    y: d.value
  }))}
  colorScale={["tomato", "orange", "gold", "cyan", "navy"]}
/>
```

---

## 🔄 Real-Time Updates

### Auto-refresh analytics every 5 minutes:

```javascript
useEffect(() => {
  loadAnalytics();
  
  const interval = setInterval(() => {
    loadAnalytics();
  }, 5 * 60 * 1000); // 5 minutes
  
  return () => clearInterval(interval);
}, [farmerId]);
```

---

## 📊 Advanced: Combined Historical + Forecast Chart

```javascript
function CombinedForecastChart({ analytics }) {
  // Combine historical and forecast data
  const historicalData = analytics.charts.supply_trend.data;
  const forecastData = analytics.analytics.forecast.map(f => ({
    x: f.week_start,
    y: f.kg,
    isForecast: true
  }));
  
  const combinedData = [...historicalData, ...forecastData];
  
  return (
    <LineChart
      data={{
        labels: combinedData.slice(-8).map(d => {
          const date = new Date(d.x);
          return `${date.getMonth() + 1}/${date.getDate()}`;
        }),
        datasets: [
          {
            data: combinedData.slice(-8).map(d => d.y),
            color: (opacity = 1) => d.isForecast 
              ? `rgba(255, 165, 0, ${opacity})` // Orange for forecast
              : `rgba(76, 175, 80, ${opacity})`, // Green for historical
            strokeDasharray: combinedData.map(d => d.isForecast ? [5, 5] : [0, 0])
          }
        ],
        legend: ['Historical', 'AI Forecast']
      }}
      width={Dimensions.get('window').width - 40}
      height={220}
      chartConfig={{...}}
    />
  );
}
```

---

## 🎯 Complete Integration Flow

### 1. In Creao App Startup:

```javascript
// Load farmer data and send to API
async function syncFarmerData() {
  const farmerData = await fetchFarmerDataFromCreaoDatabase();
  
  await fetch(`${API_BASE}/api/data/send`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      farmer_id: farmerId,
      farmer_name: farmerName,
      data: farmerData
    })
  });
}
```

### 2. When Farmer Opens Analytics Screen:

```javascript
// Generate analytics with Gemini AI
const analytics = await fetch(`${API_BASE}/api/analytics/generate`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ farmer_id: farmerId })
}).then(r => r.json());

// Display all graphs
<FarmerAnalytics farmerId={farmerId} />
```

---

## 📸 What It Looks Like

```
┌─────────────────────────────────────────┐
│  🤖 AI Insights                         │
│  ┌───────────────────────────────────┐  │
│  │ Strong Tomato Demand              │  │
│  │ Sales above 90% of supply...      │  │
│  └───────────────────────────────────┘  │
│                                          │
│  📈 Supply Trend                        │
│  [Beautiful Line Graph]                 │
│                                          │
│  📊 Sales by Crop                       │
│  [Bar Chart showing crops]              │
│                                          │
│  🥧 Crop Distribution                   │
│  [Pie Chart]                            │
│                                          │
│  🔮 AI Forecast                         │
│  Week 2025-10-29: tomato - 610kg        │
│  Week 2025-11-05: tomato - 620kg        │
│                                          │
│  💡 AI Recommendations                  │
│  • Focus on tomato production           │
│  • Improve delivery times               │
└─────────────────────────────────────────┘
```

---

## ✅ Summary

**YES!** Gemini API can:

1. ✅ **Analyze** your Creao farmer data
2. ✅ **Generate** AI-powered insights
3. ✅ **Forecast** next 2 weeks
4. ✅ **Recommend** actionable improvements
5. ✅ **Format** data for beautiful graphs
6. ✅ **Display** in Creao app with charts

**The API returns everything you need to display professional analytics dashboards!**

---

## 🚀 Next Steps

1. Test API locally with test_creao_upload.py
2. See the analytics JSON response
3. Deploy API to Render
4. Add charting library to Creao app
5. Implement analytics screen
6. Show beautiful AI-powered graphs! 📊

---

**The Gemini AI does the heavy lifting, your app just displays the results beautifully!** 🎨

