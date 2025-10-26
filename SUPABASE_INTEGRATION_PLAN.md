# Supabase + Creao Dual-Database Integration Plan

## 🎯 Goal

Connect this service to Supabase database because Creao webapp doesn't support webcam/camera access. When farmer clicks a button in Creao, it triggers your API which:

1. Processes the image (Claude AI extracts weight)
2. Writes to Supabase produce table
3. Returns JSON response to Creao so it can populate its own database
4. Keeps both databases in sync

---

## 📐 Architecture Overview

```
┌─────────────────┐
│   Creao Webapp  │
│   (farmer UI)   │
└────────┬────────┘
         │
         │ 1. Click button
         │    with farmerId
         ▼
┌─────────────────────────────────────┐
│         Your API Service            │
│     (Python FastAPI + Claude)       │
│                                     │
│  - Receive farmerId as parameter    │
│  - Camera/image capture (if needed) │
│  - Image processing (Claude OCR)    │
│  - Extract: weight, produce name    │
│                                     │
├─────────────────────────────────────┤
│         Data Flow:                  │
│  1. Write to Supabase               │
│  2. Return JSON to Creao            │
└────────┬────────────────────┬───────┘
         │                    │
         │ 2a.                 │ 2b.
         ▼                    ▼
┌─────────────────┐    ┌─────────────────┐
│   Supabase DB   │    │   Creao API     │
│  (source of     │    │   (receives     │
│   truth)        │    │    JSON, logs   │
│                 │    │    to own DB)   │
└─────────────────┘    └─────────────────┘
```

---

## 🔧 Step-by-Step Implementation

### Step 1: Create Supabase Produce Table

First, set up the database schema in Supabase.

**Table: `produce`**

```sql
CREATE TABLE produce (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farmer_id TEXT NOT NULL,
    produce_name TEXT NOT NULL,
    weight DECIMAL(10, 2) NOT NULL,
    unit TEXT NOT NULL,  -- 'g', 'kg', 'lb', 'oz'
    weight_confidence DECIMAL(3, 2),  -- 0.00 to 1.00
    image_url TEXT,  -- URL to the captured image
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    creao_logged BOOLEAN DEFAULT FALSE,  -- Track if synced to Creao
);

-- Index for faster queries
CREATE INDEX idx_produce_farmer_id ON produce(farmer_id);
CREATE INDEX idx_produce_created_at ON produce(created_at DESC);
```

### Step 2: Set Up Supabase Python Client

Install Supabase library:

```bash
pip install supabase
```

Add to `requirements.txt`:

```
supabase
```

### Step 3: Add Environment Variables

Create `.env` file (if not exists) or update Railway config:

```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-or-service-role-key

# Existing variables
CLAUDE_API_KEY=your-claude-key
API_KEY=your-api-key
```

### Step 4: Modify API Endpoint

Update `POST /api/v1/capture/weight` to:

1. Accept `farmer_id` as required parameter
2. Handle camera capture (if Creao sends image) OR process uploaded image
3. Extract weight using Claude
4. Write to Supabase `produce` table
5. Return JSON response to Creao

**Updated Request Model:**

```python
class WeightCaptureRequest(BaseModel):
    farmer_id: str  # REQUIRED: Farmer ID from Creao
    produce_name: Optional[str] = None  # Optional: Let Claude detect if not provided
    image_base64: Optional[str] = None  # Image from camera
    image_url: Optional[str] = None  # Or image URL
```

**New API Response:**

```json
{
  "status": "success",
  "farmer_id": "farmer123",
  "produce": {
    "name": "apples",
    "weight": 5.2,
    "unit": "kg",
    "confidence": 0.96
  },
  "supabase_id": "uuid-here",
  "message": "Produce captured and logged to database",
  "synced_to_creao": false // Will be true after Creao receives this
}
```

### Step 5: Write to Supabase Function

Add new function to `app.py`:

```python
from supabase import create_client, Client
import os

# Initialize Supabase client
supabase: Client = None

def init_supabase():
    global supabase
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if supabase_url and supabase_key:
        supabase = create_client(supabase_url, supabase_key)
        print("✅ Supabase client initialized")
    else:
        print("⚠️  Supabase credentials not found")

async def write_to_supabase(data: dict) -> dict:
    """
    Write produce data to Supabase produce table.

    Args:
        data: Dictionary with farmer_id, produce_name, weight, unit, etc.

    Returns:
        Dictionary with insert result and record ID
    """
    if not supabase:
        raise Exception("Supabase client not initialized")

    try:
        # Prepare data for Supabase
        record = {
            "farmer_id": data["farmer_id"],
            "produce_name": data["produce_name"],
            "weight": data["weight"],
            "unit": data["unit"],
            "weight_confidence": data.get("confidence", 0.0),
            "image_url": data.get("image_url"),
            "creao_logged": False
        }

        # Insert into Supabase
        result = supabase.table("produce").insert(record).execute()

        # Return the inserted record
        return {
            "success": True,
            "id": result.data[0]["id"],
            "record": result.data[0]
        }

    except Exception as e:
        print(f"❌ Error writing to Supabase: {e}")
        raise
```

### Step 6: Update Main Endpoint

Modify the `capture_weight()` function to call Supabase write:

