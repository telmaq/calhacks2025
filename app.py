from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, Form, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import cv2
import numpy as np
import json
import base64
from typing import List, Optional
from ultralytics import YOLO
import easyocr
from pydantic import BaseModel
import re
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI(
    title="Smart Camera Service - Creao Integration",
    description="Computer vision service for capturing produce weight from scale images",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Security
security = HTTPBearer()
API_KEY = os.getenv("API_KEY", "your-secret-api-key-here")

# def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     """Verify API key for authentication"""
#     if credentials.credentials != API_KEY:
#         raise HTTPException(status_code=401, detail="Invalid API key")
#     return credentials.credentials

# Request model for weight capture
class WeightCaptureRequest(BaseModel):
    farmer_id: str
    produce_name: str
    image_base64: Optional[str] = None

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def send_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            self.disconnect(websocket)

manager = ConnectionManager()

# Load YOLOv8 model (will download on first run)
# Use smaller model to reduce memory footprint
model = None
reader = None

def get_model():
    global model
    if model is None:
        model = YOLO('yolov8n.pt')  # Downloads ~6MB model
    return model

def get_reader():
    global reader
    if reader is None:
        reader = easyocr.Reader(['en'])  # Downloads models on first use
    return reader

def extract_weight_from_scale(frame: np.ndarray) -> dict:
    """
    Extract weight from digital scale display using EasyOCR.
    """
    # Convert to grayscale for better OCR
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Run OCR
    reader = get_reader()
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
    print("No weight found")
    return {
        'weight': 0.0,
        'unit': 'kg',
        'confidence': 0.0,
        'error': 'No weight detected in image',
        'method': 'ocr'
    }
def detect_produce(frame: np.ndarray) -> dict:
    """Detect produce items using YOLOv8 object detection"""
    # Run YOLOv8 inference
    model = get_model()
    results = model(frame, conf=0.5)

    # Filter for produce-related classes (COCO dataset classes)
    produce_classes = {
        0: 'person',  # Sometimes farmers are in frame
        47: 'apple', 48: 'orange', 49: 'broccoli', 50: 'carrot',
        51: 'hot dog', 52: 'pizza', 53: 'donut', 54: 'cake',
        55: 'chair', 56: 'couch', 57: 'potted plant', 58: 'bed',
        59: 'dining table', 60: 'toilet', 61: 'tv', 62: 'laptop',
        63: 'mouse', 64: 'remote', 65: 'keyboard', 66: 'cell phone',
        67: 'microwave', 68: 'oven', 69: 'toaster', 70: 'sink',
        71: 'refrigerator', 72: 'book', 73: 'clock', 74: 'vase',
        75: 'scissors', 76: 'teddy bear', 77: 'hair drier', 78: 'toothbrush'
    }

    # Focus on food-related items that could be produce
    food_classes = [47, 48, 49, 50, 51, 52, 53, 54]  # apple, orange, broccoli, carrot, etc.

    annotated_frame = frame.copy()
    detected_objects = []

    for result in results:
        boxes = result.boxes
        if boxes is not None:
            for box in boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])

                # Only process food-related items
                if class_id in food_classes:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)

                    # Draw bounding box
                    cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    # Add label
                    label = f"{produce_classes.get(class_id, 'unknown')}: {confidence:.2f}"
                    cv2.putText(annotated_frame, label, (x1, y1 - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    detected_objects.append({
                        'class': produce_classes.get(class_id, 'unknown'),
                        'confidence': confidence,
                        'bbox': [int(x1), int(y1), int(x2), int(y2)]
                    })

    return annotated_frame, {
        'objects_detected': len(detected_objects),
        'detected_objects': detected_objects,
        'confidence': max([obj['confidence'] for obj in detected_objects], default=0.0)
    }

@app.post("/api/v1/capture/weight",
          summary="Capture Weight from Scale Image",
          description="Extract weight value from a digital scale image using computer vision and OCR",
          response_description="Weight data extracted from the image",
          tags=["Weight Capture"])
async def capture_weight(
    request: WeightCaptureRequest,
    # api_key: str = Depends(verify_api_key)
):
    # Debug logging
    print(f"🔍 Received request from Creao:")
    print(f"   - farmer_id: {request.farmer_id}")
    print(f"   - produce_name: {request.produce_name}")
    print(f"   - image_base64 length: {len(request.image_base64) if request.image_base64 else 0}")
    # print(f"   - API key: {api_key[:10]}...")
    """
    Capture weight from a scale image using computer vision and OCR.

    **Process:**
    1. Receives image and context (farmer_id, produce_name)
    2. Runs computer vision to detect the scale display
    3. Runs OCR to extract weight value and unit
    4. Validates the extracted data
    5. Returns structured weight data

    **Authentication:** Bearer token required

    **Example Request:**
    ```json
    {
        "farmer_id": "farmer123",
        "produce_name": "apples",
        "image_base64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ..."
    }
    ```

    **Example Response:**
    ```json
    {
        "status": "success",
        "farmer_id": "farmer123",
        "produce_name": "apples",
        "weight_data": {
            "weight": 5.2,
            "unit": "kg",
            "confidence": 0.96,
            "raw_text": "5.2 kg",
            "method": "ocr"
        },
        "message": "Weight 5.2 kg captured!",
        "creao_logged": false
    }
    ```
    """
    try:
        # Decode base64 image
        if not request.image_base64:
            return JSONResponse(
                status_code=400,
                content={"error": "image_base64 is required"}
            )

        image_data = base64.b64decode(request.image_base64)
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid image data"}
            )

        # Extract weight from scale
        weight_data = extract_weight_from_scale(frame)

        # Validate weight
        if weight_data['weight'] <= 0:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid weight value", "weight": weight_data['weight']}
            )

        # TODO: Log to Creao database
        # In production, make an API call to Creao here
        # creao_response = await log_to_creao({
        #     'farmer_id': request.farmer_id,
        #     'produce_name': request.produce_name,
        #     'weight': weight_data['weight'],
        #     'unit': weight_data['unit']
        # })

        return JSONResponse(content={
            "status": "success",
            "farmer_id": request.farmer_id,
            "produce_name": request.produce_name,
            "weight_data": weight_data,
            "message": f"Weight {weight_data['weight']} {weight_data['unit']} captured!",
            "creao_logged": False  # Set to True when Creao integration is complete
        })

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )

