# 🔗 Integrating with Creao Database

Guide to connect the analytics API with your actual Creao database.

---

## 🎯 Overview

Instead of sending data via API calls, the analytics will read directly from your Creao database CSV file.

---

## 📊 Option 1: Creao Exports CSV to API

### How It Works

```
Creao Database → Export CSV → Upload to API → Analytics Generated
```

### Implementation

Add this endpoint to `dashboard_api.py`:

```python
from fastapi import UploadFile, File

@app.post("/api/data/upload-csv")
async def upload_creao_database(
    file: UploadFile = File(...),
    source: str = "creao_database"
):
    """
    Upload Creao database CSV file for analytics.
    Automatically processes all farmers' data.
    """
    try:
        # Read uploaded CSV
        contents = await file.read()
        csv_string = contents.decode('utf-8')
        
        # Parse CSV
        import pandas as pd
        from io import StringIO
        df = pd.read_csv(StringIO(csv_string))
        
        # Expected columns (adjust based on your Creao DB structure):
        # user_id, farmer_name, transaction_date, crop, quantity_kg, 
        # revenue, order_status, delivery_time, etc.
        
        # Group by farmer and process
        farmers_processed = []
        
        for farmer_id in df['user_id'].unique():
            farmer_data = df[df['user_id'] == farmer_id]
            
            # Convert to our format
            weekly_data = []
            for _, row in farmer_data.iterrows():
                weekly_data.append({
                    "week_start": row.get('transaction_date', ''),
                    "crop": row.get('crop', ''),
                    "total_supplied_kg": row.get('quantity_kg', 0),
                    "total_sold_kg": row.get('quantity_sold_kg', 0),
                    "avg_delivery_delay_min": row.get('delivery_time', 0)
                })
            
            # Store farmer data
            farmer_data_store[farmer_id] = {
                "farmer_name": farmer_data.iloc[0].get('farmer_name', f'Farmer {farmer_id}'),
                "data": weekly_data,
                "metadata": {"source": "creao_database"},
                "updated_at": datetime.now().isoformat()
            }
            
            farmers_processed.append(farmer_id)
        
        return {
            "status": "success",
            "farmers_processed": len(farmers_processed),
            "farmer_ids": farmers_processed,
            "message": f"Processed data for {len(farmers_processed)} farmers"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Usage in Creao

```javascript
// Export database to CSV, then upload
async function syncCreaoDatabase() {
  const csvFile = await exportDatabaseToCSV();
  
  const formData = new FormData();
  formData.append('file', csvFile);
  
  const response = await fetch('https://your-api.com/api/data/upload-csv', {
    method: 'POST',
    body: formData
  });
  
  const result = await response.json();
  console.log(`Synced ${result.farmers_processed} farmers`);
}
```

---

## 📊 Option 2: Direct Database Connection

If Creao database is accessible via URL or API:

```python
import requests
import pandas as pd

