# 📊 Dashboard Deployment Guide

How to deploy your Dash analytics dashboard and integrate it with Creao.

---

## 🚀 Quick Deploy

### Option 1: Render (Recommended - Free)

1. **Create account**: https://render.com

2. **Create `render.yaml`** (already created below)

3. **Push to GitHub**:
```bash
git add .
git commit -m "Add analytics dashboard"
git push
```

4. **Deploy**:
   - Go to Render Dashboard
   - New → Web Service
   - Connect your GitHub repo
   - Render will auto-detect and deploy!

5. **Get your URL**: `https://your-app.onrender.com`

**Cost**: Free tier available

---

### Option 2: Railway (Easy - Free Trial)

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

**Cost**: Free $5 credit/month

---

### Option 3: Heroku

```bash
# Install Heroku CLI
brew install heroku/brew/heroku  # macOS
# or download from heroku.com

# Login
heroku login

# Create app
heroku create your-farm-analytics

# Deploy
git push heroku main

# Open
heroku open
```

**Cost**: $7/month for basic dyno

---

### Option 4: PythonAnywhere (Simplest)

1. Sign up: https://www.pythonanywhere.com
2. Upload your files
3. Create web app
4. Configure WSGI file:
```python
from dashboard import app
application = app.server
```
5. Reload

**Cost**: Free tier available

---

## 📦 Deployment Files

### `render.yaml`

```yaml
services:
  - type: web
    name: farm-analytics-dashboard
    env: python
    buildCommand: "pip install -r requirements-dashboard.txt"
    startCommand: "gunicorn dashboard:server --bind 0.0.0.0:$PORT"
    envVars:
      - key: PYTHON_VERSION
        value: 3.9.0
      - key: GEMINI_API_KEY
        sync: false
```

### `Procfile` (for Heroku)

```
web: gunicorn dashboard:server
```

### `requirements-dashboard.txt`

```
dash>=2.14.0
plotly>=5.18.0
pandas>=2.0.0
gunicorn>=21.2.0
google-genai>=0.2.0
python-dotenv>=1.0.0
```

---

## 🔗 Integrate with Creao App

### Method 1: iFrame Embed (Easiest)

In your Creao mobile app (React Native):

```javascript
import { WebView } from 'react-native-webview';

function AnalyticsDashboard({ farmerId }) {
  const dashboardUrl = `https://your-dashboard.onrender.com?farmer=${farmerId}`;
  
  return (
    <WebView
      source={{ uri: dashboardUrl }}
      style={{ flex: 1 }}
    />
  );
}
```

For web app:
```html
<iframe 
  src="https://your-dashboard.onrender.com?farmer=farmer123"
  width="100%"
  height="800px"
  frameborder="0">
</iframe>
```

---

### Method 2: Deep Link Button

Add a button in Creao that opens dashboard in browser:

```javascript
import { Linking } from 'react-native';

function ViewAnalytics({ farmerId }) {
  const openDashboard = () => {
    const url = `https://your-dashboard.onrender.com?farmer=${farmerId}`;
    Linking.openURL(url);
  };
  
  return (
    <TouchableOpacity onPress={openDashboard}>
      <Text>📊 View Analytics Dashboard</Text>
    </TouchableOpacity>
  );
}
```

---

### Method 3: API Mode (Advanced)

Make dashboard return JSON when called with `?api=true`:

Add to `dashboard.py`:
```python
from flask import request, jsonify

@app.server.route('/api/analytics')
def api_analytics():
    farmer_id = request.args.get('farmer_id')
    crop = request.args.get('crop')
    
    # Generate analytics
    analytics = analyze_csv("sample_weekly.csv", crop=crop)
    
    return jsonify(analytics)
```

Then in Creao app:
```javascript
const response = await fetch(
  `https://your-dashboard.onrender.com/api/analytics?farmer_id=${farmerId}`
);
const analytics = await response.json();
```

---

## 🎨 Customize for Creao Branding

### Update Colors in `dashboard.py`

```python
COLORS = {
    'primary': '#YOUR_PRIMARY_COLOR',
    'secondary': '#YOUR_SECONDARY_COLOR',
    'accent': '#YOUR_ACCENT_COLOR',
    'background': '#f8f9fa',
    'text': '#212529'
}
```

### Add Your Logo

1. Create `assets/` folder
2. Add `logo.png`
3. Restart dashboard

---

## 🔒 Add Authentication (Optional)

### Simple Password Protection

Add to `dashboard.py`:

```python
import dash_auth

VALID_USERNAME_PASSWORD_PAIRS = {
    'farmer': 'harvest2025'
}

auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)
```

### OAuth with Creao

```python
from flask import session, redirect
from authlib.integrations.flask_client import OAuth

oauth = OAuth(app.server)

creao = oauth.register(
    name='creao',
    client_id='YOUR_CREAO_CLIENT_ID',
    client_secret='YOUR_CREAO_CLIENT_SECRET',
    authorize_url='https://creao.com/oauth/authorize',
    access_token_url='https://creao.com/oauth/token',
)

@app.server.route('/login')
def login():
    return creao.authorize_redirect('YOUR_CALLBACK_URL')
