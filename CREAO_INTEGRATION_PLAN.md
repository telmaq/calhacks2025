# Creao Integration Plan

## ✅ Current Status

### What's Working Now

- ✅ Produce detection using YOLOv8 (apples, oranges, broccoli, etc.)
- ✅ POST `/api/v1/capture/weight` endpoint created
- ✅ Weight capture test client (`test_weight_capture.html`)
- ✅ WebSocket real-time detection
- ✅ Mock weight extraction (returns random values for testing)

### What Needs to Be Done

---

## 📍 NEXT STEP: Implement Real OCR (Phase 1 - Step 3)

### Why This is Next

Right now, the `extract_weight_from_scale()` function returns mock data. We need to implement real OCR to extract actual weight values from digital scale displays.

### Action Plan: Add EasyOCR

#### 1. Install EasyOCR

```bash
# Activate your virtual environment first
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Install EasyOCR
pip install easyocr
```

#### 2. Update the OCR Function

In `app.py`, replace the `extract_weight_from_scale()` function with:

```python
import easyocr

# Initialize EasyOCR reader (only once, at module level)
reader = easyocr.Reader(['en'])  # Initialize once

def extract_weight_from_scale(frame: np.ndarray) -> dict:
    """
    Extract weight from digital scale display using EasyOCR.
    """
    # Convert to grayscale for better OCR
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Run OCR
    results = reader.readtext(gray)

    # Look for weight pattern (e.g., "5.2 kg" or "1.5kg")
    import re
    weight_pattern = r'(\d+\.?\d*)\s*(kg|lb|g|oz)?'

    for (bbox, text, confidence) in results:
        # Try to match weight pattern
        match = re.search(weight_pattern, text, re.IGNORECASE)
        if match:
            weight = float(match.group(1))
            unit = match.group(2) if match.group(2) else 'kg'

            return {
                'weight': weight,
                'unit': unit.lower(),
                'confidence': confidence,
                'raw_text': text,
                'method': 'ocr'
            }

    # No weight found
    return {
        'weight': 0.0,
        'unit': 'kg',
        'confidence': 0.0,
        'error': 'No weight detected in image',
        'method': 'ocr'
    }
```

#### 3. Test the OCR

Run your server and test with the test client:

```bash
python app.py
# Open http://localhost:8001/test_weight_capture.html
# Point camera at a digital scale display and click "Capture Weight"
```

### Expected Outcome

- OCR reads actual numbers from scale displays
- Weight values are extracted correctly
- Confidence scores reflect OCR accuracy

---

## 🔄 After OCR Works: Creao API Integration (Phase 2)

### Prerequisites

- Get your Creao API endpoint documentation
- Obtain API authentication token/key
- Understand the data format Creao expects

### Implementation Steps

#### 1. Create Creao Logging Function

Add to `app.py`:

```python
import httpx  # Add to requirements.txt: pip install httpx

async def log_to_creao(data: dict) -> dict:
    """
    Log weight data to Creao database.
    """
    creao_endpoint = "YOUR_CREAO_API_ENDPOINT"  # TODO: Replace with actual endpoint
    api_token = "YOUR_API_TOKEN"  # TODO: Replace with actual token

    payload = {
        "farmer_id": data['farmer_id'],
        "produce_name": data['produce_name'],
        "weight": data['weight'],
        "unit": data['unit'],
        "timestamp": datetime.now().isoformat()
    }

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            creao_endpoint,
            json=payload,
            headers=headers,
            timeout=10.0
        )
        response.raise_for_status()
        return response.json()
```

#### 2. Update the Weight Capture Endpoint

In the `capture_weight()` function, uncomment and update the Creao logging:

```python
# Log to Creao database
try:
    creao_response = await log_to_creao({
        'farmer_id': request.farmer_id,
        'produce_name': request.produce_name,
        'weight': weight_data['weight'],
        'unit': weight_data['unit']
    })

    return JSONResponse(content={
        "status": "success",
        "farmer_id": request.farmer_id,
        "produce_name": request.produce_name,
        "weight_data": weight_data,
        "message": f"Weight {weight_data['weight']} {weight_data['unit']} captured and logged!",
        "creao_logged": True,
        "creao_response": creao_response
    })
except Exception as e:
    # Log error but still return success
    print(f"Creao logging failed: {e}")
    return JSONResponse(content={
        "status": "success",
        "farmer_id": request.farmer_id,
        "produce_name": request.produce_name,
        "weight_data": weight_data,
        "message": f"Weight {weight_data['weight']} {weight_data['unit']} captured!",
        "creao_logged": False,
        "error": str(e)
    })
```

