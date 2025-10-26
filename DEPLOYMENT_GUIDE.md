# 🚀 Deploy Analytics API for Creao

Complete deployment guide - get your API live in 10 minutes.

---

## ⚡ Quick Deploy to Render.com (FREE)

### Step 1: Prepare for Deployment

```bash
# Make sure everything is committed
git add .
git commit -m "Analytics API ready for Creao integration"
git push origin main
```

---

### Step 2: Deploy on Render.com

1. **Go to** https://render.com
2. **Sign up/Login** (use GitHub account for easy setup)
3. **Click** "New +" → "Web Service"
4. **Connect** your GitHub repository
5. **Configure:**

   **Settings:**
   - **Name:** `farm-analytics-api` (or your choice)
   - **Region:** Oregon (US West) or closest to you
   - **Branch:** `main`
   - **Root Directory:** leave blank
   - **Runtime:** Python 3
   
   **Build Command:**
   ```bash
   pip install fastapi uvicorn pandas google-genai python-dotenv requests
   ```
   
   **Start Command:**
   ```bash
   uvicorn dashboard_api:app --host 0.0.0.0 --port $PORT
   ```
   
   **Plan:** Free

6. **Click** "Create Web Service"

7. **Wait 2-3 minutes** for deployment

8. **Your URL:** `https://farm-analytics-api.onrender.com`

---

## 🧪 Test Your Deployed API

Once deployed, test it:

```bash
# Check health
curl https://farm-analytics-api.onrender.com/api/health

# Check docs
open https://farm-analytics-api.onrender.com/docs
```

---

## 📤 Upload Your Creao Data to Production

After deployment, upload your farmer data:

```bash
curl -X POST https://farm-analytics-api.onrender.com/api/creao/bulk-upload \
  -H "Content-Type: application/json" \
  -d @creao_farmers_data.json
```

Verify it worked:

```bash
curl https://farm-analytics-api.onrender.com/api/farmers
```

---

## 📧 Share with Creao Team

### Email Template:

```
Subject: Farm Analytics API - Ready for Integration

Hi Creao Team,

The analytics API is deployed and ready! 🎉

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📡 API BASE URL:
https://farm-analytics-api.onrender.com

📚 INTERACTIVE DOCS:
https://farm-analytics-api.onrender.com/docs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔑 KEY ENDPOINTS:

1. Generate Analytics for a Farmer:
   POST /api/analytics/generate
   
   Request:
   {
     "farmer_id": "100019a1edcbeed766ea9c19842fdcfa5f1",
     "crop_filter": null,
     "weeks": 12
   }
   
   Returns:
   - AI-generated insights
   - 2-week forecast
   - Recommendations
   - Chart data (supply_trend, sales_performance, forecast, distribution)

2. List All Farmers:
   GET /api/farmers

3. Send New Farmer Data:
   POST /api/data/send
   
   Request:
   {
     "farmer_id": "...",
     "farmer_name": "...",
     "data": [
       {
         "week_start": "2025-09-01",
         "crop": "tomato",
         "total_supplied_kg": 500,
         "total_sold_kg": 450,
         "avg_delivery_delay_min": 20
       }
     ]
   }

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 RESPONSE FORMAT:

{
  "status": "success",
  "farmer_id": "...",
  "analytics": {
    "insights": [
      {"title": "...", "explanation": "..."}
    ],
    "forecast": [
      {"week_start": "2025-10-29", "crop": "tomato", "kg": 610}
    ],
    "recommendations": ["..."]
  },
  "charts": {
    "supply_trend": {"chart_type": "line", "data": [...]},
    "sales_performance": {"chart_type": "bar", "data": [...]},
    "forecast": {"chart_type": "line", "data": [...]},
    "distribution": {"chart_type": "pie", "data": [...]}
  }
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧪 TEST IT NOW:

curl -X POST https://farm-analytics-api.onrender.com/api/analytics/generate \
  -H "Content-Type: application/json" \
  -d '{"farmer_id": "100019a1edcbeed766ea9c19842fdcfa5f1"}'

Or visit the interactive docs to try all endpoints:
https://farm-analytics-api.onrender.com/docs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ ALREADY LOADED:
- 7 farmers from your database
- 12 weeks of sales history each
- Ready to generate analytics

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Let me know if you need any help with integration!

Best,
[Your Name]
```

---

## 📋 Quick Reference for Creao

### API Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/analytics/generate` | POST | Generate AI analytics for a farmer |
| `/api/data/send` | POST | Send farmer data to system |
| `/api/creao/bulk-upload` | POST | Upload multiple farmers at once |
| `/api/farmers` | GET | List all farmers |
| `/api/farmers/{id}/data` | GET | Get specific farmer data |
| `/api/health` | GET | Check API health |
| `/docs` | GET | Interactive API documentation |

---

## 🔧 Environment Variables (Optional)

If you want to use real Gemini AI (not mock data), add on Render:

1. Go to your service dashboard
2. Click "Environment"
3. Add variable:
   - **Key:** `GEMINI_API_KEY`
   - **Value:** `your_gemini_api_key_here`
4. Save and redeploy

---

## 🚨 Important Notes

### Free Tier Behavior

**Render Free Tier:**
- API **sleeps after 15 min** of inactivity
- **First request** after sleep takes 30-60 seconds (cold start)
- Subsequent requests are fast
- Good for demo/hackathon
- For production, upgrade to paid ($7/month for always-on)

**Tell Creao team:**
> "The API is on a free tier, so the first request may take 30-60 seconds if it's been idle. Subsequent requests are instant. This is perfect for the hackathon demo!"

---

## 🔄 Update API After Deployment

If you need to make changes:

```bash
# Make changes locally
# Test them
python dashboard_api.py

# Commit and push
git add .
git commit -m "Update analytics API"
git push

# Render auto-deploys! (takes 2-3 min)
```

---

## 📊 Monitor Your API

On Render dashboard you can see:
- ✅ Deployment status
- 📊 Request logs
- 💻 CPU/Memory usage
- 🚨 Errors

---

## 🎯 Complete Deployment Checklist

- [ ] Code committed and pushed to GitHub
- [ ] Render.com account created
- [ ] Web Service created and deployed
- [ ] API is live (visit `/docs`)
- [ ] Uploaded `creao_farmers_data.json`
- [ ] Tested with curl
- [ ] Shared URL with Creao team
- [ ] Email sent with API details

---

## 🆘 Troubleshooting

### API won't start?

Check Render logs:
1. Go to your service
2. Click "Logs"
3. Look for errors

Common fixes:
- Make sure `dashboard_api.py` is in repo root
- Check that all imports are correct
- Verify `requirements-api.txt` has all dependencies

### API returns errors?

Test locally first:
```bash
python dashboard_api.py
curl http://localhost:8000/api/health
```

### Slow response?

First request after sleep takes 30-60 seconds (free tier). Subsequent requests are fast.

---

## 🚀 Ready to Deploy!

**Commands to run:**

```bash
# 1. Commit everything
git add .
git commit -m "Analytics API for Creao"
git push

# 2. Go to render.com and create service

# 3. Upload data to production
curl -X POST https://your-api.onrender.com/api/creao/bulk-upload \
  -H "Content-Type: application/json" \
  -d @creao_farmers_data.json

# 4. Share with Creao!
```

**Time to deploy: ~10 minutes** ⏱️

---

**Need help? Check the logs or test locally first!** 🎉

