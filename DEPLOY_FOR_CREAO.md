# 🚀 Deploy API for Creao Integration

Quick guide to deploy your analytics API and share it with Creao team.

---

## ⚡ Quick Deploy (Choose One)

### Option 1: Render.com (Recommended - Free)

**Time: 5 minutes**

1. **Create `requirements-api.txt`** (already done)
2. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add analytics API for Creao"
   git push
   ```

3. **Deploy on Render:**
   - Go to https://render.com
   - Sign up (free)
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Settings:
     - **Name:** `farm-analytics-api`
     - **Build Command:** `pip install fastapi uvicorn pandas google-genai python-dotenv requests`
     - **Start Command:** `uvicorn dashboard_api:app --host 0.0.0.0 --port $PORT`
   - Click "Create Web Service"

4. **Wait 2-3 minutes** for deployment

5. **Get your URL:** `https://farm-analytics-api.onrender.com`

**Done!** ✅

---

### Option 2: Railway (Easy - $5 Free Credit)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize
railway init

# Deploy
railway up

# Get URL
railway domain
```

Your URL: `https://your-app.railway.app`

---

### Option 3: Replit (Fastest - No Setup)

1. Go to https://replit.com
2. Create new Repl → Import from GitHub
3. Add your repo
4. Click "Run"
5. Share the URL

---

## 📝 What to Send to Creao Team

Once deployed, send them this information:

### **Email/Message Template:**

```
Subject: Analytics API Ready for Integration

Hi Creao Team,

The analytics API is deployed and ready for integration! Here are the details:

📡 API Base URL:
https://your-app.onrender.com

📚 Interactive Documentation:
https://your-app.onrender.com/docs

🔑 Key Endpoints:

1. Send Farmer Data:
   POST https://your-app.onrender.com/api/data/send
   
2. Generate Analytics & Charts:
   POST https://your-app.onrender.com/api/analytics/generate

📖 Full Integration Guide:
[Attach CREAO_API_INTEGRATION.md]

Let me know if you need any help with integration!
```

---

## 📋 Integration Details for Creao

### Endpoint 1: Send Farmer Data

```javascript
// When farmer creates/updates sales in Creao
const response = await fetch('https://your-app.onrender.com/api/data/send', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    farmer_id: farmerId,
    farmer_name: farmerName,
    data: [
      {
        week_start: "2025-09-01",
        crop: "tomato",
        total_supplied_kg: 500,
        total_sold_kg: 450,
        avg_delivery_delay_min: 20
      }
      // ... more weekly records
    ]
  })
});
```

### Endpoint 2: Get Analytics

```javascript
// When farmer views analytics in Creao
const response = await fetch('https://your-app.onrender.com/api/analytics/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    farmer_id: farmerId,
    crop_filter: null,  // or "tomato", "mango", etc.
    weeks: 12
  })
});

const analytics = await response.json();

// Now Creao has:
// - analytics.insights (AI insights)
// - analytics.forecast (2-week predictions)
// - analytics.recommendations (actionable advice)
// - analytics.charts (ready-to-display chart data)
```

---

## 🔧 Environment Variables

If using Gemini API (not mock data), set this on Render:

1. Go to your service on Render
2. Click "Environment"
3. Add:
   - Key: `GEMINI_API_KEY`
   - Value: `your_gemini_api_key`

---

## 🧪 Test Your Deployed API

```bash
# Test health
curl https://your-app.onrender.com/api/health

# Test send data
curl -X POST https://your-app.onrender.com/api/data/send \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "test123",
    "farmer_name": "Test Farm",
    "data": [{
      "week_start": "2025-09-01",
      "crop": "tomato",
      "total_supplied_kg": 500,
      "total_sold_kg": 450
    }]
  }'

# Test analytics
curl -X POST https://your-app.onrender.com/api/analytics/generate \
  -H "Content-Type: application/json" \
  -d '{"farmer_id": "test123"}'
```

---

## 📦 Files to Share with Creao

Send them these files:

1. **CREAO_API_INTEGRATION.md** - Complete integration guide
2. **API URL** - Your deployed endpoint
3. **API Docs URL** - https://your-app.onrender.com/docs
4. This **Quick Reference:**

```
API Base: https://your-app.onrender.com

Endpoints:
- POST /api/data/send          → Send farmer data
- POST /api/analytics/generate → Get analytics + charts
- GET  /api/farmers            → List all farmers
- GET  /api/health             → Health check
- GET  /docs                   → Interactive docs
```

---

## 🚨 Important Notes

### CORS is Already Enabled
Your API allows requests from any domain (good for development/hackathon).

For production, update this in `dashboard_api.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://creao-app.com"],  # Specify Creao domain
    ...
)
```

### Free Tier Limitations

**Render.com Free Tier:**
- API goes to sleep after 15 min of inactivity
- First request after sleep takes 30-60 seconds
- Good for hackathon, upgrade for production

**Railway Free Tier:**
- $5 credit/month
- ~500 hours of uptime
- Better for production

---

## 📱 Creao Implementation Example

Complete React Native example for Creao:

```javascript
// FarmerAnalytics.js
import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ActivityIndicator } from 'react-native';
import { LineChart } from 'react-native-chart-kit';

const API_BASE = 'https://your-app.onrender.com';

export default function FarmerAnalytics({ farmerId, farmerData }) {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(false);

  async function loadAnalytics() {
    setLoading(true);
    
    try {
      // Step 1: Send farmer data
      await fetch(`${API_BASE}/api/data/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          farmer_id: farmerId,
          farmer_name: farmerData.name,
          data: farmerData.weeklyRecords
        })
      });
      
      // Step 2: Get analytics
      const response = await fetch(`${API_BASE}/api/analytics/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ farmer_id: farmerId })
      });
      
      const data = await response.json();
      setAnalytics(data);
      
    } catch (error) {
      console.error('Analytics error:', error);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAnalytics();
  }, []);

  if (loading) return <ActivityIndicator />;

  return (
    <View>
      {/* Insights */}
      {analytics?.insights.map(insight => (
        <View key={insight.title}>
          <Text>{insight.title}</Text>
          <Text>{insight.explanation}</Text>
        </View>
      ))}

      {/* Chart */}
      <LineChart
        data={{
          labels: analytics?.charts.supply_trend.data.map(d => d.x),
          datasets: [{
            data: analytics?.charts.supply_trend.data.map(d => d.y)
          }]
        }}
        width={350}
        height={220}
      />
    </View>
  );
}
```

---

## ✅ Deployment Checklist

Before sending to Creao:

- [ ] Code pushed to GitHub
- [ ] API deployed (Render/Railway/Replit)
- [ ] Tested deployed API with curl
- [ ] Visited `/docs` endpoint - works
- [ ] Tested full flow (send data → get analytics)
- [ ] Prepared email/message with API details
- [ ] Attached CREAO_API_INTEGRATION.md
- [ ] Ready to help Creao team integrate!

---

## 🎯 Next Steps

1. **Deploy now** (5 minutes on Render)
2. **Get your URL**
3. **Test it** with curl commands above
4. **Send to Creao** with the email template
5. **Support their integration** if they have questions

---

**Ready to deploy! Choose Render.com for fastest deployment. 🚀**

