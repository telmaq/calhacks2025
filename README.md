# Smart Camera Service

Simple webcam-based object detection using OpenCV.

## Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start the server:

```bash
python app.py
```

3. Open your browser:

```
http://localhost:8001/webcam_client.html
```

4. Click "Start Camera" to begin streaming and detection

## What It Does

- Captures frames from your webcam every 500ms
- Detects objects using simple contour detection
- Identifies rectangular shapes that might be scales
- Returns detection results in real-time

## Files

- `app.py` - FastAPI server with WebSocket endpoint
- `webcam_client.html` - Simple webcam client for browser
- `requirements.txt` - Python dependencies

That's it. Keep it simple.
