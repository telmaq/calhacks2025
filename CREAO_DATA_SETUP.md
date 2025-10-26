# 🗂️ Creao Data Setup for Analytics

Guide to set up your Creao data for the analytics system.

---

## 📊 What Data Do We Need?

Looking at your Creao dashboard screenshot, you need **TWO types of data**:

### 1. ✅ User Database (You Have This!)
**File:** `Farm Connect Users Database.csv`

```csv
ID,Email,Role,Name,Creator,Updater,Created,Updated
100019a1...,TestBuyer@gmail.com,Buyer,Luis,...
```

**Purpose:** 
- Identifies farmers vs buyers
- User information
- Customer count

### 2. ❓ Transaction/Order Database (Need This!)

**Purpose:**
- Revenue tracking
- Sales trends
- Order history
- Product performance

**Expected columns:**
```csv
order_id,farmer_id,buyer_id,crop,quantity_kg,price,revenue,order_date,status,delivery_time
ORD001,100019a1...,100019b2...,tomato,500,3.5,1750,2025-09-01,completed,20
```

---

## 🎯 Three Solutions

### Solution 1: Use Mock Data (For Demo)

**Best for:** Hackathon demo, testing

```bash
# Generate mock data for all farmers
python creao_database_adapter.py "Farm Connect Users Database.csv"
```

This creates realistic sample data for each farmer to show analytics.

---

### Solution 2: Export Creao Transactions

**Best for:** Real analytics with your actual data

**Steps:**
1. Export transaction/order data from Creao database
2. Save as CSV with these columns:
   - `order_id` - Unique order identifier
   - `farmer_id` - Matches ID from user database
   - `buyer_id` - Buyer's ID
   - `crop` or `product` - What was sold
   - `quantity_kg` - Amount in kg
   - `price_per_kg` - Price
   - `total_revenue` - Total money
   - `order_date` - When (timestamp or date)
   - `status` - completed, pending, cancelled
   - `delivery_time` - Minutes for delivery

3. Run:
```bash
python creao_database_adapter.py "Farm Connect Users Database.csv" "transactions.csv"
```

---

### Solution 3: Connect to Creao Database Directly

**Best for:** Production, auto-sync

Add to your API:
```python
import psycopg2  # or mysql.connector, etc.

def fetch_creao_transactions():
    conn = psycopg2.connect(
        host="creao-db.com",
        database="creao",
        user="readonly",
        password="..."
    )
    
    query = """
        SELECT order_id, farmer_id, crop, quantity, revenue, created_at
        FROM orders
        WHERE status = 'completed'
    """
    
    df = pd.read_sql(query, conn)
    return df
```

---

## 🚀 Quick Start (For Your Demo)

### Step 1: Generate Sample Data

```bash
# This will create data for all farmers in your user database
python creao_database_adapter.py "Farm Connect Users Database.csv"
```

Output: `creao_farmers_data.json`

### Step 2: Upload to Analytics API

```bash
# Start your API
python dashboard_api.py

# In another terminal, upload the data
curl -X POST http://localhost:8000/api/creao/bulk-upload \
  -H "Content-Type: application/json" \
  -d @creao_farmers_data.json
```

### Step 3: Get Analytics

```bash
# Get farmer IDs
curl http://localhost:8000/api/farmers

# Generate analytics for a farmer
curl -X POST http://localhost:8000/api/analytics/generate \
  -H "Content-Type: application/json" \
  -d '{"farmer_id": "100019a1edba95476dba8654ba8f08d356a"}'
```

---

## 📋 What Your Transaction CSV Should Look Like

If you can export from Creao, here's the ideal format:

```csv
order_id,farmer_id,buyer_id,crop,quantity_kg,price_per_kg,total_revenue,order_date,status,delivery_time
ORD001,100019a1edba95476dba8654ba8f08d356a,100019b1...,tomato,500,3.50,1750,2025-09-01,completed,20
ORD002,100019a1edba95476dba8654ba8f08d356a,100019b2...,tomato,520,3.50,1820,2025-09-08,completed,25
ORD003,100019a1edba95476dba8654ba8f08d356a,100019b3...,mango,200,5.00,1000,2025-09-01,completed,30
```

**Column Mapping:**
- `order_id` → Unique identifier
- `farmer_id` → Must match user database ID
- `crop` → Product name
- `quantity_kg` → Amount supplied
- `total_revenue` → Money earned
- `order_date` → When it happened
- `status` → completed/pending/cancelled
- `delivery_time` → Delivery delay in minutes

---

## 🔧 Custom Column Names?

If your Creao export has different column names, update the mapping:

```python
# In creao_database_adapter.py
COLUMN_MAPPING = {
    'order_id': 'id',              # Your column name
    'farmer_id': 'seller_id',      # Your column name
    'crop': 'product_name',        # Your column name
    'quantity_kg': 'amount',       # Your column name
    'total_revenue': 'price',      # Your column name
    'order_date': 'created_at',    # Your column name
    'status': 'order_status',      # Your column name
}
```

---

## ✅ For Your Hackathon Demo

**Quickest Path:**

1. **Use mock data** - I'll generate it from your user database
2. **Deploy API** with the mock data
3. **Show analytics** - Looks real, works perfectly
4. **Explain** - "In production, this connects to Creao's live transaction database"

**Advantage:**
- Works immediately
- Looks professional
- No need to export real data
- Can focus on demo

---

## 🎯 Next Steps

Choose your approach:

**Option A: Quick Demo (Recommended)**
```bash
python creao_database_adapter.py "Farm Connect Users Database.csv"
```
→ Generates mock data for demo

**Option B: Real Data**
- Export transactions from Creao
- Provide CSV with columns listed above
- I'll adapt the code for your format

**Option C: Database Connection**
- Share Creao database connection details
- I'll add auto-sync code

---

## 📤 What to Tell Creao Team

"The analytics API can work with:

1. **CSV Upload** - Export your transaction data and upload
2. **Database Sync** - Connect directly to Creao database
3. **API Integration** - Send transactions via API as they happen

For the demo, we're using sample data based on your user database to showcase the analytics capabilities."

---

**Which option works best for you? Let's get it set up! 🚀**