```

---

## 🧪 Test Before Deploying

### Local Testing

```bash
# Install dashboard dependencies
pip install dash plotly pandas gunicorn

# Run dashboard
python dashboard.py

# Visit: http://localhost:8050
```

### Test iFrame Embedding

Create `test_embed.html`:
```html
<!DOCTYPE html>
<html>
<head>
    <title>Dashboard Test</title>
</head>
<body>
    <h1>Testing Dashboard Embed</h1>
    <iframe 
        src="http://localhost:8050"
        width="100%"
        height="800px"
        frameborder="0">
    </iframe>
</body>
</html>
```

Open in browser to test.

---

## 📱 Mobile Optimization

### Add Responsive Design

In `dashboard.py`, add:

```python
app.layout = html.Div([
    # ... your layout
], style={
    'fontFamily': 'Arial, sans-serif',
    'margin': '0',
    'padding': '0',
    '@media (max-width: 768px)': {
        'padding': '10px'
    }
})
```

### Disable Zoom

```python
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        {%metas%}
        <title>{%title%}</title>
        {%css%}
    </head>
    <body>
        {%app_entry%}
        {%config%}
        {%scripts%}
        {%renderer%}
    </body>
</html>
'''
```

---

## 🚀 Production Checklist

Before deploying:

- [ ] Update `COLORS` to match Creao branding
- [ ] Add your logo to `assets/logo.png`
- [ ] Set `GEMINI_API_KEY` environment variable
- [ ] Test on mobile device
- [ ] Test iFrame embedding
- [ ] Set up analytics tracking (optional)
- [ ] Configure HTTPS (automatic on Render/Railway)
- [ ] Test with real farmer data

---

## 🔗 Share with Creao Team

After deployment, send:

1. **Dashboard URL**: `https://your-dashboard.onrender.com`
2. **iFrame Code**:
```html
<iframe 
  src="https://your-dashboard.onrender.com?farmer=FARMER_ID"
  width="100%"
  height="800px"
  frameborder="0">
</iframe>
```
3. **Deep Link**: For "Open in Browser" button
4. **API Endpoint** (if using): `https://your-dashboard.onrender.com/api/analytics`

---

## 💡 Example Integration Flow

**In Creao App:**

```javascript
// screens/FarmerDashboard.js

import React from 'react';
import { View, TouchableOpacity, Text } from 'react-native';
import { WebView } from 'react-native-webview';

export default function FarmerDashboard({ farmer }) {
  const dashboardUrl = `https://your-dashboard.onrender.com?farmer=${farmer.id}`;
  
  return (
    <View style={{ flex: 1 }}>
      {/* Header with refresh */}
      <View style={{ padding: 10, background: '#4CAF50' }}>
        <Text style={{ color: 'white', fontSize: 18 }}>
          📊 Analytics Dashboard
        </Text>
      </View>
      
      {/* Embedded Dashboard */}
      <WebView
        source={{ uri: dashboardUrl }}
        style={{ flex: 1 }}
        onLoad={() => console.log('Dashboard loaded')}
      />
    </View>
  );
}
```

---

## 🎯 Advanced Features

### Multi-Language Support

```python
LANGUAGES = {
    'en': {'title': 'Farm Analytics', 'insights': 'Insights'},
    'es': {'title': 'Analítica Agrícola', 'insights': 'Perspectivas'},
}

@app.callback(...)
def update_language(lang):
    return LANGUAGES[lang]['title']
```

### Export to PDF

```python
from dash import dcc

html.Button("📄 Export PDF", id='export-pdf'),
dcc.Download(id="download-pdf")

@app.callback(
    Output("download-pdf", "data"),
    Input("export-pdf", "n_clicks")
)
def export_pdf(n_clicks):
    if n_clicks:
        # Generate PDF (use reportlab or weasyprint)
        return dcc.send_file("analytics_report.pdf")
```

### Real-time Updates

```python
dcc.Interval(
    id='interval-component',
    interval=60*1000,  # Update every minute
    n_intervals=0
)
```

---

## 🆘 Troubleshooting

**Dashboard won't start**
```bash
pip install --upgrade dash plotly pandas
python dashboard.py
```

**Charts not showing**
→ Check browser console for errors
→ Verify sample_weekly.csv exists

**Deploy fails**
→ Check `requirements-dashboard.txt` is correct
→ Verify Python version (3.9+)

**iFrame blocked**
→ Add CORS headers (automatic on Render)
→ Use HTTPS URL

---

## 📊 Success Metrics

Track:
- Dashboard load time
- Farmer engagement (views/week)
- Most viewed insights
- Click-through on recommendations

Add to `dashboard.py`:
```python
import logging

@app.callback(...)
def track_view(farmer_id):
    logging.info(f"Dashboard viewed by {farmer_id}")
```

---

**Ready to deploy! 🚀**

Quick steps:
1. `pip install -r requirements-dashboard.txt`
2. `python dashboard.py` (test locally)
3. Push to GitHub
4. Deploy on Render
5. Share URL with Creao team

Questions? Check the troubleshooting section above!

