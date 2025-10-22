# Quick Fix: "relation 'users' does not exist" Error

## Your Current Issue

You're getting this error on Vercel:
```
psycopg2.errors.UndefinedTable: relation "users" does not exist
```

This means your PostgreSQL database exists, but the **tables haven't been created yet**.

---

## Fix It Now (3 Steps)

### Step 1: Get Your Database Connection String

From your Vercel environment variables, copy the value of:
```
STORAGE_DATABASE_URL
```

It should look like:
```
postgresql://username:password@host:5432/database
```

### Step 2: Initialize Database Tables

Run this on your **local machine**:

```bash
# Navigate to backend folder
cd backend

# Set the database URL (use your actual production URL)
# Windows PowerShell:
$env:STORAGE_DATABASE_URL="postgresql://your-user:your-pass@your-host:5432/your-db"

# Windows CMD:
set STORAGE_DATABASE_URL=postgresql://your-user:your-pass@your-host:5432/your-db

# Mac/Linux:
export STORAGE_DATABASE_URL=postgresql://your-user:your-pass@your-host:5432/your-db

# Run the initialization script
python init_database.py
```

### Step 3: Verify

You should see:
```
============================================================
Database Initialization Script
============================================================

Database URL: postgresql://...
Database Type: PostgreSQL

Initializing database tables...

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

---

## That's It!

Your Vercel app should now work! The tables are created and ready.

**No need to redeploy** - just refresh your app and try logging in again.

---

## Why Did This Happen?

1. SQLite (local dev) automatically creates tables on first access
2. PostgreSQL (production) requires explicit table creation
3. The app tries to create tables on startup, but in Vercel's serverless environment, this doesn't always work reliably
4. Solution: Run the initialization script once before deploying

---

## Troubleshooting

### Can't connect to database?

**Check:**
- Database URL is correct (copy from Vercel exactly)
- Database server is running
- Your IP is allowed (some services like Supabase have IP whitelists)
- Network/firewall isn't blocking port 5432

### Script fails with authentication error?

**Check:**
- Username and password are correct
- User has permissions to create tables
- Database exists

### Script succeeds but still getting error on Vercel?

**Try:**
- Wait 1-2 minutes for Vercel to restart
- Check Vercel logs for any other errors
- Verify `STORAGE_DATABASE_URL` is set in Vercel environment variables
- Trigger a redeploy in Vercel dashboard

---

## Need More Help?

See:
- `DATABASE_SETUP.md` - Full database setup guide
- `VERCEL_DEPLOYMENT_FIX.md` - Complete Vercel deployment guide