@app.post("/api/sync-creao-database")
async def sync_from_creao_api(
    creao_api_url: str,
    api_key: Optional[str] = None
):
    """
    Fetch data directly from Creao database API
    """
    try:
        headers = {}
        if api_key:
            headers['Authorization'] = f'Bearer {api_key}'
        
        # Fetch from Creao
        response = requests.get(creao_api_url, headers=headers)
        data = response.json()
        
        # Process and store
        # ... (same as above)
        
        return {"status": "success", "farmers_synced": len(data)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 📊 Option 3: Scheduled Sync (Recommended)

### Setup Automatic Sync

```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()

def sync_creao_database():
    """Run every hour to sync Creao database"""
    try:
        # Fetch from Creao database URL
        response = requests.get(os.getenv('CREAO_DATABASE_URL'))
        csv_data = response.text
        
        # Process and update farmer_data_store
        # ... (same processing logic)
        
        print(f"✅ Synced Creao database at {datetime.now()}")
    except Exception as e:
        print(f"❌ Sync failed: {e}")

# Schedule every hour
scheduler.add_job(sync_creao_database, 'interval', hours=1)
scheduler.start()
```

---

## 🗂️ Creao Database Format

### Expected CSV Structure

Your `datasbase.csv` should have columns like:

```csv
user_id,farmer_name,transaction_date,crop,quantity_kg,quantity_sold_kg,revenue,delivery_time
farmer001,John's Farm,2025-09-01,tomato,500,450,4500,20
farmer001,John's Farm,2025-09-08,tomato,520,480,4800,25
farmer002,Maria's Farm,2025-09-01,mango,200,180,3600,30
```

### Column Mapping

If your columns are different, update this mapping:

```python
COLUMN_MAPPING = {
    'user_id': 'user_id',           # Farmer ID
    'farmer_name': 'name',          # Farmer name
    'transaction_date': 'date',     # Date of transaction
    'crop': 'product',              # Crop/product name
    'quantity_kg': 'supplied',      # Amount supplied
    'quantity_sold_kg': 'sold',     # Amount sold
    'delivery_time': 'delay'        # Delivery delay in minutes
}
```

---

## 🚀 Complete Implementation

### Updated `dashboard_api.py`

Add this to your existing file:

```python
import pandas as pd
from io import StringIO
from fastapi import UploadFile, File

@app.post("/api/creao/upload-database")
async def upload_creao_database(
    file: UploadFile = File(...),
    column_mapping: Optional[Dict] = None
):
    """
    Upload Creao database CSV and process for all farmers.
    
    Example:
    Upload your datasbase.csv file and it will:
    1. Parse all farmers
    2. Convert to analytics format
    3. Store for analytics generation
    """
    try:
        contents = await file.read()
        csv_string = contents.decode('utf-8')
        
        df = pd.read_csv(StringIO(csv_string))
        
        # Default column mapping (adjust if needed)
        if column_mapping is None:
            column_mapping = {
                'user_id': 'user_id',
                'farmer_name': 'farmer_name',
                'transaction_date': 'transaction_date',
                'crop': 'crop',
                'quantity_kg': 'quantity_kg',
                'quantity_sold_kg': 'quantity_sold_kg',
                'delivery_time': 'delivery_time'
            }
        
        farmers_processed = 0
        
        # Group by farmer
        for farmer_id in df[column_mapping['user_id']].unique():
            farmer_df = df[df[column_mapping['user_id']] == farmer_id]
            
            # Convert to weekly format
            weekly_data = []
            for _, row in farmer_df.iterrows():
                weekly_data.append({
                    "week_start": str(row.get(column_mapping['transaction_date'], '')),
                    "crop": str(row.get(column_mapping['crop'], '')),
                    "total_supplied_kg": float(row.get(column_mapping['quantity_kg'], 0)),
                    "total_sold_kg": float(row.get(column_mapping['quantity_sold_kg'], 0)),
                    "avg_delivery_delay_min": float(row.get(column_mapping['delivery_time'], 0))
                })
            
            # Store
            farmer_data_store[str(farmer_id)] = {
                "farmer_name": str(farmer_df.iloc[0].get(column_mapping['farmer_name'], f'Farmer {farmer_id}')),
                "data": weekly_data,
                "metadata": {
                    "source": "creao_database",
                    "uploaded_at": datetime.now().isoformat(),
                    "records": len(weekly_data)
                },
                "updated_at": datetime.now().isoformat()
            }
            
            farmers_processed += 1
        
        return {
            "status": "success",
            "farmers_processed": farmers_processed,
            "total_records": len(df),
            "message": f"Successfully processed {farmers_processed} farmers from Creao database"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "hint": "Make sure your CSV has the correct columns"
        }

@app.get("/api/creao/database-info")
async def get_database_info():
    """Get information about uploaded Creao database"""
    return {
        "farmers_count": len(farmer_data_store),
        "farmers": [
            {
                "farmer_id": fid,
                "farmer_name": info["farmer_name"],
                "records": len(info["data"]),
                "updated_at": info["updated_at"]
            }
            for fid, info in farmer_data_store.items()
        ]
    }
```

---

## 🧪 Testing

### 1. Upload Your Database

```bash
curl -X POST https://your-api.com/api/creao/upload-database \
  -F "file=@datasbase.csv"
```

### 2. Check What Was Loaded

```bash
curl https://your-api.com/api/creao/database-info
```

### 3. Generate Analytics for a Farmer

```bash
curl -X POST https://your-api.com/api/analytics/generate \
  -H "Content-Type: application/json" \
  -d '{"farmer_id": "farmer001"}'
```

---

## 🔄 Workflow for Creao

### In Creao Admin Panel:

1. **Upload Database** (once or when updated):
   ```javascript
   const file = document.getElementById('csv-file').files[0];
   const formData = new FormData();
   formData.append('file', file);
   
   await fetch('https://your-api.com/api/creao/upload-database', {
     method: 'POST',
     body: formData
   });
   ```

2. **Get Analytics for Any Farmer**:
   ```javascript
   const response = await fetch('https://your-api.com/api/analytics/generate', {
     method: 'POST',
     headers: { 'Content-Type': 'application/json' },
     body: JSON.stringify({ farmer_id: selectedFarmerId })
   });
   
   const analytics = await response.json();
   // Display charts, insights, etc.
   ```

---

## 📋 Next Steps

1. **Share your `datasbase.csv` structure** - Show me the column names
2. **I'll update the code** to match your exact format
3. **Deploy with the new endpoint**
4. **Test with your real data**
5. **Share API with Creao team**

---

## 🎯 Alternative: Environment Variable

If your database is at a fixed URL:

```bash
# In Render.com environment variables
CREAO_DATABASE_URL=https://creao.com/api/export/database.csv
CREAO_API_KEY=your_api_key
```

Then the API auto-syncs on startup:

```python
@app.on_event("startup")
async def load_creao_database():
    """Load Creao database on startup"""
    url = os.getenv('CREAO_DATABASE_URL')
    if url:
        # Fetch and process
        # ... 
        print("✅ Loaded Creao database")
```

---

**Tell me the structure of your `datasbase.csv` and I'll customize the code exactly for it!**

