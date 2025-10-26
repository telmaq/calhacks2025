# Creao Integration Guide

## 🎯 Quick Start - Connect Creao in 5 Minutes

### Step 1: Add Capture Button in Creao

In your Creao webapp, add this button:

```html
<button onclick="openCaptureWindow()" class="btn-primary">
  📸 Capture Produce Weight
</button>
```

### Step 2: Add JavaScript Handler

```javascript
function openCaptureWindow() {
  // Get current farmer ID from your app
  const farmerId = getCurrentFarmerId(); // Your function to get farmer

  // Open capture page in new tab
  const url = `https://your-api.com/test_weight_capture.html?farmer_id=${farmerId}`;

  const captureWindow = window.open(url, "_blank", "width=800,height=600");

  // Listen for capture data
  window.addEventListener("message", handleCaptureMessage);
}

function handleCaptureMessage(event) {
  // Security: Check origin
  if (event.origin !== "https://your-api.com") {
    return;
  }

  const data = event.data;

  if (data.type === "produce_captured") {
    const captureData = data.data;

    console.log("Received capture:", captureData);

    // Log to Creao database
    syncToCreaoDatabase(captureData);
  }
}

async function syncToCreaoDatabase(data) {
  try {
    // Send to your Creao backend
    const response = await fetch("/api/produce", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: data.name,
        price: data.price,
        unit: data.unit,
        seller_id: data.seller_id,
        external_id: data.id
      })
    });

    const result = await response.json();

    if (response.ok) {
      console.log("✅ Saved to Creao database:", result);

      // Show success notification
      showNotification("Produce captured successfully!");

      // Refresh produce list
      refreshProduceList();
    }
  } catch (error) {
    console.error("❌ Error syncing to Creao:", error);
    showNotification("Error saving produce", "error");
  }
}
```

### Step 3: Update Capture Page to Send Data Back

Update `test_weight_capture.html` to send data to Creao after capture:

```javascript
async function captureWeight() {
  // ... existing capture code ...

  const data = await response.json();

  if (response.ok) {
    // Send data back to Creao parent window
    if (window.opener) {
      window.opener.postMessage(
        {
          type: "produce_captured",
          data: data
        },
        "https://your-creao-domain.com"
      ); // Replace with actual Creao domain

      // Show success and close
      updateStatus(`✅ ${data.message}`, "success");
      setTimeout(() => window.close(), 2000);
    }
  }
}
```

## 🔄 Complete Flow

```
┌─────────────────┐
│   Creao App     │
│                 │
│ [Capture Button]│
└────────┬────────┘
         │ Click
         ▼
┌─────────────────────────────────┐
│  Opens: capture.html?           │
│  farmer_id=123                  │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Your Camera Service            │
│  - Opens camera                 │
│  - Captures image               │
│  - Sends to API                 │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Your API (app.py)              │
│  - Claude OCR → extracts weight │
│  - Saves to Supabase            │
│  - Returns JSON                 │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  postMessage back to Creao      │
│  with capture data              │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Creao Database                 │
│  - Logs produce                 │
│  - Shows in marketplace         │
└─────────────────────────────────┘
```

## 📋 Creao Backend Endpoint

Create this endpoint in your Creao backend:

```javascript
// POST /api/produce
app.post("/api/produce", async (req, res) => {
  const { name, price, unit, seller_id, external_id } = req.body;

  // Save to Creao database
  const produce = await db.produce.create({
    data: {
      name,
      price,
      unit,
      seller_id,
      external_id, // Reference to Supabase record
      status: "pending",
      created_at: new Date()
    }
  });

  res.json({
    success: true,
    produce_id: produce.id
  });
});
```

## 🔐 Security Considerations

### 1. Validate Origin in Creao

```javascript
window.addEventListener("message", function (event) {
  // Only accept messages from your API domain
  if (event.origin !== "https://your-api.com") {
    console.warn("Ignored message from unauthorized origin:", event.origin);
    return;
  }

  handleCaptureMessage(event);
});
```

### 2. Add CORS Headers in Your API

Already configured in `app.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-creao-domain.com"],  # Your Creao domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Authenticate API Requests

Optionally add API key authentication:

```python
@app.post("/api/v1/capture/weight")
async def capture_weight(
    request: WeightCaptureRequest,
    api_key: str = Header(None)
):
    if api_key != os.getenv("CREAO_API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    # ... rest of code ...
```

## 🧪 Testing Checklist

- [ ] Capture button opens new tab
- [ ] Camera loads in capture page
- [ ] Image capture works
- [ ] API returns weight data
- [ ] Data saved to Supabase
- [ ] `postMessage` sends data to Creao
- [ ] Creao receives data
- [ ] Creao saves to its database
- [ ] New listing appears in marketplace

## 🎯 Success Indicators

1. **User clicks button** → New tab opens
2. **User captures image** → Weight extracted
3. **Data saved to Supabase** → Visible in dashboard
4. **Creao receives data** → Logged in database
5. **Listing appears** → Farmer sees in marketplace

## 🚨 Troubleshooting

**Issue: Capture window doesn't open**

- Check popup blocker settings
- Use `window.open()` with permissions

**Issue: No data received in Creao**

- Check browser console for errors
- Verify `postMessage` origin matches
- Test API endpoint directly

**Issue: Data not saved to Creao**

- Check backend API logs
- Verify database connection
- Test endpoint with Postman/curl

## 📝 Example: Complete Implementation

See `test_weight_capture.html` for full implementation.

Key functions:

- `captureWeight()` - Main capture function
- `window.opener.postMessage()` - Send data to Creao
- Error handling and user feedback

---

## ✅ Ready to Integrate!

Follow these steps and your Creao app will be fully integrated with the capture service! 🚀
