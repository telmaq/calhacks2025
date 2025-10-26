#!/usr/bin/env python3
# analyze_image.py
"""
Image analysis using Gemini's multimodal capabilities.
Analyzes crate photos to count produce, estimate weight, and assess quality.
"""

from gemini_client import init_client, get_model_name
import json
import base64
import sys
import os
from pathlib import Path

def read_image_b64(path):
    """
    Read image file and convert to base64.
    
    Args:
        path: Path to image file
        
    Returns:
        str: Base64 encoded image
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image file not found: {path}")
    
    with open(path, "rb") as f:
        image_bytes = f.read()
    
    file_size_kb = len(image_bytes) / 1024
    print(f"✅ Loaded image: {Path(path).name} ({file_size_kb:.1f} KB)")
    
    return base64.b64encode(image_bytes).decode('utf-8')

def craft_image_prompt():
    """
    Create prompt for image analysis.
    
    Returns:
        str: Structured prompt for Gemini
    """
    return """You are an AI image analyst for farm produce logistics.

**Input:** Photo of produce crates on a scale or in storage.

**Your Task:** Analyze this image and return ONLY valid JSON in this EXACT format:
{
  "crate_count": 0,
  "estimated_total_weight_kg": 0.0,
  "per_crate_estimate_kg": 0.0,
  "quality_score": "excellent|good|average|fair|poor",
  "confidence": 0.0,
  "notes": "Brief description of what you see"
}

**Analysis Guidelines:**
1. Count visible crates/containers
2. Estimate total weight based on visual cues (size, fullness, produce type)
3. Calculate per-crate average weight
4. Assess produce quality based on visible freshness, color, damage
5. Provide confidence score (0.0 to 1.0)
6. Add brief notes about what you observed

**Requirements:**
- Output MUST be valid JSON only - no markdown, no explanation, no extra text
- Be conservative with weight estimates
- Quality score must be one of: excellent, good, average, fair, poor
- Confidence should reflect how clearly you can see the produce

**Output (JSON only):**"""

def analyze_image(path):
    """
    Analyze image using Gemini's multimodal model.
    
    Args:
        path: Path to image file
        
    Returns:
        dict: Structured image analysis results
    """
    print(f"🖼️  Analyzing image: {path}")
    
    # Read image
    img_b64 = read_image_b64(path)
    
    # Initialize Gemini client
    try:
        client = init_client()
        model_name = get_model_name()
        print(f"🤖 Using Gemini model: {model_name}")
    except Exception as e:
        print(f"❌ Failed to initialize Gemini client: {e}")
        print("💡 Tip: Set GEMINI_API_KEY environment variable or run 'gcloud auth application-default login'")
        raise
    
    # Create prompt
    prompt = craft_image_prompt()
    
    # Call Gemini API with multimodal input
    print("🔄 Calling Gemini Vision API...")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[
                {
                    "parts": [
                        {"inline_data": {"mime_type": "image/jpeg", "data": img_b64}},
                        {"text": prompt}
                    ]
                }
            ],
            config={
                "temperature": 0.2,  # Low temperature for consistent analysis
                "max_output_tokens": 500,
                "response_mime_type": "application/json"  # Request JSON response
            }
        )
        
        # Extract text from response
        out_text = response.text
        print("✅ Received response from Gemini")
        
        # Parse JSON
        try:
            result = json.loads(out_text)
            print("✅ Successfully parsed JSON response")
            
            # Validate structure
            required_keys = ["crate_count", "estimated_total_weight_kg", "quality_score", "confidence"]
            for key in required_keys:
                if key not in result:
                    raise ValueError(f"Missing required key in response: {key}")
            
            # Validate quality score
            valid_scores = ["excellent", "good", "average", "fair", "poor"]
            if result["quality_score"] not in valid_scores:
                print(f"⚠️  Warning: Invalid quality score '{result['quality_score']}', using 'average'")
                result["quality_score"] = "average"
            
            return result
            
        except json.JSONDecodeError as e:
            print("❌ Failed to parse JSON from Gemini response")
            print(f"Raw output:\n{out_text}")
            raise ValueError(f"Invalid JSON response: {e}")
            
    except Exception as e:
        print(f"❌ Error calling Gemini API: {e}")
        raise

def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python analyze_image.py <path_to_image>")
        print("Example: python analyze_image.py sample_crates.jpg")
        sys.exit(1)
    
    path = sys.argv[1]
    
    try:
        result = analyze_image(path)
        print("\n" + "="*60)
        print("🔍 IMAGE ANALYSIS RESULTS")
        print("="*60)
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

