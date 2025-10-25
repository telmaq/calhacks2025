#!/usr/bin/env python3
"""
Simple test script for the deployed Smart Camera API
Replace YOUR_RAILWAY_URL with your actual Railway URL
"""

import requests
import base64
from pathlib import Path

# Replace with your Railway URL
API_URL = "https://calhacks2025-production.up.railway.app"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing health endpoint...")
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_weight_capture(image_path):
    """Test weight capture with an image"""
    print(f"📸 Testing weight capture with {image_path}...")

    # Read and encode image
    with open(image_path, "rb") as f:
        image_data = f.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')

    # Make request
    payload = {
        "farmer_id": "test_farmer_001",
        "produce_name": "apples",
        "image_base64": image_base64
    }

    response = requests.post(
        f"{API_URL}/api/v1/capture/weight",
        json=payload
    )

    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

if __name__ == "__main__":
    print("🚀 Testing Smart Camera API\n")

    # Test health
    test_health()

    # Test with an image if provided
    image_path = input("Enter path to test image (or press Enter to skip): ").strip()
    if image_path and Path(image_path).exists():
        test_weight_capture(image_path)
    else:
        print("Skipping image test (no valid image provided)")
        print()
        print("To test with an image:")
        print(f"  python test_api.py")
        print()
        print("Example: python test_api.py path/to/scale_image.jpg")
