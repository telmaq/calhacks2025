# gemini_client.py
"""
Gemini API client for AI-powered analytics.
Supports both API key and Application Default Credentials (ADC) authentication.
"""

from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

def init_client():
    """
    Initialize Gemini client with authentication.
    
    Authentication options (in priority order):
    1. GEMINI_API_KEY environment variable (API key mode)
    2. Application Default Credentials (gcloud auth application-default login)
    
    Returns:
        genai.Client: Initialized Gemini client
    """
    api_key = os.getenv("GEMINI_API_KEY")
    
    if api_key:
        print("✅ Using Gemini API key authentication")
        client = genai.Client(api_key=api_key)
    else:
        print("✅ Using Application Default Credentials (ADC)")
        # Falls back to ADC if no API key is provided
        client = genai.Client()
    
    return client

def get_model_name():
    """
    Get the Gemini model name to use.
    Defaults to gemini-2.0-flash-exp but can be overridden via environment variable.
    
    Returns:
        str: Model name
    """
    return os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

