#!/bin/bash

# Railway startup script for Smart Camera Service
echo "🚀 Starting Smart Camera Service..."

# Set environment variables
export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

# Create necessary directories
mkdir -p ~/.cache/torch/hub/checkpoints

# Start the application directly
echo "🎯 Starting FastAPI server..."
exec python app.py
