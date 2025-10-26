# 🎯 Quick Command Reference

Copy and paste these commands to run your Gemini AI analytics system.

---

## 🚀 Setup (First Time)

```bash
# Install all dependencies
pip install -r requirements.txt

# (Optional) Get Gemini API key from:
# https://aistudio.google.com/app/apikey

# Configure environment (optional - works without it!)
cp .env.example .env
# Edit .env and add: GEMINI_API_KEY=your_key_here
```

---

## ✅ Verify Everything Works

```bash
# Check setup and dependencies
python demo.py --check
```

---

## 📊 CSV Analytics

```bash
# Analyze farm data
python analyze_csv.py sample_weekly.csv

# Analyze specific crop
python analyze_csv.py sample_weekly.csv tomato

# With your own CSV file
python analyze_csv.py path/to/your/data.csv
```

**Output:** Insights, 2-week forecast, recommendations

---

## 🖼️ Image Analysis

```bash
# Analyze produce/crate image
python analyze_image.py path/to/image.jpg
```

**Output:** Crate count, weight estimate, quality score

---

## 🎪 Complete Demo

```bash
# Run full hackathon demo
python demo.py

# Run specific parts
python demo.py --csv-only      # CSV analytics only
python demo.py --image-only    # Image analytics only
python demo.py --api-only      # API integration only
python demo.py --check         # Setup verification only
```

---

## 🚀 Start API Server

```bash
# Start FastAPI server
python app.py

# Server runs at: http://localhost:8001
# API docs at: http://localhost:8001/docs
```

**New Endpoints:**
- `POST /api/v1/analytics/csv` - CSV analytics
- `POST /api/v1/analytics/image` - Image analysis
- `GET /api/v1/analytics/status` - Check status

---

## 🧪 Test API

```bash
# Test all endpoints
python test_api.py
```

---

## 📖 Integration Examples

```bash
# See code examples
python example_usage.py
```

---

## 🌐 API Examples with cURL

### Test Analytics Status
```bash
curl http://localhost:8001/api/v1/analytics/status
```

### CSV Analytics
```bash
curl -X POST http://localhost:8001/api/v1/analytics/csv \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "farmer123",
    "csv_data": "week_start,crop,total_supplied_kg,total_sold_kg\n2025-09-01,tomato,500,450"
  }'
```

### Image Analytics
```bash
# First encode image
base64 -i image.jpg -o image.b64

# Then send request
curl -X POST http://localhost:8001/api/v1/analytics/image \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "farmer123",
    "image_base64": "'$(cat image.b64)'"
  }'
```

---

## 🛠️ Troubleshooting

### Kill process on port 8001
```bash
lsof -ti:8001 | xargs kill -9
```

### Create virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Check Python version
```bash
python --version  # Should be 3.7+
```

### Reinstall dependencies
```bash
pip install --upgrade -r requirements.txt
```

---

## 📚 View Documentation

```bash
# Quick start guide
cat QUICKSTART.md

# Full setup guide
cat SETUP.md

# Complete overview
cat IMPLEMENTATION_SUMMARY.md

# This reference
cat COMMANDS.md
```

---

## 🎯 Recommended Demo Flow

```bash
# Terminal 1: Show data
cat sample_weekly.csv

# Terminal 1: Run analysis
python analyze_csv.py sample_weekly.csv

# Terminal 2: Start API server
python app.py

# Browser: Open API docs
# http://localhost:8001/docs
```

---

## ⚡ One-Line Demo Commands

```bash
# Fastest demo (everything automatic)
python demo.py

# Just show CSV analytics
python analyze_csv.py sample_weekly.csv | tail -30

# Check if everything works
python demo.py --check && echo "✅ Ready!"

# Test API (if server running)
python test_api.py
```

---

## 🎓 For Your Presentation

**Option 1: Command Line Demo (Simplest)**
```bash
python analyze_csv.py sample_weekly.csv
```

**Option 2: API Demo (Most Impressive)**
```bash
# Terminal 1
python app.py

# Browser
# Visit: http://localhost:8001/docs
# Try the POST /api/v1/analytics/csv endpoint
```

**Option 3: Full Demo Script (Most Complete)**
```bash
python demo.py
```

---

## 💡 Pro Tips

- **No API key?** Everything works with mock data!
- **Quick test:** `python demo.py --check`
- **Short on time?** Just run `python demo.py`
- **API docs:** http://localhost:8001/docs (when server running)
- **Need help?** Check `SETUP.md` troubleshooting section

---

## 🎉 Quick Win Checklist

Before your demo, run these 3 commands:

```bash
# 1. Install (once)
pip install -r requirements.txt

# 2. Verify
python demo.py --check

# 3. Test
python analyze_csv.py sample_weekly.csv
```

If all three work, you're ready! 🚀

---

**Questions?** See documentation:
- `QUICKSTART.md` - Fast start
- `SETUP.md` - Detailed guide  
- `IMPLEMENTATION_SUMMARY.md` - Complete overview

