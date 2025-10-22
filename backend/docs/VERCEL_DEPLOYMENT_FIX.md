# Vercel Deployment Fix - PostgreSQL Driver Issue

## Problem

When deploying to Vercel, you encountered this error:

```
ModuleNotFoundError: No module named 'psycopg2'
```

## Root Cause

`psycopg2-binary` is a compiled C extension that doesn't work well in Vercel's serverless environment. Serverless platforms have strict limitations on binary dependencies.

## Solution

The application now **automatically selects the best PostgreSQL driver**:

### 1. Dual Driver Support

**requirements.txt** now includes both drivers:

```txt
psycopg2-binary==2.9.9  # For local development
psycopg==3.1.18         # For Serverless environments (pure Python)
```

### 2. Automatic Driver Selection

**app/db/database.py** now intelligently chooses the driver:

```python
# Priority order:
1. psycopg (v3)     → Pure Python, works in Serverless ✅
2. psycopg2-binary  → Fallback for local development ✅
```

**How it works:**
- If `psycopg` is available → Use it (URL becomes `postgresql+psycopg://...`)
- If only `psycopg2` is available → Use it (URL stays `postgresql://...`)
- Logs the driver being used for debugging

### 3. What You'll See

**In Vercel (Serverless):**
```
[OK] Using PostgreSQL database
[OK] Using psycopg (v3) driver for PostgreSQL
```

**In Local Development:**
```
[OK] Using PostgreSQL database
[OK] Using psycopg (v3) driver for PostgreSQL
```
or
```
[OK] Using PostgreSQL database
[OK] Using psycopg2 driver for PostgreSQL
```

## Deployment Steps

### 1. Update Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Test Locally

```bash
# Set PostgreSQL URL
export STORAGE_DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Start the server
python -m uvicorn app.main:app --reload
```

Check the console output for driver confirmation.

### 3. Initialize Database Tables

**IMPORTANT**: Before deploying to Vercel, you must initialize the database tables in your PostgreSQL database.

```bash
# Set your production database URL
export STORAGE_DATABASE_URL=postgresql://user:pass@your-db-host:5432/dbname

# Run the initialization script
cd backend
python init_database.py
```

You should see:
```
============================================================
Database Initialization Script
============================================================

[SUCCESS] Database tables created successfully!

Created tables:
  - users
  - articles
  - insights
  - collections
  - sparks
  - meta_analysis
  - thinking_lens
  - insight_history
  - preferences
============================================================
```

### 4. Deploy to Vercel

```bash
# Commit changes
git add .
git commit -m "Fix PostgreSQL driver for Serverless deployment"
git push

# Vercel will auto-deploy
```

### 5. Verify Deployment

Check Vercel deployment logs. You should see:
```
[OK] Using PostgreSQL database
[OK] Using psycopg (v3) driver for PostgreSQL
[OK] Database initialization completed
```

## Environment Variables

Make sure your Vercel project has:

```bash
STORAGE_DATABASE_URL=postgresql://user:pass@your-db-host:5432/dbname
OPENAI_API_KEY=sk-...
SECRET_KEY=your-secret-key
```

## Recommended PostgreSQL Services for Vercel

For Serverless deployments, use managed PostgreSQL with connection pooling:

1. **Supabase** (Recommended)
   - Built-in connection pooling
   - Free tier available
   - URL format: `postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres`

2. **Neon**
   - Serverless PostgreSQL
   - Auto-scaling
   - URL format: `postgresql://[user]:[password]@[endpoint].neon.tech/[dbname]`

3. **PlanetScale**
   - MySQL-compatible (requires different driver)
   - Great for serverless

4. **Railway**
   - Simple setup
   - Built-in PostgreSQL

## Common Errors

### Error: "relation 'users' does not exist"

**Problem**: The database tables haven't been created yet.

**Solution**:
```bash
# 1. Set your production database URL
export STORAGE_DATABASE_URL=postgresql://user:pass@your-db:5432/dbname

# 2. Initialize tables
cd backend
python init_database.py

# 3. Redeploy
git push
```

**Why this happens**:
- PostgreSQL databases don't automatically create tables
- The application tries to query tables that don't exist yet
- You must run the initialization script first

## Troubleshooting

### Still seeing psycopg2 error?

1. **Check requirements.txt** contains:
   ```
   psycopg==3.1.18
   ```

2. **Force reinstall** on Vercel:
   - Go to Vercel Dashboard → Your Project → Settings → General
   - Toggle "Clear Build Cache and Deploy"

3. **Check build logs** for installation errors

### Driver not found warning locally?

Install dependencies:
```bash
pip install -r requirements.txt
```

### Want to force a specific driver?

**Force psycopg (v3):**
```bash
pip uninstall psycopg2-binary
```

**Force psycopg2:**
```bash
pip uninstall psycopg
```

## Technical Details

### Why psycopg (v3)?

- **Pure Python**: No C compilation required
- **Serverless-friendly**: Works in AWS Lambda, Vercel, Google Cloud Functions
- **Modern**: Built for PostgreSQL 9.5+
- **Maintained**: Active development, better than psycopg2

### URL Format Conversion

The system automatically converts:
```
postgresql://user:pass@host:5432/db
↓
postgresql+psycopg://user:pass@host:5432/db
```

This tells SQLAlchemy to use the `psycopg` driver instead of the default `psycopg2`.

### Compatibility

- ✅ SQLAlchemy 2.0+
- ✅ PostgreSQL 9.5+
- ✅ Python 3.8+
- ✅ Vercel Serverless Functions
- ✅ AWS Lambda
- ✅ Google Cloud Functions
- ✅ Local development

## Summary

The fix is **automatic and backward-compatible**:
- No code changes needed in your application logic
- Works in both local and serverless environments
- Logs clearly show which driver is being used
- Falls back gracefully if a driver is missing

Just deploy, and it will work! 🚀
