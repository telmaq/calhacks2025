#!/usr/bin/env python3
"""
Dashboard API Integration
==========================

API endpoints for Creao to send data and retrieve analytics.
This allows Creao app to:
1. Send farmer data via API
2. Request analytics generation
3. Get charts/graphs data

Can run standalone or alongside dashboard.py

Usage:
    python dashboard_api.py
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import json
import os
from datetime import datetime
import tempfile

# Import analytics
try:
    from analyze_csv import analyze_csv
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

app = FastAPI(
    title="Farm Analytics Dashboard API",
    description="API for Creao to send data and get analytics with charts",
    version="1.0.0"
)

# Enable CORS for Creao app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify Creao app domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (for demo - use database in production)
farmer_data_store = {}

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class WeeklyData(BaseModel):
    week_start: str  # "2025-09-01"
    crop: str
    total_supplied_kg: float
    total_sold_kg: float
    avg_delivery_delay_min: Optional[float] = 0

class SendDataRequest(BaseModel):
    farmer_id: str
    farmer_name: Optional[str] = "Unknown Farmer"
    data: List[WeeklyData]
    metadata: Optional[Dict] = {}

class GenerateAnalyticsRequest(BaseModel):
    farmer_id: str
    crop_filter: Optional[str] = None
    weeks: Optional[int] = 12

class ChartDataPoint(BaseModel):
    x: str  # Date or label
    y: float  # Value
    crop: Optional[str] = None

class ChartData(BaseModel):
    chart_type: str  # "line", "bar", "pie", "forecast"
    title: str
    data: List[Dict]  # Flexible for different chart types
    
class AnalyticsResponse(BaseModel):
    status: str
    farmer_id: str
    farmer_name: str
    insights: List[Dict]
    forecast: List[Dict]
    recommendations: List[str]
    charts: Dict[str, ChartData]
    source: str  # "gemini" or "mock"

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.post("/api/data/send")
async def receive_farmer_data(request: SendDataRequest):
    """
    Creao sends farmer data to be stored for analytics.
    
    Example:
    ```json
    {
        "farmer_id": "farmer123",
        "farmer_name": "John's Farm",
        "data": [
            {
                "week_start": "2025-09-01",
                "crop": "tomato",
                "total_supplied_kg": 500,
                "total_sold_kg": 450,
                "avg_delivery_delay_min": 20
            }
        ]
    }
    ```
    """
    try:
        # Store data
        farmer_data_store[request.farmer_id] = {
            "farmer_name": request.farmer_name,
            "data": [d.dict() for d in request.data],
            "metadata": request.metadata,
            "updated_at": datetime.now().isoformat()
        }
        
        return {
            "status": "success",
            "message": f"Data received for {request.farmer_name}",
            "farmer_id": request.farmer_id,
            "records_received": len(request.data)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/analytics/generate", response_model=AnalyticsResponse)
async def generate_analytics(request: GenerateAnalyticsRequest):
    """
    Generate analytics and chart data for a farmer.
    Creao calls this after sending data to get insights + charts.
    
    Returns:
    - AI insights
    - Forecast
    - Recommendations
    - Chart data ready to display
    """
    try:
        # Get farmer data
        if request.farmer_id not in farmer_data_store:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for farmer {request.farmer_id}. Send data first using /api/data/send"
            )
        
        farmer_info = farmer_data_store[request.farmer_id]
        data_records = farmer_info["data"]
        
        # Convert to CSV format for analytics
        csv_lines = ["week_start,crop,total_supplied_kg,total_sold_kg,avg_delivery_delay_min"]
        for record in data_records:
            csv_lines.append(
                f"{record['week_start']},{record['crop']},{record['total_supplied_kg']},"
                f"{record['total_sold_kg']},{record.get('avg_delivery_delay_min', 0)}"
            )
        csv_string = "\n".join(csv_lines)
        
        # Save to temp file for analysis
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_string)
            temp_path = f.name
        
        try:
            # Generate AI analytics
            if GEMINI_AVAILABLE:
                analytics = analyze_csv(temp_path, crop=request.crop_filter)
                source = "gemini"
            else:
                analytics = _mock_analytics()
                source = "mock"
            
            # Generate chart data
            charts = _generate_chart_data(data_records, analytics)
            
            return AnalyticsResponse(
                status="success",
                farmer_id=request.farmer_id,
                farmer_name=farmer_info["farmer_name"],
                insights=analytics["insights"],
                forecast=analytics["forecast"],
                recommendations=analytics["recommendations"],
                charts=charts,
                source=source
            )
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/farmers")
async def list_farmers():
    """List all farmers with stored data"""
    farmers = []
    for farmer_id, info in farmer_data_store.items():
        farmers.append({
            "farmer_id": farmer_id,
            "farmer_name": info["farmer_name"],
            "records": len(info["data"]),
            "updated_at": info["updated_at"]
        })
    return {"farmers": farmers}

@app.get("/api/farmers/{farmer_id}/data")
async def get_farmer_data(farmer_id: str):
    """Get raw data for a specific farmer"""
    if farmer_id not in farmer_data_store:
        raise HTTPException(status_code=404, detail="Farmer not found")
    
    return farmer_data_store[farmer_id]

@app.delete("/api/farmers/{farmer_id}")
async def delete_farmer_data(farmer_id: str):
    """Delete farmer data"""
    if farmer_id in farmer_data_store:
        del farmer_data_store[farmer_id]
        return {"status": "success", "message": "Farmer data deleted"}
    raise HTTPException(status_code=404, detail="Farmer not found")

@app.get("/")
async def root():
    """API homepage with available endpoints"""
    return {
        "name": "Farm Analytics Dashboard API",
        "version": "1.0.0",
        "status": "running",
        "gemini_available": GEMINI_AVAILABLE,
        "farmers_count": len(farmer_data_store),
        "endpoints": {
            "send_data": "POST /api/data/send",
            "generate_analytics": "POST /api/analytics/generate",
            "list_farmers": "GET /api/farmers",
            "get_farmer_data": "GET /api/farmers/{id}/data",
            "delete_farmer": "DELETE /api/farmers/{id}",
            "health": "GET /api/health",
            "docs": "GET /docs",
            "openapi": "GET /openapi.json"
        },
        "quick_start": {
            "1_send_data": "POST /api/data/send with farmer_id and data",
            "2_get_analytics": "POST /api/analytics/generate with farmer_id",
            "3_view_docs": "Visit /docs for interactive API documentation"
        },
        "documentation": "/docs"
    }

@app.get("/api/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "gemini_available": GEMINI_AVAILABLE,
        "farmers_count": len(farmer_data_store)
    }

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _generate_chart_data(data_records: List[Dict], analytics: Dict) -> Dict[str, ChartData]:
    """Generate chart data from farmer records and analytics"""
    
    charts = {}
    
    # 1. Supply Trend Chart (Line)
    supply_data = []
    crops = set(r['crop'] for r in data_records)
    
    for crop in crops:
        crop_records = [r for r in data_records if r['crop'] == crop]
        crop_records.sort(key=lambda x: x['week_start'])
        
        for record in crop_records:
            supply_data.append({
                "x": record['week_start'],
                "y": record['total_supplied_kg'],
                "crop": crop
            })
    
    charts["supply_trend"] = ChartData(
        chart_type="line",
        title="Supply Trend",
        data=supply_data
    )
    
    # 2. Sales Performance Chart (Bar)
    sales_data = []
    for crop in crops:
        crop_records = [r for r in data_records if r['crop'] == crop]
        crop_records.sort(key=lambda x: x['week_start'])
        
        for record in crop_records:
            sales_data.append({
                "x": record['week_start'],
                "y": record['total_sold_kg'],
                "crop": crop
            })
    
    charts["sales_performance"] = ChartData(
        chart_type="bar",
        title="Sales Performance",
        data=sales_data
    )
    
    # 3. Forecast Chart (Line with predictions)
    forecast_data = []
    for forecast_item in analytics.get("forecast", []):
        forecast_data.append({
            "x": forecast_item['week_start'],
            "y": forecast_item['kg'],
            "crop": forecast_item['crop'],
            "is_forecast": True
        })
    
    charts["forecast"] = ChartData(
        chart_type="line",
        title="2-Week Forecast",
        data=forecast_data
    )
    
    # 4. Crop Distribution Chart (Pie)
    crop_totals = {}
    for record in data_records:
        crop = record['crop']
        crop_totals[crop] = crop_totals.get(crop, 0) + record['total_supplied_kg']
    
    pie_data = [
        {"label": crop, "value": total}
        for crop, total in crop_totals.items()
    ]
    
    charts["distribution"] = ChartData(
        chart_type="pie",
        title="Supply Distribution by Crop",
        data=pie_data
    )
    
    return charts

def _mock_analytics():
    """Mock analytics for testing"""
    return {
        "insights": [
            {"title": "Strong Demand", "explanation": "Sales are consistently high"},
            {"title": "Efficient Operations", "explanation": "Delivery times are improving"}
        ],
        "forecast": [
            {"week_start": "2025-10-01", "crop": "tomato", "kg": 610},
            {"week_start": "2025-10-08", "crop": "tomato", "kg": 620}
        ],
        "recommendations": [
            "Focus on high-demand crops",
            "Optimize delivery routes",
            "Increase inventory by 10%"
        ]
    }

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print("="*60)
    print("🚀 Dashboard API Server")
    print("="*60)
    print("\n📡 API Endpoints:")
    print("   POST   /api/data/send           - Creao sends farmer data")
    print("   POST   /api/analytics/generate  - Generate analytics + charts")
    print("   GET    /api/farmers             - List all farmers")
    print("   GET    /api/farmers/{id}/data   - Get farmer data")
    print("   DELETE /api/farmers/{id}        - Delete farmer data")
    print("   GET    /api/health              - Health check")
    print("\n📚 API Docs:")
    print("   http://localhost:8000/docs")
    print("\n🌐 CORS: Enabled for all origins")
    print("   (Configure for production)")
    print("\n⏹️  Press Ctrl+C to stop\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

