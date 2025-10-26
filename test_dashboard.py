#!/usr/bin/env python3
"""
Quick Dashboard Test
====================

Tests if dashboard dependencies are installed and working.

Usage:
    python test_dashboard.py
"""

def test_imports():
    """Test if all required packages are installed"""
    print("🧪 Testing Dashboard Dependencies...\n")
    
    tests = []
    
    # Test Dash
    try:
        import dash
        print(f"✅ Dash {dash.__version__}")
        tests.append(True)
    except ImportError:
        print("❌ Dash not installed")
        print("   → pip install dash")
        tests.append(False)
    
    # Test Plotly
    try:
        import plotly
        print(f"✅ Plotly {plotly.__version__}")
        tests.append(True)
    except ImportError:
        print("❌ Plotly not installed")
        print("   → pip install plotly")
        tests.append(False)
    
    # Test Pandas
    try:
        import pandas
        print(f"✅ Pandas {pandas.__version__}")
        tests.append(True)
    except ImportError:
        print("❌ Pandas not installed")
        print("   → pip install pandas")
        tests.append(False)
    
    # Test Gunicorn (for deployment)
    try:
        import gunicorn
        print(f"✅ Gunicorn (for deployment)")
        tests.append(True)
    except ImportError:
        print("⚠️  Gunicorn not installed (only needed for deployment)")
        print("   → pip install gunicorn")
        tests.append(True)  # Not critical for local testing
    
    return all(tests)

def test_data_file():
    """Test if sample data exists"""
    print("\n🗂️  Testing Data Files...\n")
    
    import os
    
    if os.path.exists("sample_weekly.csv"):
        print("✅ sample_weekly.csv found")
        return True
    else:
        print("❌ sample_weekly.csv not found")
        print("   → Make sure you're in the project directory")
        return False

def test_dashboard_loads():
    """Test if dashboard.py can be imported"""
    print("\n📊 Testing Dashboard Module...\n")
    
    try:
        from dashboard import app
        print("✅ Dashboard module loads successfully")
        print(f"   Server: {app.server}")
        return True
    except Exception as e:
        print(f"❌ Dashboard failed to load: {e}")
        return False

def main():
    print("="*60)
    print("DASHBOARD TEST SUITE".center(60))
    print("="*60)
    print()
    
    results = []
    
    # Test 1: Imports
    results.append(("Dependencies", test_imports()))
    
    # Test 2: Data
    results.append(("Data Files", test_data_file()))
    
    # Test 3: Dashboard
    results.append(("Dashboard Load", test_dashboard_loads()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY".center(60))
    print("="*60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:30} {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Dashboard is ready to run.")
        print("\n🚀 Start dashboard with:")
        print("   python dashboard.py")
        print("\n📊 Then visit:")
        print("   http://localhost:8050")
    else:
        print("\n⚠️  Some tests failed. Fix issues above and try again.")
        print("\n💡 Quick fix:")
        print("   pip install -r requirements-dashboard.txt")

if __name__ == "__main__":
    main()

