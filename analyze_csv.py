#!/usr/bin/env python3
# analyze_csv.py
"""
CSV analytics using Gemini AI.
Analyzes farm marketplace data and returns structured insights, forecasts, and recommendations.
"""

from gemini_client import init_client, get_model_name
import pandas as pd
import json
import sys
import os

def load_csv(path):
    """Load CSV file into pandas DataFrame"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"CSV file not found: {path}")
    
    df = pd.read_csv(path)
    print(f"✅ Loaded CSV with {len(df)} rows and columns: {', '.join(df.columns)}")
    return df

def craft_prompt(df, crop=None):
    """
    Create a structured prompt for Gemini to analyze farm data.
    
    Args:
        df: pandas DataFrame with farm data
        crop: Optional specific crop to focus on
        
    Returns:
        str: Formatted prompt for Gemini
    """
    # Convert DataFrame to CSV string (limit to reasonable size)
    csv_snippet = df.to_csv(index=False)
    
    # Truncate if too large (keep under ~4KB for reliable processing)
    if len(csv_snippet) > 4000:
        # Take first N rows that fit
        rows_to_keep = int(len(df) * 4000 / len(csv_snippet))
        csv_snippet = df.head(rows_to_keep).to_csv(index=False)
        csv_snippet += f"\n... (showing {rows_to_keep} of {len(df)} rows)"
    
    crop_context = f" Focus on {crop} crop." if crop else ""
    
    instruction = f"""You are a farm marketplace analytics AI assistant.

**Input Data:**
CSV with columns: {', '.join(df.columns)}
Total records: {len(df)} rows

**Your Task:**
Analyze this farm supply/sales data and return ONLY valid JSON in this EXACT format:
{{
  "insights": [
    {{"title": "Brief insight title", "explanation": "1-2 sentence explanation"}},
    {{"title": "Another insight", "explanation": "1-2 sentence explanation"}},
    {{"title": "Third insight", "explanation": "1-2 sentence explanation"}}
  ],
  "forecast": [
    {{"week_start": "YYYY-MM-DD", "crop": "crop_name", "kg": 0}},
    {{"week_start": "YYYY-MM-DD", "crop": "crop_name", "kg": 0}}
  ],
  "recommendations": [
    "Practical recommendation 1 for the farmer",
    "Practical recommendation 2 for the farmer",
    "Practical recommendation 3 for the farmer"
  ]
}}

**Requirements:**
1. Provide EXACTLY 3 insights (top patterns, trends, or anomalies)
2. Forecast supply for the next 2 weeks for each crop found in the data
3. Give EXACTLY 3 actionable recommendations to improve sales/delivery/efficiency
4. Output MUST be valid JSON only - no markdown, no explanation, no extra text
5. Base all analysis on the actual data patterns{crop_context}

**CSV Data:**
{csv_snippet}

**Output (JSON only):**"""
    
    return instruction

def analyze_csv(path, crop=None):
    """
    Analyze CSV file using Gemini AI.
    
    Args:
        path: Path to CSV file
        crop: Optional specific crop to analyze
        
    Returns:
        dict: Structured analytics results with insights, forecast, recommendations
    """
    print(f"📊 Analyzing CSV: {path}")
    
    # Load data
    df = load_csv(path)
    
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
    prompt = craft_prompt(df, crop)
    
    # Call Gemini API
    print("🔄 Calling Gemini API...")
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                "temperature": 0.1,  # Low temperature for deterministic JSON output
                "max_output_tokens": 1000,
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
            required_keys = ["insights", "forecast", "recommendations"]
            for key in required_keys:
                if key not in result:
                    raise ValueError(f"Missing required key in response: {key}")
            
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
        print("Usage: python analyze_csv.py <path_to_csv> [crop_name]")
        print("Example: python analyze_csv.py sample_weekly.csv tomato")
        sys.exit(1)
    
    path = sys.argv[1]
    crop = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result = analyze_csv(path, crop)
        print("\n" + "="*60)
        print("📈 ANALYTICS RESULTS")
        print("="*60)
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