---

## 📱 Phase 3: Mobile Integration

### Mobile App Changes Needed

1. **Update Listing UI**

   - Replace manual weight input with "Capture Weight" button
   - Store `farmer_id` and `produce_name` context

2. **Camera Integration**

   - Use camera API on mobile device
   - Capture image when button is pressed
   - Send image + context to your API

3. **Real-time Feedback**
   - Display "Capturing..." while processing
   - Show success message: "Weight 5.2 kg captured!"
   - Refresh listing to show new data

### Example Mobile Code (Pseudo-code)

```javascript
async function captureWeight() {
  // 1. Get context
  const farmerId = getCurrentFarmerId();
  const produceName = getCurrentProduceName();

  // 2. Capture image
  const imageBlob = await captureCameraImage();
  const base64 = await blobToBase64(imageBlob);

  // 3. Send to your API
  const response = await fetch("https://your-api.com/api/v1/capture/weight", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      farmer_id: farmerId,
      produce_name: produceName,
      image_base64: base64
    })
  });

  // 4. Show feedback
  const result = await response.json();
  showMessage(result.message);

  // 5. Refresh UI (if Creao logged the data)
  if (result.creao_logged) {
    refreshListing();
  }
}
```

---

## 🚀 Deployment (Phase 4)

### Deploy Your API Service

1. **Choose Platform**

   - AWS (EC2, Lambda, or Elastic Beanstalk)
   - Google Cloud (Cloud Run or App Engine)
   - Azure (App Service or Functions)
   - Railway, Render, or Fly.io (easiest)

2. **Environment Variables**

   ```
   CREAO_API_ENDPOINT=https://your-creao-app.com/api/listings
   CREAO_API_TOKEN=your_secret_token
   ```

3. **Security**
   - Enable HTTPS (SSL)
   - Add API key authentication
   - Rate limiting
   - CORS configuration

### Example Deployment (Railway)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize project
railway init

# 4. Deploy
railway up
```

---

## 📊 Progress Checklist

### Phase 1: Core Logic ✅ IN PROGRESS

- [x] Create `/api/v1/capture/weight` endpoint
- [ ] Implement real OCR (EasyOCR or Tesseract)
- [ ] Test with actual scale images
- [ ] Validate weight data

### Phase 2: Creao Integration ⏳ NEXT

- [ ] Get Creao API documentation
- [ ] Implement `log_to_creao()` function
- [ ] Add authentication
- [ ] Test data flow end-to-end

### Phase 3: Mobile Integration ⏳ PENDING

- [ ] Update Creao mobile UI
- [ ] Add camera capture button
- [ ] Implement image capture + API call
- [ ] Add real-time feedback

### Phase 4: Deployment ⏳ FUTURE

- [ ] Deploy API to cloud
- [ ] Configure SSL/HTTPS
- [ ] Add API security (keys, rate limiting)
- [ ] Monitor and log errors

---

## 🆘 Need Help?

### Common Issues

1. **OCR not detecting text**

   - Ensure good lighting
   - Camera is in focus
   - Display is clearly visible
   - Try different OCR libraries

2. **Creao API authentication fails**

   - Check API token is correct
   - Verify endpoint URL
   - Check network connectivity

3. **Mobile camera not working**
   - Check browser permissions
   - Use HTTPS (required for camera on most browsers)
   - Test on real device, not just emulator

### Debug Endpoints

Test your API locally:

```bash
# Start server
python app.py

# Test with curl
curl -X POST http://localhost:8001/api/v1/capture/weight \
  -H "Content-Type: application/json" \
  -d '{"farmer_id":"test","produce_name":"apples","image_base64":"..."}'
```

---

## 🎯 Success Criteria

You'll know integration is complete when:

1. ✅ Camera captures scale image
2. ✅ OCR extracts weight correctly
3. ✅ API returns valid weight data
4. ✅ Data is logged to Creao database
5. ✅ Farmer sees confirmation in Creao app
6. ✅ New listing appears in Creao marketplace

Good luck! 🚀
