# ⚡ Quick Start - 3 Steps to Demo

## 1️⃣ Install (2 minutes)

```bash
pip install -r requirements.txt
```

## 2️⃣ Configure (1 minute)

Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

```bash
cp .env.example .env
# Edit .env and add: GEMINI_API_KEY=your_key_here
```

## 3️⃣ Test (1 minute)

```bash
# Option A: Run full demo
python demo.py

# Option B: Test individual features
python analyze_csv.py sample_weekly.csv
python demo.py --check
```

---

## 🎯 For Your Hackathon Demo

### Show CSV Analytics

```bash
python analyze_csv.py sample_weekly.csv
```

This will display:
- ✅ Top 3 insights about farm data
- ✅ 2-week supply forecast
- ✅ 3 actionable recommendations

### Start API Server

```bash
python app.py
```

Then visit: http://localhost:8001/docs

### Test API Endpoints

```bash
python test_api.py
```

---

## 📊 API Endpoints You Can Demo

1. **CSV Analytics**: `POST /api/v1/analytics/csv`
2. **Image Analytics**: `POST /api/v1/analytics/image`
3. **Status Check**: `GET /api/v1/analytics/status`

Interactive docs: http://localhost:8001/docs

---

## 🚨 If Something Breaks

**No Gemini API Key?**
→ The system will use mock data automatically. Your demo still works!

**Dependencies missing?**
```bash
pip install google-genai pandas requests
```

**Server won't start?**
```bash
# Check if port 8001 is available
lsof -ti:8001 | xargs kill -9  # Kill any process on that port
python app.py
```

---

## 🎬 Demo Script

1. **Show the problem**: "Farmers need insights from their supply data"
2. **Show sample data**: `cat sample_weekly.csv`
3. **Run AI analysis**: `python analyze_csv.py sample_weekly.csv`
4. **Show results**: Point out insights, forecast, recommendations
5. **Show API**: Open http://localhost:8001/docs and run a request
6. **Show integration**: Explain how it connects to your full app

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `demo.py` | Complete hackathon demo script |
| `analyze_csv.py` | CSV analytics (command line) |
| `analyze_image.py` | Image analytics (command line) |
| `app.py` | FastAPI server with all endpoints |
| `test_api.py` | API test suite |
| `sample_weekly.csv` | Sample farm data |

---

## 💡 Pro Tips

- **No real data?** Use `sample_weekly.csv` - it looks realistic!
- **No images?** CSV analytics alone is impressive enough
- **API key issues?** Demo with mock data - it's already built in
- **Time pressure?** Just run `python demo.py` - it does everything
`
---

**You're ready! 🚀 Good luck with your demo!**

