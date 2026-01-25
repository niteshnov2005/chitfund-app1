# Heroku Deployment - Quick Start

## Prerequisites
- Heroku account (sign up at https://heroku.com)
- Git installed
- MongoDB Atlas account (free tier)

## Step 1: Install Heroku CLI

### Linux/Mac:
```bash
curl https://cli-assets.heroku.com/install.sh | sh
```

### Windows:
Download installer from: https://devcenter.heroku.com/articles/heroku-cli

## Step 2: Login to Heroku

```bash
heroku login
```

This will open a browser window to login.

## Step 3: Create MongoDB on Atlas (Free)

1. **Go to:** https://www.mongodb.com/cloud/atlas/register
2. **Sign up** for free account
3. **Create Cluster:**
   - Choose **FREE tier** (M0 Sandbox)
   - Select closest region
   - Cluster name: `chitfund`
4. **Create Database User:**
   - Database Access → Add User
   - Username: `chitfund_user`
   - Password: `YourStrongPassword123`
   - Role: Read/Write any database
5. **Allow Network Access:**
   - Network Access → Add IP Address
   - Select **"Allow Access from Anywhere"** (0.0.0.0/0)
6. **Get Connection String:**
   - Clusters → Connect → Connect your application
   - Copy connection string:
   ```
   mongodb+srv://chitfund_user:<password>@cluster.mongodb.net/chitfund_db?retryWrites=true&w=majority
   ```
   - Replace `<password>` with your actual password

## Step 4: Prepare Your Code

```bash
cd /app

# Create .gitignore
cat > .gitignore << 'EOF'
.env
__pycache__/
*.pyc
.DS_Store
*.log
venv/
.venv/
*.sqlite
app_old_backup.py
EOF

# Initialize git
git init
git add .
git commit -m "Initial commit for Heroku"
```

## Step 5: Create Heroku App

```bash
heroku create chitfund-yourname
```

Replace `yourname` with your name or any unique identifier.

This creates:
- Heroku app: `chitfund-yourname`
- URL: `https://chitfund-yourname.herokuapp.com`

## Step 6: Set Environment Variables

```bash
heroku config:set SECRET_KEY=wueEQ7d8vF4nfkWjTl2tbgq6U4a4gbwPAd6EKdPG7VI

heroku config:set DEFAULT_ADMIN_PASSWORD=nitesh2025

heroku config:set FLASK_ENV=production

heroku config:set MONGO_DB=chitfund_db

# Add your MongoDB Atlas connection string (replace with yours)
heroku config:set MONGO_URI="mongodb+srv://chitfund_user:YourPassword123@cluster.mongodb.net/chitfund_db?retryWrites=true&w=majority"
```

## Step 7: Deploy to Heroku

```bash
# Add Heroku remote
heroku git:remote -a chitfund-yourname

# Deploy
git push heroku main
```

If you're on `master` branch instead of `main`:
```bash
git push heroku master
```

## Step 8: Scale Up Dyno

```bash
heroku ps:scale web=1
```

## Step 9: Open Your App

```bash
heroku open
```

Your app will open in browser at: `https://chitfund-yourname.herokuapp.com`

## Step 10: Migrate Data

### Option A: Using Heroku CLI

```bash
heroku run python migrate_data.py
```

### Option B: Run Locally

```bash
# Get your Heroku MongoDB URI
heroku config:get MONGO_URI

# Set it locally
export MONGO_URI="your-heroku-mongo-uri"
export MONGO_DB="chitfund_db"

# Run migration
python migrate_data.py
```

## Step 11: Test Your App

1. Visit: `https://chitfund-yourname.herokuapp.com`
2. Login with:
   - Username: `admin`
   - Password: `nitesh2025`
3. Test all features

## Viewing Logs

```bash
heroku logs --tail
```

This shows real-time logs. Press Ctrl+C to stop.

## Troubleshooting

### Check App Status
```bash
heroku ps
```

### Restart App
```bash
heroku restart
```

### Common Issues

**Issue: "Application Error"**
```bash
# Check logs
heroku logs --tail

# Usually means missing environment variables
heroku config
```

**Issue: "Can't connect to MongoDB"**
```bash
# Verify MongoDB URI
heroku config:get MONGO_URI

# Test connection
heroku run python -c "from database import db; print(db.list_collection_names())"
```

**Issue: "Deployment failed"**
```bash
# Check build logs
heroku logs --tail

# Usually means missing dependencies
# Make sure requirements.txt is updated
```

## Heroku Dashboard

Access your app dashboard: https://dashboard.heroku.com/apps/chitfund-yourname

From there you can:
- View logs
- Manage environment variables
- Scale dynos
- Add collaborators
- View metrics

## Custom Domain

1. Buy domain from Namecheap/GoDaddy
2. Add domain to Heroku:
```bash
heroku domains:add www.yourdomain.com
```
3. Configure DNS:
```
Type: CNAME
Name: www
Value: chitfund-yourname.herokuapp.com
```

## Automatic Deployments from GitHub

1. **Connect GitHub:**
   - Dashboard → Deploy tab
   - Connect to GitHub
   - Select your repository

2. **Enable Auto Deploy:**
   - Enable "Automatic Deploys" from main branch
   - Every push to GitHub will auto-deploy

## Cost

**Free Tier (Eco Dynos):**
- FREE for 1000 hours/month
- App sleeps after 30 min inactivity
- Wakes up on first request (takes 5-10 seconds)

**Paid Tier (Basic Dynos):**
- $7/month
- Always on, no sleeping
- Better performance

**MongoDB:**
- MongoDB Atlas FREE tier: 512MB (perfect for this app)

**Total:** FREE or $7/month for always-on

## Upgrading Your App

When you have code changes:

```bash
git add .
git commit -m "Update feature"
git push heroku main
```

Heroku automatically redeploys!

## Rollback to Previous Version

```bash
# View releases
heroku releases

# Rollback to previous version
heroku rollback
```

## Monitoring

### View Metrics
```bash
heroku logs --tail
```

### Check Dyno Status
```bash
heroku ps
```

### Restart Dyno
```bash
heroku restart
```

## Benefits of Heroku

✅ Very popular and reliable  
✅ Great documentation  
✅ Easy CLI  
✅ Auto SSL certificate  
✅ Easy rollbacks  
✅ Add-ons marketplace  
✅ Great for production  

## Support

- Heroku Docs: https://devcenter.heroku.com
- Heroku Support: https://help.heroku.com
- Status: https://status.heroku.com

---

## Quick Reference

### Essential Commands

```bash
# Deploy
git push heroku main

# View logs
heroku logs --tail

# Run command
heroku run python migrate_data.py

# Restart
heroku restart

# Check status
heroku ps

# Open app
heroku open

# Check config
heroku config
```

---

**Your ChitFund app is now live on Heroku!** 🚀

Access at: `https://chitfund-yourname.herokuapp.com`

**Login:**
- Username: `admin`
- Password: `nitesh2025`
