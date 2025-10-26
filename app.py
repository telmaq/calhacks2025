from fastapi import FastAPI, WebSocket, WebSocketDisconnect, File, UploadFile, Form, HTTPException, Depends, Header
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import json
import base64
from typing import List, Optional
import httpx
import requests
from pydantic import BaseModel
import re
import os
from dotenv import load_dotenv
import anthropic
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import uuid
from datetime import datetime
load_dotenv()

app = FastAPI(
    title="FarmFresh Marketplace - Smart Camera Service",
    description="AI-powered computer vision service for family farms to capture produce weight and manage inventory",
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


# Google Sheets configuration
GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE")
GOOGLE_SHEETS_ID = os.getenv("GOOGLE_SHEETS_ID")
sheets_service = None


def init_google_sheets():
    """Initialize Google Sheets service"""
    global sheets_service
    if GOOGLE_SHEETS_CREDENTIALS_FILE and GOOGLE_SHEETS_ID:
        try:
            # Define the scopes
            SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

            # Load credentials from file
            creds = Credentials.from_service_account_file(
                GOOGLE_SHEETS_CREDENTIALS_FILE, scopes=SCOPES)

            # Build the service
            sheets_service = build('sheets', 'v4', credentials=creds)
            print("Google Sheets service initialized")
        except Exception as e:
            print(f"Error initializing Google Sheets: {e}")
            sheets_service = None
    else:
        print("Google Sheets credentials not found")

async def write_to_google_sheets(data: dict) -> str:
    """Write product data to Google Sheets"""
    if not sheets_service:
        raise Exception("Google Sheets service not initialized")

    try:
        # Generate UUID for product ID
        product_id = str(uuid.uuid4())

        # Get current timestamp
        current_time = int(datetime.now().timestamp())

        # Prepare the row data according to the Google Sheets format
        row_data = [
            product_id,                    # ID
            data["farmer_id"],            # Seller ID
            data["produce_name"],         # Name (Claude-detected)
            data.get("description", f"Captured produce: {data['produce_name']}"),  # Description (Claude-detected)
            data.get("category", "other"), # Category (Claude-detected)
            data["weight"],               # Price (using weight as price)
            data["unit"],                 # Unit
            1,                            # Stock
            "null",                       # Image URL
            "TRUE",                       # Available
            data["farmer_id"],            # Creator
            data["farmer_id"],            # Updater
            current_time,                 # Created timestamp
            current_time                  # Updated timestamp
        ]

        # Append the row to the sheet using a simpler approach
        range_name = 'Products'  # Just use the sheet name
        body = {
            'values': [row_data]
        }

        result = sheets_service.spreadsheets().values().append(
            spreadsheetId=GOOGLE_SHEETS_ID,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()

        print(f"Successfully wrote to Google Sheets: {product_id}")
        return product_id

    except Exception as e:
        print(f"Error writing to Google Sheets: {e}")
        raise

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
    image_url: Optional[str] = None

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

# Use smaller model to reduce memory footprint
model = None


async def extract_weight_from_scale(frame: np.ndarray) -> dict:
    """
    Extract weight from digital scale display using Claude API.
    """
    if not claude_client:
        print("Claude API key not configured. Set CLAUDE_API_KEY environment variable.")
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
                            "text": """Look at this image of produce on a digital scale and extract the following information:

1. Weight value and unit from the digital display
2. Name of the produce item
3. Description of the produce
4. Category (must be one of: Vegetables, Fruits, Dairy, Grains, Meat, Other)

You must respond with ONLY a valid JSON object in this exact format:
{
    "weight": <number>,
    "unit": "<unit>",
    "name": "<produce name>",
    "description": "<brief description>",
    "category": "<category>",
    "confidence": <0.0-1.0>
}

Examples:
- If you see tomatoes weighing "54 g" return: {"weight": 54, "unit": "g", "name": "Tomatoes", "description": "Fresh red tomatoes", "category": "Vegetables", "confidence": 0.95}
- If you see apples weighing "1.5 kg" return: {"weight": 1.5, "unit": "kg", "name": "Apples", "description": "Red apples", "category": "Fruits", "confidence": 0.90}
- If you see cheese weighing "250 g" return: {"weight": 250, "unit": "g", "name": "Cheese", "description": "Block of cheese", "category": "Dairy", "confidence": 0.88}

Category must be exactly one of: vegetables, fruits, dairy, grains, meat, other

If you cannot clearly read a weight value or identify the produce, return: {"weight": 0, "unit": "g", "name": "Unknown", "description": "Unable to identify", "category": "Other", "confidence": 0.0}

Focus on both the digital display area and the produce item. Return ONLY the JSON object, no other text."""
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
            if all(field in weight_data for field in ['weight', 'unit', 'name', 'description', 'category', 'confidence']):
                weight = float(weight_data['weight'])
                unit = str(weight_data['unit']).lower().strip()
                name = str(weight_data['name']).strip()
                description = str(weight_data['description']).strip()
                category = str(weight_data['category']).strip()
                confidence = float(weight_data['confidence'])

                # Validate category
                valid_categories = ['vegetables', 'fruits', 'dairy', 'grains', 'meat', 'other']
                if category not in valid_categories:
                    print(f"⚠️ Invalid category '{category}', defaulting to 'Other'")
                    category = 'Other'

                print(f"✅ Claude detected: {name} - {weight} {unit} ({category}, confidence: {confidence:.2f})")

                return {
                    'weight': weight,
                    'unit': unit,
                    'name': name,
                    'description': description,
                    'category': category,
                    'price': weight,  # Using weight as price for now
                    'stock_quantity': 1,
                    'image_url': None,
                    'available': True,
                    'confidence': confidence,
                    'method': 'claude_api'
                }
            else:
                missing_fields = [field for field in ['weight', 'unit', 'name', 'description', 'category', 'confidence'] if field not in weight_data]
                print(f"❌ Invalid Claude response format: {weight_data}")
                print(f"   Missing required fields: {missing_fields}")

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Error parsing Claude response: {e}")
            print(f"   Response: {content}")

    except Exception as e:
        print(f"❌ Claude API error: {e}")

    return {
        'weight': 0.0,
        'unit': 'g',
        'name': 'Unknown',
        'description': 'Unable to identify',
        'category': 'Other',
        'confidence': 0.0,
        'error': 'Failed to read weight from image',
        'method': 'claude_api'
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
    print(f"   - image_url: {request.image_url}")
    print(f"   - using: {'base64' if request.image_base64 else 'URL' if request.image_url else 'neither'}")
    # print(f"   - API key: {api_key[:10]}...")

    try:
        # Process image from either base64 or URL
        if not request.image_base64 and not request.image_url:
            return JSONResponse(
                status_code=400,
                content={"error": "image_base64 or image_url is required"}
            )

        try:
            if request.image_base64:
                # Process base64 image
                image_base64 = request.image_base64.strip()
                # Add padding if needed
                padding = len(image_base64) % 4
                if padding:
                    image_base64 += '=' * (4 - padding)
                image_data = base64.b64decode(image_base64)

            elif request.image_url:
                # Process image URL
                image_url = request.image_url.strip()
                print(f"Fetching image from URL: {image_url}")
                response = requests.get(image_url, timeout=30)
                response.raise_for_status()  # Raise exception for bad status codes
                image_data = response.content
                print(f"Successfully fetched image ({len(image_data)} bytes)")

        except requests.RequestException as e:
            return JSONResponse(
                status_code=400,
                content={"error": f"Failed to fetch image from URL: {str(e)}"}
            )
        except Exception as decode_error:
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid image data: {str(decode_error)}"}
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

        # Write to Google Sheets
        product_id = None
        try:
            if sheets_service:
                product_id = await write_to_google_sheets({
                    'farmer_id': request.farmer_id,
                    'produce_name': weight_data.get('name', 'Unknown Produce'),  # Use Claude-detected name
                    'weight': weight_data['weight'],
                    'unit': weight_data['unit'],
                    'description': weight_data.get('description', ''),
                    'category': weight_data.get('category', 'other')
                })
                print(f"✅ Saved to Google Sheets: {product_id}")
            else:
                print("⚠️  Google Sheets not initialized, skipping database write")
        except Exception as e:
            print(f"❌ Failed to write to Google Sheets: {e}")

        # Return data in Creao-compatible format
        return JSONResponse(content={
            "status": "success",
            "farmer_id": request.farmer_id,
            "weight_data": {
                "weight": weight_data['weight'],
                "unit": weight_data['unit'],
                "confidence": weight_data.get('confidence', 0.95),
                "raw_text": f"{weight_data['weight']} {weight_data['unit']}",
                "method": weight_data.get('method', 'claude_api')
            },
            "message": f"Weight {weight_data['weight']} {weight_data['unit']} captured!",
            "creao_logged": False,
            "id": product_id,
            "seller_id": request.farmer_id,
            "name": weight_data.get('name', 'Unknown Produce'),  # Use Claude-detected name
            "description": weight_data.get('description', ''),
            "category": weight_data.get('category', 'other'),
            "price": weight_data['weight'],
            "unit": weight_data['unit']
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
         description="Get the current status of the FarmFresh Marketplace Smart Camera Service",
         tags=["Health"])
async def root():
    """Get API status and version information"""
    return {
        "status": "FarmFresh Marketplace - Smart Camera Service",
        "version": "1.0.0",
        "description": "AI-powered computer vision service for family farms to capture produce weight and manage inventory",
        "marketplace": "FarmFresh - Connecting Family Farms with Smart Technology",
        "endpoints": {
            "weight_capture": "/api/v1/capture/weight",
            "produce_detection": "/webcam_client.html",
            "weight_test": "/test_weight_capture.html",
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

    # Initialize Google Sheets service
    init_google_sheets()

    # Initialize models in background thread to avoid blocking startup
    def init_models_async():
        initialize_models()

    model_thread = threading.Thread(target=init_models_async, daemon=True)
    model_thread.start()

    port = int(os.getenv("PORT", 8000))
    print("="*60)
    print("FarmFresh Marketplace - Smart Camera Service")
    print("Connecting Family Farms with AI Technology")
    print("="*60)
    print(f"Starting server on http://0.0.0.0:{port}")
    print("AI models are loading in the background...")
    print("\nAvailable Marketplace Services:")
    print(f"  http://0.0.0.0:{port}/test_weight_capture.html (Smart Weight Capture)")
    print(f"  http://0.0.0.0:{port}/webcam_client.html (Produce Detection)")
    print(f"  POST http://0.0.0.0:{port}/api/v1/capture/weight (API endpoint)")
    print(f"  WebSocket ws://0.0.0.0:{port}/ws/stream (Real-time detection)")
    print(f"  http://0.0.0.0:{port}/docs (API Documentation)")
    print("="*60)
    uvicorn.run(app, host="0.0.0.0", port=port)