@app.websocket("/ws/stream")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "frame":
                # Decode base64 image
                image_data = base64.b64decode(message["data"])
                nparr = np.frombuffer(image_data, np.uint8)
                frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                if frame is not None:
                    annotated_frame, detection_result = detect_produce(frame)

                    # Encode annotated frame to base64
                    _, buffer = cv2.imencode('.jpg', annotated_frame)
                    annotated_base64 = base64.b64encode(buffer).decode('utf-8')

                    response = {
                        "type": "detection",
                        "timestamp": message.get("timestamp"),
                        "detection": detection_result,
                        "annotated_frame": annotated_base64
                    }

                    await manager.send_message(json.dumps(response), websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/",
         summary="API Status",
         description="Get the current status of the Smart Camera Service API",
         tags=["Health"])
async def root():
    """Get API status and version information"""
    return {
        "status": "Smart Camera Service API",
        "version": "1.0.0",
        "description": "Computer vision service for capturing produce weight from scale images",
        "endpoints": {
            "weight_capture": "/api/v1/capture/weight",
            "docs": "/docs",
            "health": "/health"
        }
    }

@app.get("/health",
         summary="Health Check",
         description="Check if the API service is running and healthy",
         tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0"
    }

@app.get("/webcam_client.html", response_class=HTMLResponse)
async def webcam_client():
    try:
        with open("webcam_client.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Webcam client not found</h1>", status_code=404)

@app.get("/test_weight_capture.html", response_class=HTMLResponse)
async def test_weight_capture():
    try:
        with open("test_weight_capture.html", "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Test client not found</h1>", status_code=404)

if __name__ == "__main__":
    import uvicorn
    print("Starting server on http://localhost:8001")
    print("\nAvailable endpoints:")
    print("  - http://localhost:8001/webcam_client.html (Produce detection demo)")
    print("  - http://localhost:8001/test_weight_capture.html (Weight capture test)")
    print("  - POST http://localhost:8001/api/v1/capture/weight (API endpoint)")
    print("  - WebSocket ws://localhost:8001/ws/stream (Real-time detection)")
    uvicorn.run(app, host="0.0.0.0", port=8001)
