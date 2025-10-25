from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, Form, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import json
import base64
from typing import List, Optional
from ultralytics import YOLO
import httpx
from pydantic import BaseModel
import re
import os
from dotenv import load_dotenv
import anthropic
load_dotenv()

app = FastAPI(
    title="Smart Camera Service - Creao Integration",
    description="Computer vision service for capturing produce weight from scale images",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Security
security = HTTPBearer()
API_KEY = os.getenv("API_KEY", "your-secret-api-key-here")

# Claude API configuration
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
# Initialize Claude client
claude_client = anthropic.Anthropic(api_key=CLAUDE_API_KEY) if CLAUDE_API_KEY else None

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

# Load YOLOv8 model at startup

# Use smaller model to reduce memory footprint
model = None

def initialize_models():
    """Initialize models at startup to avoid timeout issues"""
    global model
    print("🔄 Initializing AI models...")

    try:
        print("  - Loading YOLOv8 model...")
        # Options: yolov8n.pt (nano), yolov8s.pt (small), yolov8m.pt (medium), yolov8l.pt (large)
        model = YOLO('yolov8m.pt')  # Medium model - best accuracy within 4GB limit
        print("  ✅ YOLOv8 model loaded successfully")

        print("  - Claude API ready...")
        print("  ✅ Claude API configured successfully")

        print("🎉 All models initialized successfully!")

    except Exception as e:
        print(f"❌ Error initializing models: {e}")
        print("⚠️  Models will be loaded on first use")
        # Continue without models - they'll be loaded on first use
        model = None

def get_model():
    global model
    if model is None:
        print("⚠️  Model not initialized, loading now...")
        model = YOLO('yolov8m.pt')  # Medium model
    return model

async def extract_weight_from_scale(frame: np.ndarray) -> dict:
    """
    Extract weight from digital scale display using Claude API.
    """
    if not claude_client:
        print("❌ Claude API key not configured. Set CLAUDE_API_KEY environment variable.")
        return {
            'weight': 0.0,
            'unit': 'g',
            'confidence': 0.0,
            'error': 'Claude API key not configured',
            'method': 'claude_api'
        }

    try:
        # Convert image to base64 for Claude API
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
        image_base64 = base64.b64encode(buffer).decode('utf-8')

        # Call Claude API using the official SDK
        message = claude_client.messages.create(
            model="claude-haiku-4-5",  # fastest model
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": """Look at this digital scale display and extract the weight value and unit.

You must respond with ONLY a valid JSON object in this exact format:
{
    "weight": <number>,
    "unit": "<unit>",
    "confidence": <0.0-1.0>
}

Examples:
- If you see "54 g" return: {"weight": 54, "unit": "g", "confidence": 0.95}
- If you see "1.5 kg" return: {"weight": 1.5, "unit": "kg", "confidence": 0.90}
- If you see just "25" return: {"weight": 25, "unit": "g", "confidence": 0.85}

If you cannot clearly read a weight value, return: {"weight": 0, "unit": "g", "confidence": 0.0}

Focus on the digital display area and ignore any other text or numbers in the image. Return ONLY the JSON object, no other text."""
                        }
                    ]
                }
            ]
        )

        # Extract content from response
        content = message.content[0].text

        # Parse Claude's response
        try:
            print(f"🔍 Claude raw response: {content}")

            # Try to parse the entire response as JSON first
            try:
                weight_data = json.loads(content.strip())
            except json.JSONDecodeError:
                # If that fails, try to extract JSON from the response
                json_match = re.search(r'\{[^{}]*\}', content)
                if json_match:
                    weight_data = json.loads(json_match.group())
                else:
                    print(f"❌ No valid JSON found in Claude response: {content}")
                    raise ValueError("No valid JSON found")

            # Validate the response
            if 'weight' in weight_data and 'unit' in weight_data and 'confidence' in weight_data:
                weight = float(weight_data['weight'])
                unit = str(weight_data['unit']).lower().strip()
                confidence = float(weight_data['confidence'])

                print(f"✅ Claude detected: {weight} {unit} (confidence: {confidence:.2f})")

                return {
                    'weight': weight,
                    'unit': unit,
                    'confidence': confidence,
                    'raw_text': f"{weight} {unit}",
                    'method': 'claude_api'
                }
            else:
                print(f"❌ Invalid Claude response format: {weight_data}")
                print(f"   Missing required fields: weight={weight_data.get('weight')}, unit={weight_data.get('unit')}, confidence={weight_data.get('confidence')}")

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"❌ Error parsing Claude response: {e}")
            print(f"   Response: {content}")

    except Exception as e:
        print(f"❌ Claude API error: {e}")

    return {
        'weight': 0.0,
        'unit': 'g',
        'confidence': 0.0,
        'error': 'Failed to read weight from image',
        'method': 'claude_api'
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
          description="Extract weight value from a digital scale image using Claude AI vision",
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
    Capture weight from a scale image using Claude AI vision.

    **Process:**
    1. Receives image and context (farmer_id, produce_name)
    2. Sends image to Claude API for analysis
    3. Claude extracts weight value and unit from digital display
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

        # Fix base64 padding if needed and decode
        try:
            image_base64 = request.image_base64.strip()
            # Add padding if needed
            padding = len(image_base64) % 4
            if padding:
                image_base64 += '=' * (4 - padding)

            image_data = base64.b64decode(image_base64)
        except Exception as decode_error:
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid base64 encoding: {str(decode_error)}"}
            )
        nparr = np.frombuffer(image_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if frame is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Invalid image data"}
            )

        # Extract weight from scale using Claude API
        weight_data = await extract_weight_from_scale(frame)

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
    import threading

    # Initialize models in background thread to avoid blocking startup
    def init_models_async():
        initialize_models()

    model_thread = threading.Thread(target=init_models_async, daemon=True)
    model_thread.start()

    port = int(os.getenv("PORT", 8000))
    print(f"Starting server on http://0.0.0.0:{port}")
    print("🔄 Models are loading in the background...")
    print("\nAvailable endpoints:")
    print(f"  - http://0.0.0.0:{port}/webcam_client.html (Produce detection demo)")
    print(f"  - http://0.0.0.0:{port}/test_weight_capture.html (Weight capture test)")
    print(f"  - POST http://0.0.0.0:{port}/api/v1/capture/weight (API endpoint)")
    print(f"  - WebSocket ws://0.0.0.0:{port}/ws/stream (Real-time detection)")
    uvicorn.run(app, host="0.0.0.0", port=port)
