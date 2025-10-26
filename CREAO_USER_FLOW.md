# Creao Integration - Complete User Flow

## 🎯 Overview

When farmer clicks a button in Creao, it opens your service in a new tab to handle camera capture (since Creao doesn't support webcam). Here's the complete flow:

---

## 📱 Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: Creao Webapp                                           │
│                                                                  │
│  Farmer clicks "Capture Produce" button                         │
│  └─▶ Opens new tab: your-service.com/test_weight_capture.html  │
│      ?farmer_id=farmer123&auto_capture=true │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: Your Camera Service (New Tab)                          │
│                                                                  │
│  1. Page loads with farmerId from URL                           │
│  2. Camera automatically starts                                 │
│  3. Shows countdown: "Auto-capturing in 3 seconds..."           │
│  4. At 0: Captures image from camera                            │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: Your API Processing                                    │
│                                                                  │
│  POST /api/v1/capture/weight                                    │
│  {                                                                │
│    farmer_id: "farmer123",                                       │
│  }                                                                │
│                                                                  │
│  Processing:                                                     │
│  1. Capture image                                                 │
│  2. Send to image to claude ai
│  3. Extract weight: 5.2 kg                                       │
│  4. Write to Supabase produce table                             │
│  5. Return JSON response                                         │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: Success Response                                       │
│                                                                  │
│  Response JSON:                                                 │
│  {                                                                │
│    status: "success",                                           │
│    farmer_id: "farmer123",                                      │
│    produce: {                                                    │
│      name: "apples",                                             │
│      weight: 5.2,                                                │
│      unit: "kg",                                                 │
│      confidence: 0.96                                            │
│    },                                                             │
│    supabase_id: "uuid-123",                                     │
│    message: "Produce captured and logged to database"           │
│  }                                                                │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: Display Success & Close Tab                            │
│                                                                  │
│  - Shows success message: "✅ 5.2 kg apples captured!"          │
│  - Shows countdown: "Closing in 2 seconds..."                   │
│  - Automatically closes tab                                      │
│  - (Optional) Redirect back to Creao with data                  │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: Creao Syncs Data                                       │
│                                                                  │
│  Creao receives data via one of:                                │
│  1. Window.postMessage() from your service                       │
│  2. Webhook/callback URL                                        │
│  3. Polling Supabase for new records                            │
│                                                                  │
│  Creao logs to its own database:                                │
│  - Produce name: apples                                          │
│  - Weight: 5.2 kg                                                │
│  - Farmer: farmer123                                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Implementation: How to Set It Up

### 1. Creao Button Click Handler

In your Creao webapp, add this button:

```html
<button onclick="openCaptureWindow()">Capture Produce</button>

<script>
  function openCaptureWindow() {
    const farmerId = getCurrentFarmerId(); // Your function to get farmer ID
    const produceName = getCurrentProduceName(); // Or leave empty for auto-detection

    const url = `https://your-service.com/test_weight_capture.html?farmer_id=${farmerId}&auto_capture=true`;

    // Open in new tab
    const newWindow = window.open(url, "_blank", "width=800,height=600");

    // Listen for messages from the capture service
    window.addEventListener("message", function (event) {
      if (event.origin === "https://your-service.com") {
        const data = event.data;
        console.log("Received capture data:", data);

        // Log to Creao database
        syncToCreaoDatabase(data);
      }
    });
  }

  async function syncToCreaoDatabase(data) {
    // Send data to your Creao backend
    await fetch("/api/produce", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: data.produce.name,
        weight: data.produce.weight,
        unit: data.produce.unit,
        farmer_id: data.farmer_id,
        external_id: data.supabase_id
      })
    });

    console.log("Data synced to Creao database");
  }
