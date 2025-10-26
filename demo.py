#!/usr/bin/env python3
"""
Hackathon Demo Script
=====================

This script demonstrates the Gemini AI analytics system for your hackathon demo.

Features demonstrated:
1. CSV data analysis (insights, forecasts, recommendations)
2. Image analysis (crate counting, quality assessment)
3. API endpoint integration

Usage:
    python demo.py [--csv-only | --image-only | --api-only]
"""

import sys
import os
import json
import argparse
from pathlib import Path

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print a styled header"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.ENDC}\n")

def print_section(text):
    """Print a section divider"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.BLUE}{'-'*50}{Colors.ENDC}")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.ENDC}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}")

def demo_csv_analytics():
    """Demo CSV analytics functionality"""
    print_header("📊 CSV ANALYTICS DEMO")
    
    csv_path = "sample_weekly.csv"
    
    if not os.path.exists(csv_path):
        print_error(f"Sample CSV not found: {csv_path}")
        print("Creating sample CSV...")
        create_sample_csv()
    
    print_section("1. Loading Sample Data")
    print(f"📁 CSV File: {csv_path}")
    
    try:
        import pandas as pd
        df = pd.read_csv(csv_path)
        print_success(f"Loaded {len(df)} rows of farm data")
        print(f"\n{df.to_string()}\n")
    except Exception as e:
        print_error(f"Failed to load CSV: {e}")
        return
    
    print_section("2. Analyzing with Gemini AI")
    
    try:
        from analyze_csv import analyze_csv
        
        print("🤖 Sending to Gemini for analysis...")
        result = analyze_csv(csv_path)
        
        print_success("Analysis complete!")
        
        # Display insights
        print_section("📈 Key Insights")
        for i, insight in enumerate(result['insights'], 1):
            print(f"\n{Colors.BOLD}{i}. {insight['title']}{Colors.ENDC}")
            print(f"   {insight['explanation']}")
        
        # Display forecast
        print_section("🔮 2-Week Forecast")
        forecast_table = []
        for f in result['forecast']:
            forecast_table.append(f"{f['week_start']:12} | {f['crop']:10} | {f['kg']:>6} kg")
        
        print(f"\n{'Week Start':12} | {'Crop':10} | {'Supply (kg)':>6}")
        print("-" * 40)
        for row in forecast_table:
            print(row)
        
        # Display recommendations
        print_section("💡 Recommendations")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"\n{i}. {rec}")
        
        print()
        
    except ImportError:
        print_error("Gemini modules not available")
        print_warning("Install: pip install google-genai pandas")
    except Exception as e:
        print_error(f"Analysis failed: {e}")

def demo_image_analytics():
    """Demo image analytics functionality"""
    print_header("🖼️  IMAGE ANALYTICS DEMO")
    
    # Check for sample images
    image_extensions = ['.jpg', '.jpeg', '.png']
    sample_images = []
    
    for ext in image_extensions:
        sample_images.extend(Path('.').glob(f'*sample*{ext}'))
        sample_images.extend(Path('.').glob(f'*crate*{ext}'))
        sample_images.extend(Path('.').glob(f'*produce*{ext}'))
    
    if not sample_images:
        print_warning("No sample images found in current directory")
        print("Looking for images with names like: sample_crates.jpg, produce.png, etc.")
        print("\n💡 To test image analysis:")
        print("   1. Add a sample image (crates, produce, etc.)")
        print("   2. Run: python analyze_image.py <image_path>")
        return
    
    image_path = str(sample_images[0])
    print_section("1. Sample Image")
    print(f"📷 Image: {image_path}")
    
    print_section("2. Analyzing with Gemini Vision AI")
    
    try:
        from analyze_image import analyze_image
        
        print("🤖 Sending to Gemini Vision for analysis...")
        result = analyze_image(image_path)
        
        print_success("Analysis complete!")
        
        # Display results
        print_section("🔍 Analysis Results")
        print(f"\n{Colors.BOLD}Crate Count:{Colors.ENDC} {result['crate_count']}")
        print(f"{Colors.BOLD}Total Weight:{Colors.ENDC} {result['estimated_total_weight_kg']} kg")
        print(f"{Colors.BOLD}Per Crate:{Colors.ENDC} {result.get('per_crate_estimate_kg', 0)} kg")
        print(f"{Colors.BOLD}Quality:{Colors.ENDC} {result['quality_score']}")
        print(f"{Colors.BOLD}Confidence:{Colors.ENDC} {result['confidence']:.1%}")
        print(f"\n{Colors.BOLD}Notes:{Colors.ENDC} {result.get('notes', 'N/A')}")
        print()
        
    except ImportError:
        print_error("Gemini modules not available")
        print_warning("Install: pip install google-genai")
    except Exception as e:
        print_error(f"Analysis failed: {e}")

def demo_api_integration():
    """Demo API endpoint integration"""
    print_header("🚀 API INTEGRATION DEMO")
    
    print_section("Available API Endpoints")
    
    endpoints = [
        ("POST", "/api/v1/analytics/csv", "Analyze CSV data"),
        ("POST", "/api/v1/analytics/image", "Analyze produce image"),
        ("GET", "/api/v1/analytics/status", "Check analytics status"),
        ("POST", "/api/v1/capture/weight", "Capture weight from scale"),
    ]
    
    for method, endpoint, description in endpoints:
        print(f"{Colors.GREEN}{method:6}{Colors.ENDC} {endpoint:35} - {description}")
    
    print_section("Example: CSV Analytics Request")
    
    example_request = {
        "farmer_id": "farmer123",
        "csv_data": "week_start,crop,total_supplied_kg,total_sold_kg\\n2025-09-01,tomato,500,450",
        "crop_filter": "tomato"
    }
    
    print(f"\n{Colors.BOLD}POST{Colors.ENDC} http://localhost:8001/api/v1/analytics/csv")
    print(f"\n{json.dumps(example_request, indent=2)}")
    
    print_section("Example: Image Analytics Request")
    
    example_image_request = {
        "farmer_id": "farmer123",
        "image_base64": "<base64_encoded_image>",
        "produce_type": "tomatoes"
    }
    
    print(f"\n{Colors.BOLD}POST{Colors.ENDC} http://localhost:8001/api/v1/analytics/image")
    print(f"\n{json.dumps(example_image_request, indent=2)}")
    
    print_section("Testing API")
    
    # Check if server is running
    try:
        import requests
        response = requests.get("http://localhost:8001/api/v1/analytics/status", timeout=2)
        
        if response.status_code == 200:
            status = response.json()
            print_success("API server is running!")
            print(f"\n{json.dumps(status, indent=2)}")
        else:
            print_warning(f"API returned status code: {response.status_code}")
            
    except ImportError:
        print_warning("Install 'requests' to test API: pip install requests")
    except Exception as e:
        print_warning("API server not running")
        print("\n💡 Start the server with:")
        print("   python app.py")
    
    print()

def create_sample_csv():
    """Create sample CSV if it doesn't exist"""
    csv_content = """week_start,crop,total_supplied_kg,total_sold_kg,avg_delivery_delay_min
2025-09-01,tomato,500,450,20
2025-09-08,tomato,520,480,25
2025-09-15,tomato,480,430,40
2025-09-22,tomato,600,560,15
2025-09-01,mango,200,180,30
2025-09-08,mango,230,210,20
2025-09-15,mango,210,200,35
2025-09-22,mango,250,240,18
"""
    with open("sample_weekly.csv", "w") as f:
        f.write(csv_content)
    print_success("Created sample_weekly.csv")