```python
@app.post("/api/v1/capture/weight")
async def capture_weight(request: WeightCaptureRequest):
    try:
        # 1. Process image (existing logic)
        # ... image processing code ...

        # 2. Extract weight using Claude
        weight_data = await extract_weight_from_scale(frame)

        # 3. Determine produce name (from request or let Claude detect)
        produce_name = request.produce_name
        if not produce_name:
            # TODO: Add Claude vision to detect produce type
            produce_name = "unknown"

        # 4. Write to Supabase
        supabase_result = await write_to_supabase({
            "farmer_id": request.farmer_id,
            "produce_name": produce_name,
            "weight": weight_data['weight'],
            "unit": weight_data['unit'],
            "confidence": weight_data['confidence'],
            "image_url": None  # TODO: Upload image to Supabase storage
        })

        # 5. Return JSON to Creao
        return JSONResponse(content={
            "status": "success",
            "farmer_id": request.farmer_id,
            "produce": {
                "name": produce_name,
                "weight": weight_data['weight'],
                "unit": weight_data['unit'],
                "confidence": weight_data['confidence']
            },
            "supabase_id": supabase_result["id"],
            "message": "Produce captured and logged to database",
            "synced_to_creao": False  # Creao will set this to True when it receives
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
```

---

## 🔄 Keeping Databases in Sync

### Strategy 1: Supabase as Source of Truth (Recommended)

- **Supabase**: Primary database (all scanned produce)
- **Creao**: Receives JSON response, logs to its own DB
- **Sync Method**: Creao uses the JSON response to populate its table

**Creao Side (pseudo-code):**

```javascript
// In Creao webapp
async function captureProduce(farmerId) {
  // 1. Call your API
  const response = await fetch("https://your-api.com/api/v1/capture/weight", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ farmer_id: farmerId })
  });

  const data = await response.json();

  // 2. Log to Creao database
  await fetch("https://creao-api.com/api/produce", {
    method: "POST",
    body: JSON.stringify({
      name: data.produce.name,
      weight: data.produce.weight,
      unit: data.produce.unit,
      farmer_id: farmerId,
      external_id: data.supabase_id // Reference to Supabase
    })
  });

  // 3. Update Supabase record (mark as synced to Creao)
  await fetch("https://your-api.com/api/v1/mark-synced/" + data.supabase_id, {
    method: "PATCH"
  });

  return data;
}
```

### Strategy 2: Webhook from Supabase to Creao

Set up Supabase Edge Function (or external webhook) to notify Creao when new produce is added.

---

## 🧪 Testing Steps

### 1. Test Supabase Connection

Create test file `test_supabase.py`:

```python
from supabase import create_client
import os

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

# Test insert
result = supabase.table("produce").insert({
    "farmer_id": "test123",
    "produce_name": "apples",
    "weight": 5.0,
    "unit": "kg",
    "weight_confidence": 0.95
}).execute()

print(result)
```

### 2. Test Full Flow

1. Start your API: `python app.py`
2. Use test client: `http://localhost:8000/test_weight_capture.html`
3. Enter farmer ID and capture image
4. Check Supabase dashboard for new record
5. Verify response JSON contains all data

### 3. Test Creao Integration

Create a test Creao webapp page that:

- Has a button to capture produce
- Calls your API endpoint
- Logs the response to console
- Displays success message

---

## 📊 Data Flow Example

**Farmer's Perspective:**

1. Opens Creao app
2. Clicks "Add Produce" button
3. Camera opens (via your API endpoint)
4. Captures image of scale
5. Sees "5.2 kg apples captured!"
6. New listing appears in marketplace

**Backend Flow:**

1. Creao sends POST to `/api/v1/capture/weight` with `farmer_id`
2. API receives request, processes image
3. Claude extracts weight: `{"weight": 5.2, "unit": "kg"}`
4. API writes to Supabase: `produce` table
5. API returns JSON to Creao
6. Creao logs to its own database
7. Both databases have the record ✅

---

## 🚨 Important Considerations

### 1. Error Handling

- What if Supabase write fails?
- What if Creao receives response but fails to log?
- How to handle duplicate requests?

**Solution**: Implement idempotency keys in requests.

### 2. Image Storage

Currently, images are only in memory. You may want to:

- Store images in Supabase Storage
- Store image URL in `produce` table
- Or skip storing images to reduce database size

### 3. Authentication

Add API key authentication to prevent abuse:

```python
@app.post("/api/v1/capture/weight")
async def capture_weight(
    request: WeightCaptureRequest,
    api_key: str = Header(None)
):
    # Verify API key
    if api_key != os.getenv("CREAO_API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    # ... rest of code ...
```

### 4. Rate Limiting

Add rate limiting to prevent spam:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/v1/capture/weight")
@limiter.limit("10/minute")  # 10 requests per minute per IP
async def capture_weight(request: WeightCaptureRequest):
    # ... code ...
```

---

## 📝 Next Steps Summary

1. ✅ Create Supabase produce table (SQL above)
2. ✅ Install supabase Python library
3. ✅ Add environment variables for Supabase
4. ✅ Implement `write_to_supabase()` function
5. ✅ Update `/api/v1/capture/weight` endpoint
6. ✅ Test full flow
7. ✅ Implement Creao webapp integration
8. ✅ Add authentication and rate limiting

---

## 🆘 Troubleshooting

**Q: Supabase write fails?**

- Check credentials in `.env`
- Verify table exists
- Check RLS (Row Level Security) policies

**Q: Creao doesn't receive response?**

- Check network/HTTPS
- Verify CORS settings
- Check API endpoint URL

**Q: Duplicate records?**

- Add unique constraint on `(farmer_id, created_at)` in Supabase
- Implement request deduplication

Let me know if you need help implementing any specific step! 🚀