</script>
```

### 2. Your Service Sends Data Back to Creao

Update your `captureWeight()` function in `test_weight_capture.html`:

```javascript
async function captureWeight() {
  // ... existing capture code ...

  const data = await response.json();

  if (response.ok) {
    updateStatus(`✅ ${data.message}`, "success");

    // Send data back to Creao (parent window)
    if (window.opener) {
      window.opener.postMessage(
        {
          type: "produce_captured",
          data: data
        },
        "*"
      ); // In production, specify your Creao domain
    }

    // Or redirect to success page
    setTimeout(() => {
      window.location.href = `/capture_success.html?produce_name=${data.produce.name}&weight=${data.produce.weight}&unit=${data.produce.unit}&farmer_id=${data.farmer_id}`;
    }, 2000);
  }
}
```

---

## 📋 Complete Flow Summary

### From User's Perspective:

1. **Click button in Creao** → New tab opens
2. **See camera** → Camera feed appears
3. **Wait 5 seconds** → Auto-capture happens
4. **See success** → "5.2 kg apples captured!"
5. **Tab closes** → Automatically after 3 seconds
6. **Back in Creao** → New listing appears in marketplace

### From Technical Perspective:

1. **Creao** → Opens URL with `farmer_id` parameter
2. **Your Service** → Reads `farmer_id` from URL
3. **Your Service** → Captures camera image
4. **Your API** → Processes image with Claude AI
5. **Your API** → Extracts weight (5.2 kg)
6. **Your API** → Writes to Supabase
7. **Your API** → Returns JSON response
8. **Your Service** → Sends data to Creao via `postMessage()`
9. **Creao** → Receives data and logs to its database
10. **Both databases synced** ✅

---

## 🎯 What Happens on Each Step

### Step 1: Button Click in Creao

```javascript
// Creao: Button handler
button.onclick = () => {
  window.open(
    `https://your-api.com/test_weight_capture.html?farmer_id=${userId}&auto_capture=true`
  );
};
```

### Step 2: Camera Opens & Auto-Captures

```javascript
// Your service: Reads URL params
const params = new URLSearchParams(window.location.search);
const farmerId = params.get("farmer_id"); // farmer123

// Auto-captures after 5 seconds
if (params.get("auto_capture") === "true") {
  setTimeout(captureWeight, 5000);
}
```

### Step 3: API Processes & Saves

```python
# Your API: app.py
@app.post("/api/v1/capture/weight")
async def capture_weight(request: WeightCaptureRequest):
    # 1. Process image
    weight = await extract_weight_from_scale(image)

    # 2. Save to Supabase
    supabase_id = await write_to_supabase({
        'farmer_id': request.farmer_id,
        'produce_name': request.produce_name,
        'weight': weight['weight'],
        'unit': weight['unit']
    })

    # 3. Return to frontend
    return {
        'status': 'success',
        'farmer_id': request.farmer_id,
        'produce': {...},
        'supabase_id': supabase_id
    }
```

### Step 4: Data Sent Back to Creao

```javascript
// Your service: Sends to Creao
window.opener.postMessage(
  {
    type: "produce_captured",
    data: apiResponse
  },
  "*"
);

// Creao: Receives data
window.addEventListener("message", (event) => {
  const data = event.data;
  // Log to Creao database
  syncToCreaoDatabase(data);
});
```

---

## ✅ One-Click Solution

**The key insight**: With URL parameters + auto-capture, the user experience is:

1. **Click button in Creao** (1 click)
2. **Wait 5 seconds** (camera auto-captures)
3. **Done!** (tab auto-closes)

The farmer only clicks once in Creao, and everything else happens automatically! 🎉

---

## 🔐 Security Considerations

1. **Validate `farmer_id`** - Make sure it's a valid farmer
2. **CORS** - Set proper CORS headers for Creao domain
3. **postMessage origin** - Validate origin in Creao's message listener
4. **API authentication** - Add API key if calling from Creao

---

## 🧪 Testing

Test the complete flow:

1. Start your service: `python app.py`
2. Open Creao page with button
3. Click button → Opens your capture page
4. Watch auto-capture happen
5. Check Supabase for new record
6. Verify Creao received data

---

Let me know if this flow makes sense or if you need any clarifications! 🚀
