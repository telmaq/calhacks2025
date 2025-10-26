# Deployment Checklist - 5 Minutes to Live! 🚀

## ✅ Completed

- [x] Supabase client integrated
- [x] Database write function added
- [x] API response updated to include `supabase_id`
- [x] Libraries installed

## 📋 What You Need to Do (5 min)

### 1. Add Supabase Credentials to Environment

Add these to your `.env` file or Railway config:

```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-or-service-role-key
```

**Get credentials from:**

1. Go to https://supabase.com/dashboard
2. Select your project
3. Settings → API
4. Copy "Project URL" → `SUPABASE_URL`
5. Copy "anon public" key → `SUPABASE_KEY`

### 2. Create Database Table

In Supabase SQL Editor, run:

```sql
CREATE TABLE Product (
    id VARCHAR(255) PRIMARY KEY,
    seller_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(255) NOT NULL,
    price NUMERIC NOT NULL,
    unit VARCHAR(50) NOT NULL,
    stock_quantity INTEGER NOT NULL,
    image_url VARCHAR(2048),
    available BOOLEAN NOT NULL,
    data_creator VARCHAR(255) NOT NULL,
    data_updater VARCHAR(255) NOT NULL,
    create_time TIMESTAMP WITH TIME ZONE NOT NULL,
    update_time TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE INDEX idx_product_seller_id ON Product(seller_id);
CREATE INDEX idx_product_create_time ON Product(create_time DESC);
```

### 3. Test Locally (2 min)

```bash
# Terminal 1: Start server
python3 app.py

# Terminal 2: Open browser
open http://localhost:8000/test_weight_capture.html
```

**Test steps:**

1. Enter farmer ID: `test123`
2. Enter produce: `apples`
3. Click "Capture Weight"
4. Check Supabase dashboard for new record in Product table!

### 4. Deploy to Production

If deploying to Railway/Heroku:

```bash
# Commit changes
git add .
git commit -m "Add Supabase integration"

# Push to Railway
railway up
```

## 🎯 How It Works Now

```
1. Farmer clicks button in Creao
   ↓
2. Opens: your-api.com/test_weight_capture.html?farmer_id=123
   ↓
3. Farmer captures image of scale
   ↓
4. Your API processes with Claude OCR → extracts weight
   ↓
5. Saves to Supabase produce table ✅
   ↓
6. Returns JSON to Creao with supabase_id
   ↓
7. Creao logs to its own database
   ↓
8. Both databases synced! 🎉
```

## 🔍 Verify It Works

After capturing an image, check:

**In Supabase:**

```sql
SELECT * FROM Product ORDER BY create_time DESC LIMIT 5;
```

**In API Response:**

```json
{
  "status": "success",
  "farmer_id": "test123",
  "produce": {
    "name": "apples",
    "weight": 5.2,
    "unit": "kg"
  },
  "supabase_id": "uuid-here",
  "message": "Produce captured and logged to database"
}
```

## 🚨 Troubleshooting

**Error: "Supabase client not initialized"**

- Check `.env` file has `SUPABASE_URL` and `SUPABASE_KEY`
- Restart server: `python3 app.py`

**Error: "relation 'Product' does not exist"**

- Run the SQL schema in Supabase SQL Editor

**No data in Supabase:**

- Check server logs for errors
- Verify API is receiving requests
- Check Supabase RLS (Row Level Security) policies

## ✅ Ready to Deploy!

All code is complete. Just add credentials and deploy! 🚀
