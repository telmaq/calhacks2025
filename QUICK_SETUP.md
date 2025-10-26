# Quick Setup - 30 Minutes to Production

## 🚀 Step 1: Install Supabase Library (2 min)

```bash
pip install supabase
```

## 🗄️ Step 2: Create Supabase Table (5 min)

1. Go to https://supabase.com
2. Create new project or use existing
3. Go to SQL Editor
4. Run this SQL:

```sql
CREATE TABLE produce (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    farmer_id TEXT NOT NULL,
    produce_name TEXT NOT NULL,
    weight DECIMAL(10, 2) NOT NULL,
    unit TEXT NOT NULL,
    weight_confidence DECIMAL(3, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    creao_logged BOOLEAN DEFAULT FALSE
);
```

## 🔑 Step 3: Add Environment Variables (2 min)

Add to your `.env` file or Railway config:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
```

Get these from: Supabase Project → Settings → API

## ✅ Done! Test It (5 min)

```bash
# 1. Run server
python app.py

# 2. Open browser
http://localhost:8000/test_weight_capture.html

# 3. Capture an image
# 4. Check Supabase dashboard for new record!
```

## 📝 What Happens Now

When your API processes an image:

1. ✅ Claude extracts weight
2. ✅ Saves to Supabase `produce` table
3. ✅ Returns JSON with `supabase_id`
4. ✅ Creao receives data and can log to its own DB

## 🎯 Next Step: Connect Creao

In Creao, add button that opens:

```javascript
window.open("https://your-api.com/test_weight_capture.html?farmer_id=123");
```

That's it! 🎉