def check_setup():
    """Check if setup is complete"""
    print_header("🔧 SETUP CHECK")
    
    checks = []
    
    # Check Python version
    import sys
    py_version = sys.version_info
    checks.append(("Python 3.7+", py_version >= (3, 7), f"Python {py_version.major}.{py_version.minor}"))
    
    # Check dependencies
    try:
        import pandas
        checks.append(("pandas", True, f"v{pandas.__version__}"))
    except ImportError:
        checks.append(("pandas", False, "Not installed"))
    
    try:
        from google import genai
        checks.append(("google-genai", True, "Installed"))
    except ImportError:
        checks.append(("google-genai", False, "Not installed"))
    
    try:
        import fastapi
        checks.append(("fastapi", True, f"v{fastapi.__version__}"))
    except ImportError:
        checks.append(("fastapi", False, "Not installed"))
    
    # Check environment
    gemini_key = os.getenv("GEMINI_API_KEY")
    checks.append(("GEMINI_API_KEY", bool(gemini_key), "Set" if gemini_key else "Not set"))
    
    # Check files
    checks.append(("gemini_client.py", os.path.exists("gemini_client.py"), ""))
    checks.append(("analyze_csv.py", os.path.exists("analyze_csv.py"), ""))
    checks.append(("analyze_image.py", os.path.exists("analyze_image.py"), ""))
    checks.append(("sample_weekly.csv", os.path.exists("sample_weekly.csv"), ""))
    
    # Display results
    for name, status, info in checks:
        if status:
            print_success(f"{name:25} {info}")
        else:
            print_error(f"{name:25} {info}")
    
    print()

def main():
    """Main demo function"""
    parser = argparse.ArgumentParser(description="Hackathon Demo Script")
    parser.add_argument("--csv-only", action="store_true", help="Run only CSV analytics demo")
    parser.add_argument("--image-only", action="store_true", help="Run only image analytics demo")
    parser.add_argument("--api-only", action="store_true", help="Run only API integration demo")
    parser.add_argument("--check", action="store_true", help="Check setup and dependencies")
    
    args = parser.parse_args()
    
    # Show banner
    print(f"\n{Colors.BOLD}{Colors.CYAN}")
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║                                                                    ║")
    print("║         🌾 FARM AI ANALYTICS - HACKATHON DEMO 🌾                  ║")
    print("║                                                                    ║")
    print("║              Powered by Gemini AI                                 ║")
    print("║                                                                    ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print(Colors.ENDC)
    
    if args.check:
        check_setup()
        return
    
    # Run selected demos
    if args.csv_only:
        demo_csv_analytics()
    elif args.image_only:
        demo_image_analytics()
    elif args.api_only:
        demo_api_integration()
    else:
        # Run all demos
        check_setup()
        demo_csv_analytics()
        demo_image_analytics()
        demo_api_integration()
    
    # Final message
    print_header("🎉 DEMO COMPLETE")
    print(f"{Colors.GREEN}Ready for your hackathon presentation!{Colors.ENDC}\n")
    print("📚 Quick Reference:")
    print("  • CSV analysis:   python analyze_csv.py sample_weekly.csv")
    print("  • Image analysis: python analyze_image.py <image_path>")
    print("  • Start API:      python app.py")
    print("  • API docs:       http://localhost:8001/docs")
    print()

if __name__ == "__main__":
    main()

