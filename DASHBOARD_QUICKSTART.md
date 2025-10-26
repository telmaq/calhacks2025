# 📊 Dashboard Quick Start

**Get your interactive analytics dashboard running in 5 minutes!**

---

## ⚡ 3-Step Setup

```bash
# 1. Install
pip install -r requirements-dashboard.txt

# 2. Test
python test_dashboard.py

# 3. Run
python dashboard.py
```

**Visit:** http://localhost:8050

---

## 🎯 What You Get

### Interactive Controls
- **Farmer Dropdown** - Select which farmer's data to view
- **Crop Filter** - Filter by specific crop or view all
- **Time Period** - Choose 4, 8, or 12 weeks of historical data
- **Refresh Button** - Generate new AI insights on-demand

### Visual Analytics
- 📈 **Supply Trend** - Line chart showing supply over time
- 📊 **Sales Performance** - Bar chart comparing sales by crop
- 🔮 **2-Week Forecast** - AI predictions for upcoming weeks
- 🥧 **Crop Distribution** - Pie chart of supply breakdown

### AI Insights
- 💡 **Top 3 Insights** - Key patterns discovered by AI
- 🎯 **Recommendations** - Actionable advice for farmers
- 📊 **Key Metrics** - Supply totals, sales rate, delivery times

---

## 🌐 Deploy in 3 Minutes

### Option A: Render (Free, Recommended)

```bash
# 1. Push to GitHub
git add .
git commit -m "Add analytics dashboard"
git push

# 2. Go to render.com
# 3. New Web Service → Connect repo
# 4. Auto-deploys!
```

**Result:** `https://your-app.onrender.com`

### Option B: Railway (Free $5 credit)

```bash
railway init
railway up
```

**Result:** `https://your-app.railway.app`

---

## 🔗 Embed in Creao App

### React Native

```javascript
import { WebView } from 'react-native-webview';

<WebView
  source={{ uri: 'https://your-dashboard.onrender.com?farmer=123' }}
  style={{ flex: 1 }}
/>
```

### HTML/Web

```html
<iframe 
  src="https://your-dashboard.onrender.com"
  width="100%"
  height="800px">
</iframe>
```

### Open in Browser Button

```javascript
import { Linking } from 'react-native';

<TouchableOpacity 
  onPress={() => Linking.openURL('https://your-dashboard.onrender.com')}
>
  <Text>📊 View Analytics Dashboard</Text>
</TouchableOpacity>
```

---

## 🎨 Customize

### Change Colors

Edit `dashboard.py`:
```python
COLORS = {
    'primary': '#4CAF50',      # Your primary color
    'secondary': '#8BC34A',    # Your secondary color
    'accent': '#FFC107',       # Accent color
    'background': '#f8f9fa',   # Background
    'text': '#212529'          # Text color
}
```

### Add Logo

1. Create `assets/` folder
2. Add `assets/logo.png`
3. Restart dashboard

---

## 🎬 Demo Flow

1. **Open dashboard** - "This is our AI analytics dashboard"
2. **Select filter** - Click dropdown → choose "Tomato"
3. **Click refresh** - "AI generates insights in real-time"
4. **Show charts** - Point to supply trend, forecast
5. **Explain embed** - "This embeds in our Creao mobile app"

---

## 🧪 Test Commands

```bash
# Verify setup
python test_dashboard.py

# Run dashboard
python dashboard.py

# Open in browser
open http://localhost:8050
```

---

## 📚 Full Documentation

- **Complete Guide:** `DASHBOARD_DEPLOYMENT.md`
- **Creao Integration:** `CREAO_ANALYTICS_INTEGRATION.md`
- **General Setup:** `SETUP.md`

---

## 🆘 Quick Fixes

**Dashboard won't start?**
```bash
pip install dash plotly pandas gunicorn
python dashboard.py
```

**Charts not showing?**
- Check `sample_weekly.csv` exists
- Restart dashboard
- Clear browser cache

**Deploy fails?**
- Verify `requirements-dashboard.txt` is in repo
- Check Python version (3.9+)
- See `DASHBOARD_DEPLOYMENT.md` troubleshooting

---

## 🎉 You're Ready!

Your dashboard has:
- ✅ Interactive dropdowns and buttons
- ✅ Beautiful Plotly graphs
- ✅ AI-powered insights
- ✅ Ready to deploy (free hosting)
- ✅ Easy to embed in Creao

**Start now:**
```bash
pip install -r requirements-dashboard.txt
python dashboard.py
```

Visit http://localhost:8050 and explore! 🚀

