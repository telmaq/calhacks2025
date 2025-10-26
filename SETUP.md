# 🚀 Gemini AI Analytics Setup Guide

Quick setup guide to get your Gemini-powered farm analytics system running for the hackathon demo.

---

## ⚡ Quick Start (5 minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your API key

### 3. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Gemini API key
nano .env  # or use your preferred editor
```

Your `.env` file should look like:
```
GEMINI_API_KEY=AIzaSy...your_actual_key_here
```

### 4. Test the Setup

```bash
# Run the demo script to verify everything works
python demo.py --check
```

---

## 📊 Usage Examples

### CSV Analytics (Command Line)

Analyze farm supply/sales data:

```bash
python analyze_csv.py sample_weekly.csv
```

Filter by specific crop:

```bash
python analyze_csv.py sample_weekly.csv tomato
```

### Image Analytics (Command Line)

Analyze crate/produce photos:

```bash
python analyze_image.py path/to/your/image.jpg
```

### API Server

Start the FastAPI server:

```bash
python app.py
```

The server will start at `http://localhost:8001`

**API Documentation:** http://localhost:8001/docs

### Full Demo

Run the complete hackathon demo:

```bash
python demo.py
```

Or run specific demos:

```bash
python demo.py --csv-only      # CSV analytics only
python demo.py --image-only    # Image analytics only
python demo.py --api-only      # API integration only
```

---

## 🔌 API Endpoints

### 1. CSV Analytics

```bash
POST http://localhost:8001/api/v1/analytics/csv
```

**Request Body:**
```json
{
  "farmer_id": "farmer123",
  "csv_data": "week_start,crop,total_supplied_kg,total_sold_kg\n2025-09-01,tomato,500,450",
  "crop_filter": "tomato"
}
```

**Response:**
```json
{
  "status": "success",
  "farmer_id": "farmer123",
  "analytics": {
    "insights": [
      {"title": "...", "explanation": "..."}
    ],
    "forecast": [
      {"week_start": "2025-10-01", "crop": "tomato", "kg": 610}
    ],
    "recommendations": ["...", "...", "..."]
  },
  "source": "gemini"
}
```

### 2. Image Analytics

```bash
POST http://localhost:8001/api/v1/analytics/image
```

**Request Body:**
```json
{
  "farmer_id": "farmer123",
  "image_base64": "<base64_encoded_image>",
  "produce_type": "tomatoes"
}
```

**Response:**
```json
{
  "status": "success",
  "farmer_id": "farmer123",
  "analytics": {
    "crate_count": 3,
    "estimated_total_weight_kg": 45.0,
    "per_crate_estimate_kg": 15.0,
    "quality_score": "good",
    "confidence": 0.85,
    "notes": "3 crates of ripe tomatoes visible"
  },
  "source": "gemini"
}
```

### 3. Analytics Status

Check if Gemini is configured:

```bash
GET http://localhost:8001/api/v1/analytics/status
```

---

## 🧪 Testing with cURL

### Test CSV Analytics

```bash
curl -X POST http://localhost:8001/api/v1/analytics/csv \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "farmer123",
    "csv_data": "week_start,crop,total_supplied_kg,total_sold_kg\n2025-09-01,tomato,500,450\n2025-09-08,tomato,520,480"
  }'
```

### Test Image Analytics

```bash
# First, encode an image to base64
base64 -i sample_image.jpg -o image.b64

# Then send to API (using the base64 string)
curl -X POST http://localhost:8001/api/v1/analytics/image \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "farmer123",
    "image_base64": "'$(cat image.b64)'"
  }'
```

---

## 📁 Project Structure

```
calhacks2025/
├── app.py                      # FastAPI backend with analytics endpoints
├── gemini_client.py           # Gemini API client initialization
├── analyze_csv.py             # CSV analytics module
├── analyze_image.py           # Image analytics module
├── demo.py                    # Hackathon demo script
├── sample_weekly.csv          # Sample farm data for testing
├── requirements.txt           # Python dependencies
├── .env                       # Environment variables (create from .env.example)
├── .env.example              # Environment template
└── SETUP.md                  # This file
```

---

## 🔧 Troubleshooting

### "Module not found" errors

```bash
pip install -r requirements.txt
```

### "API key not found" or authentication errors

1. Check that `.env` file exists and contains your API key
2. Verify the key is correct: `cat .env`
3. Try setting it directly in terminal:
   ```bash
   export GEMINI_API_KEY="your_key_here"
   python analyze_csv.py sample_weekly.csv
   ```

### Gemini API errors

- **Rate limit exceeded:** Wait a minute and try again, or upgrade your API plan
- **Invalid model:** Update `GEMINI_MODEL` in `.env` to a valid model name
- **Network errors:** Check your internet connection

### Mock Data Mode

If Gemini is unavailable, the API will automatically return mock data. You can still demo the flow:

```python
# Check status
curl http://localhost:8001/api/v1/analytics/status
```

If `gemini_configured` is `false`, the endpoints will return realistic mock data for your demo.

---

## 🎯 Hackathon Demo Flow

### Option 1: Command Line Demo

```bash
# 1. Show CSV data
cat sample_weekly.csv

# 2. Run analytics
python analyze_csv.py sample_weekly.csv

# 3. Show image analysis (if you have sample images)
python analyze_image.py sample_crates.jpg

# 4. Run full demo
python demo.py
```

### Option 2: API Demo

```bash
# Terminal 1: Start the server
python app.py

# Terminal 2: Test endpoints
curl http://localhost:8001/api/v1/analytics/status

# Open browser to see API docs
open http://localhost:8001/docs
```

### Option 3: Integrated Demo

```bash
# Run the complete demo script
python demo.py
```

This will:
- ✅ Check your setup
- 📊 Run CSV analytics
- 🖼️ Run image analytics (if images available)
- 🚀 Show API integration examples

---

## 🚀 Production Deployment Tips

### Environment Variables

For production, set these environment variables:

```bash
export GEMINI_API_KEY="your_production_key"
export API_KEY="your_secure_api_key_for_auth"
export GEMINI_MODEL="gemini-2.0-flash-exp"
```

### Rate Limiting

Consider adding rate limiting to your API endpoints for production:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
```

### Monitoring

- Track Gemini API usage and costs
- Monitor response times
- Log all analytics requests for debugging

### Caching

For repeated queries, consider caching Gemini responses:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_analytics(csv_hash):
    return analyze_csv(...)
```

---

## 📚 Additional Resources

- [Gemini API Documentation](https://ai.google.dev/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Sample CSV Format](./sample_weekly.csv)

---

## 🤝 Support

Having issues? Check:

1. ✅ Dependencies installed: `pip list | grep google-genai`
2. ✅ API key set: `echo $GEMINI_API_KEY`
3. ✅ Files present: `ls *.py`
4. ✅ Server running: `curl http://localhost:8001/health`

---

## 🎉 You're Ready!

Your Gemini AI analytics system is set up and ready for the hackathon demo. Good luck! 🚀

