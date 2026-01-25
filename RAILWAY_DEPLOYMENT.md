# Railway Deployment - Quick Start

## Prerequisites
- GitHub account
- Railway account (sign up at https://railway.app)

## Step 1: Prepare Your Code

1. **Create .gitignore**
```bash
cat > /app/.gitignore << 'EOF'
.env
__pycache__/
*.pyc
.DS_Store
*.log
venv/
.venv/
*.sqlite
.git
app_old_backup.py
EOF
```

2. **Initialize Git Repository**
```bash
cd /app
git init
git add .
git commit -m "Initial commit - ChitFund Management System"
```

## Step 2: Push to GitHub

1. Create a new repository on GitHub: https://github.com/new
   - Name: `chitfund-app`
   - Keep it private or public (your choice)
   - Don't initialize with README (we already have code)

2. Push your code:
```bash
git remote add origin https://github.com/YOUR_USERNAME/chitfund-app.git
git branch -M main
git push -u origin main
```

## Step 3: Deploy on Railway

1. **Go to Railway:** https://railway.app
2. **Click "Start a New Project"**
3. **Select "Deploy from GitHub repo"**
4. **Choose your `chitfund-app` repository**
5. Railway will automatically detect it's a Python app and start deploying

## Step 4: Add MongoDB

1. In your Railway project dashboard
2. Click **"+ New"** button
3. Select **"Database"** → **"Add MongoDB"**
4. Railway will provision MongoDB automatically
5. MongoDB connection URL will be available as `MONGO_URL`

## Step 5: Configure Environment Variables

1. Click on your **web service** (not MongoDB)
2. Go to **"Variables"** tab
3. Add these variables:

```
SECRET_KEY=wueEQ7d8vF4nfkWjTl2tbgq6U4a4gbwPAd6EKdPG7VI
DEFAULT_ADMIN_PASSWORD=nitesh2025
FLASK_ENV=production
MONGO_DB=chitfund_db
```

4. For `MONGO_URI`:
   - Click **"+ New Variable"**
   - Select **"Reference Variable"**
   - Choose: `MongoDB.MONGO_URL`
   - Name it: `MONGO_URI`

This will automatically use Railway's MongoDB connection string.

## Step 6: Update Database Connection (Important!)

Railway provides MongoDB URL in a different format. Update your database.py:

1. Open `/app/database.py`
2. Update the MongoDB connection code:

```python
# MongoDB Connection
MONGO_URI = os.getenv('MONGO_URI') or os.getenv('MONGO_URL')  # Railway uses MONGO_URL
MONGO_DB = os.getenv('MONGO_DB')

if not MONGO_URI:
    raise ValueError("MONGO_URI or MONGO_URL environment variable is required")
if not MONGO_DB:
    MONGO_DB = 'chitfund_db'  # Default database name

# Parse the MongoDB URI and add database name if not present
if MONGO_DB and MONGO_DB not in MONGO_URI:
    if '?' in MONGO_URI:
        MONGO_URI = MONGO_URI.replace('?', f'/{MONGO_DB}?')
    else:
        MONGO_URI = f"{MONGO_URI}/{MONGO_DB}"

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
```

3. Commit and push:
```bash
git add database.py
git commit -m "Update MongoDB connection for Railway"
git push
```

Railway will automatically redeploy.

## Step 7: Get Your URL

1. In Railway dashboard, go to **"Settings"** tab
2. Under **"Domains"**, you'll see:
   - A Railway-provided domain: `yourapp.railway.app`
   - Option to add custom domain

Your app will be live at: `https://yourapp.railway.app`

## Step 8: Migrate Data

After deployment, migrate your data:

### Option A: Using Railway CLI

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run migration
railway run python migrate_data.py
```

### Option B: Manually via Python

Connect to production MongoDB and run migration script locally:

```bash
# Set production MONGO_URI
export MONGO_URI="your-railway-mongo-url"
export MONGO_DB="chitfund_db"

# Run migration
python migrate_data.py
```

## Step 9: Test Your Deployment

1. Visit your Railway URL: `https://yourapp.railway.app`
2. You should see the login page
3. Login with:
   - Username: `admin`
   - Password: `nitesh2025`
4. Test all features

## Troubleshooting

### Check Logs
```bash
railway logs
```

Or in Railway dashboard → "Deployments" → Click latest deployment → "View Logs"

### Common Issues

**Issue: "Can't connect to MongoDB"**
Solution: Make sure MONGO_URI variable is set correctly in Railway

**Issue: "Application Error"**
Solution: Check logs for specific error. Usually missing environment variables.

**Issue: "502 Bad Gateway"**
Solution: App is starting up. Wait 1-2 minutes and refresh.

### Restart Service

In Railway dashboard:
1. Go to your service
2. Click "Deployments"
3. Click "Redeploy" on latest deployment

## Custom Domain (Optional)

1. Buy domain from Namecheap/GoDaddy
2. In Railway → Settings → Domains → "Custom Domain"
3. Add your domain: `chitfund.com`
4. Configure DNS:
   - Add CNAME record pointing to Railway domain
   - Wait for DNS propagation (5-30 minutes)

## Cost

- **First $5/month:** FREE
- **After that:** ~$10-15/month
  - Web service: ~$5/month
  - MongoDB: ~$5-10/month
  - Total: ~$10-15/month

## Benefits of Railway

✅ Automatic deployments from GitHub  
✅ Built-in MongoDB  
✅ Free SSL certificate  
✅ Environment variables management  
✅ Easy rollback to previous versions  
✅ Automatic scaling  
✅ Zero-downtime deployments  

## Next Steps

1. ✅ Set up monitoring
2. ✅ Add custom domain
3. ✅ Set up backups (Railway auto-backs up MongoDB)
4. ✅ Configure alerts
5. ✅ Add team members (if needed)

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- Railway Support: help@railway.app

---

**Your ChitFund app is now live on Railway!** 🚀

Access it at: `https://yourapp.railway.app`
