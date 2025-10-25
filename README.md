# Smart Camera Service - Creao Integration

Computer vision service for capturing produce weight from scale images.

## 🚀 Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the server:

```bash
python app.py
```

3. Test the weight capture:

```
http://localhost:8001/test_weight_capture.html
```

## 📋 What It Does

- **Produce Detection**: Detects produce items (apples, oranges, broccoli, etc.) using YOLOv8
- **Weight Capture**: Extracts weight from scale images via OCR
- **Creao Integration**: Ready to log captured weights to your Creao database

## 🎯 Endpoints

### 1. Weight Capture API

```
POST http://localhost:8001/api/v1/capture/weight
```

**Request Body:**

```json
{
  "farmer_id": "farmer123",
  "produce_name": "apples",
  "image_base64": "<base64 encoded image>"
}
```

**Response:**

```json
{
  "status": "success",
  "farmer_id": "farmer123",
  "produce_name": "apples",
  "weight_data": {
    "weight": 5.2,
    "unit": "kg",
    "confidence": 0.95
  },
  "message": "Weight 5.2 kg captured!",
  "creao_logged": false
}
```

### 2. Real-time Produce Detection (WebSocket)

```
ws://localhost:8001/ws/stream
```

### 3. Test Clients

- `http://localhost:8001/test_weight_capture.html` - Weight capture test
- `http://localhost:8001/webcam_client.html` - Produce detection demo

## 🔧 Next Steps for Creao Integration

### Phase 1: Complete OCR Implementation (Current Step)

- [ ] Install EasyOCR or Tesseract
- [ ] Implement actual OCR for scale display
- [ ] Add scale display detection using edge detection

### Phase 2: Creao API Integration

- [ ] Get Creao API endpoint documentation
- [ ] Implement `log_to_creao()` function
- [ ] Add authentication (API key/token)
- [ ] Test data flow: Camera → API → Creao DB

### Phase 3: Mobile Integration

- [ ] Add "Capture Weight" button to Creao mobile app
- [ ] Implement camera capture on mobile
- [ ] Add real-time feedback to farmer

## 📁 Files

- `app.py` - FastAPI server with weight capture endpoint
- `test_weight_capture.html` - Weight capture test client
- `webcam_client.html` - Produce detection demo
- `requirements.txt` - Python dependencies
