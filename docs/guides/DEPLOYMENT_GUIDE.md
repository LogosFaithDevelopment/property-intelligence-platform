# 🚀 Production Deployment Guide

**Last Updated:** January 2025  
**Status:** Production-Ready Architecture

---

## 🏗️ Three-Tier Architecture (Recommended)

```
┌─────────────────────────────────────────────────────────────┐
│                     PRODUCTION STACK                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐      ┌─────────────┐      ┌─────────────┐ │
│  │   VERCEL    │      │   RAILWAY   │      │  SUPABASE   │ │
│  │  (Frontend) │ ───► │  (Backend)  │ ───► │ (Database)  │ │
│  └─────────────┘      └─────────────┘      └─────────────┘ │
│                                                               │
│  Next.js 14           FastAPI                PostgreSQL 15   │
│  React                Python 3.11           PostGIS          │
│  TypeScript           Uvicorn               Pgvector         │
│  Tailwind CSS         Alembic                                │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### **Why This Architecture?**

#### **✅ Vercel (Frontend)**

- **Best for Next.js**: Built by the Next.js team, zero config
- **Edge Network**: Global CDN, <100ms latency worldwide
- **Preview Deployments**: Every PR gets automatic preview URL
- **Generous Free Tier**: 100GB bandwidth/month (perfect for MVP)
- **Auto-scaling**: Handles traffic spikes automatically
- **Custom Domains**: Free SSL certificates

**Pricing:**

- Free: Hobby projects (sufficient for MVP testing)
- $20/month: Pro (for production with team collaboration)

#### **✅ Railway (Backend - Python/FastAPI)**

- **Native Python Support**: No cold starts (critical!)
- **Long-Running Processes**: Perfect for 30-60s enrichment workflows
- **Background Jobs**: Handles property analysis without timeouts
- **No Execution Limits**: Unlike Vercel serverless (10-60s timeout)
- **Docker Support**: Full control over runtime environment
- **Database Integration**: Can host PostgreSQL if needed

**Pricing (Updated 2025):**

- ⚠️ **No Free Tier Anymore**: Minimum $5/month (changed in 2024)
- $5-20/month: Typical for small-medium apps
- Pay-as-you-go: Scales with actual usage

**Why Not Vercel Serverless for Backend?**
| Issue | Vercel Serverless | Railway |
|-------|-------------------|---------|
| Timeout | 10s (Hobby), 60s (Pro) | Unlimited |
| Cold Starts | 200-500ms delay | None (always warm) |
| Enrichment | ❌ Fails (takes 30-60s) | ✅ Perfect |
| Background Jobs | ❌ Not supported | ✅ Native support |
| WebSockets | ❌ Limited | ✅ Full support |
| Cost for sustained traffic | Higher | Lower |

#### **✅ Supabase (Database - PostgreSQL)**

- **Managed PostgreSQL 15**: Auto-backups, automatic scaling
- **PostGIS Extension**: Geospatial queries for property locations
- **Connection Pooling**: Handles concurrent requests efficiently
- **Built-in Backups**: Automatic daily backups
- **Database GUI**: Visual table editor and SQL runner
- **Real-time**: Optional for live dashboards (future feature)

**Pricing:**

- Free: 500MB database, 2GB bandwidth (good for MVP testing)
- $25/month: Pro (8GB database, unlimited API requests)

---

## 🔐 Environment Variables Strategy

### **✅ Your Backend is Already Configured Correctly!**

Your `app/config.py` uses **best practices**:

```python
# CORS Configuration (app/config.py)
allowed_origins: List[str] = Field(
    default=["http://localhost:3000"],
    alias="ALLOWED_ORIGINS"
)

@validator("allowed_origins", pre=True)
def parse_cors_origins(cls, v):
    """Parse CORS origins from comma-separated string or list"""
    if isinstance(v, str):
        return [origin.strip() for origin in v.split(",")]
    return v
```

### **✅ Flexible CORS for Multiple Environments**

**Local Development (`.env`):**

```env
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

**Production (Railway Environment Variables):**

```env
ALLOWED_ORIGINS=https://logos-development.vercel.app,https://logos-development-staging.vercel.app
```

**With Preview Deployments (Vercel PRs):**

```env
ALLOWED_ORIGINS=https://logos-development.vercel.app,https://*.vercel.app
```

### **🎯 Recommended Environment Variable Setup**

#### **Development (.env - Local)**

```env
# Application
ENVIRONMENT=development
DEBUG=true
SECRET_KEY=your-local-secret-key-here

# Database (Local PostgreSQL or Supabase Free Tier)
DATABASE_URL=postgresql://user:password@localhost:5432/property_intelligence
REDIS_URL=redis://localhost:6379

# CORS (Local Frontend)
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Authentication
CLERK_SECRET_KEY=sk_test_...

# AI APIs
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Free Tier APIs
CENSUS_API_KEY=your_census_key
HUD_API_KEY=your_hud_key

# Professional APIs (Optional)
ATTOM_API_KEY=  # Add when ready
GOOGLE_MAPS_API_KEY=  # Add when ready
```

#### **Production (Railway Environment Variables)**

```env
# Application
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<generate-strong-secret>

# Database (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xxxx.supabase.co:5432/postgres
REDIS_URL=redis://red-xxx.render.com:6379

# CORS (Production Frontend URLs)
ALLOWED_ORIGINS=https://logos-development.vercel.app,https://*.vercel.app

# Authentication
CLERK_SECRET_KEY=sk_live_...  # Production Clerk key

# AI APIs
OPENAI_API_KEY=sk-...  # Production OpenAI key
OPENAI_MODEL=gpt-4o-mini

# All other API keys...
```

---

## 📦 Step-by-Step Deployment

### **Phase 1: Deploy Database (Supabase)**

1. **Create Supabase Project**

   ```bash
   # Go to: https://supabase.com/dashboard
   # Click: "New Project"
   # Name: property-intelligence-db
   # Region: Choose closest to your users
   # Database Password: Generate strong password
   ```

2. **Enable Extensions**

   ```sql
   -- In Supabase SQL Editor
   CREATE EXTENSION IF NOT EXISTS postgis;
   CREATE EXTENSION IF NOT EXISTS pg_trgm;
   CREATE EXTENSION IF NOT EXISTS btree_gist;
   ```

3. **Get Connection String**

   ```
   Settings → Database → Connection String (URI)

   postgresql://postgres:[YOUR-PASSWORD]@db.xxxx.supabase.co:5432/postgres
   ```

4. **Test Connection Locally**

   ```bash
   # Update your local .env
   DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xxxx.supabase.co:5432/postgres

   # Run migrations
   cd backend
   alembic upgrade head
   ```

---

### **Phase 2: Deploy Backend (Railway)**

1. **Create Railway Account**

   ```bash
   # Go to: https://railway.app
   # Sign up with GitHub
   # Cost: $5/month minimum (pay-as-you-go)
   ```

2. **Create New Project**

   ```bash
   # In Railway Dashboard:
   # Click: "New Project"
   # Select: "Deploy from GitHub repo"
   # Choose: property-intelligence-platform repository
   # Select: backend/ directory
   ```

3. **Configure Build Settings**

   ```toml
   # Railway will auto-detect Python
   # Or create railway.toml in backend/

   [build]
   builder = "nixpacks"
   buildCommand = "pip install -r requirements.txt"

   [deploy]
   startCommand = "uvicorn app.main:app --host 0.0.0.0 --port $PORT"
   healthcheckPath = "/health"
   healthcheckTimeout = 100
   restartPolicyType = "on-failure"
   ```

4. **Add Environment Variables**

   ```bash
   # In Railway Project Settings → Variables
   # Add all variables from your .env file

   ENVIRONMENT=production
   DATABASE_URL=<your-supabase-connection-string>
   ALLOWED_ORIGINS=https://logos-development.vercel.app,https://*.vercel.app
   CLERK_SECRET_KEY=sk_live_...
   OPENAI_API_KEY=sk-...
   # ... all other variables
   ```

5. **Deploy & Get URL**

   ```bash
   # Railway will automatically deploy
   # Get your backend URL:
   # https://property-intelligence-production.up.railway.app
   ```

6. **Run Database Migrations**

   ```bash
   # In Railway → Service → Settings → Deploy Trigger
   # Add deployment command:

   python -m alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```

7. **Test Backend**

   ```bash
   curl https://property-intelligence-production.up.railway.app/health

   # Should return:
   {
     "status": "healthy",
     "service": "Property Intelligence Platform API",
     "version": "1.0.0"
   }
   ```

---

### **Phase 3: Deploy Frontend (Vercel)**

1. **Create Vercel Account**

   ```bash
   # Go to: https://vercel.com
   # Sign up with GitHub
   # Free tier is sufficient for MVP
   ```

2. **Import Project**

   ```bash
   # In Vercel Dashboard:
   # Click: "Add New" → "Project"
   # Import: property-intelligence-platform repository
   # Framework: Next.js (auto-detected)
   # Root Directory: frontend/
   ```

3. **Configure Build Settings**

   ```bash
   # Vercel auto-detects Next.js settings
   # Build Command: npm run build
   # Output Directory: .next
   # Install Command: npm install
   ```

4. **Add Environment Variables**

   ```bash
   # In Vercel Project Settings → Environment Variables

   # Backend API (Railway URL)
   NEXT_PUBLIC_API_URL=https://property-intelligence-production.up.railway.app

   # Clerk Auth (Production Keys)
   NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
   CLERK_SECRET_KEY=sk_live_...

   # Mapbox (Optional - for later)
   NEXT_PUBLIC_MAPBOX_TOKEN=pk.eyJ1...
   ```

5. **Deploy**

   ```bash
   # Click: "Deploy"
   # Vercel will build and deploy automatically
   # Get your URL: https://logos-development.vercel.app
   ```

6. **Test Frontend**
   ```bash
   # Visit: https://logos-development.vercel.app
   # Should see: Landing page with "Turn Your Church Property..."
   ```

---

### **Phase 4: Update CORS on Backend**

1. **Add Production Frontend URL to Railway**

   ```bash
   # In Railway → Environment Variables
   # Update ALLOWED_ORIGINS:

   ALLOWED_ORIGINS=https://logos-development.vercel.app,https://*.vercel.app
   ```

2. **Redeploy Backend**

   ```bash
   # Railway will auto-redeploy with new CORS settings
   ```

3. **Test CORS**

   ```bash
   # From frontend browser console:
   fetch('https://property-intelligence-production.up.railway.app/health')
     .then(res => res.json())
     .then(data => console.log(data))

   # Should work without CORS errors
   ```

---

## 🔄 CI/CD Pipeline (Automatic Deployments)

### **Vercel (Frontend) - Already Configured**

✅ Auto-deploys on every `git push` to `main`
✅ Preview deployments for every PR
✅ Rollback with one click

### **Railway (Backend) - Configure Git Integration**

1. Railway → Settings → Git Triggers
2. Enable: "Deploy on push to main"
3. Optional: Enable "Deploy on PR" for preview environments

### **Database Migrations (Railway)**

```bash
# Railway → Settings → Deploy Command
# Update to run migrations before starting:

python -m alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## 💰 Cost Breakdown (Monthly)

### **MVP Testing Phase (Months 1-3)**

| Service             | Tier    | Cost         |
| ------------------- | ------- | ------------ |
| Vercel (Frontend)   | Free    | $0           |
| Railway (Backend)   | Starter | $5           |
| Supabase (Database) | Free    | $0           |
| **Total**           |         | **$5/month** |

### **Production Phase (After Launch)**

| Service             | Tier        | Cost             |
| ------------------- | ----------- | ---------------- |
| Vercel (Frontend)   | Pro         | $20              |
| Railway (Backend)   | Usage-based | $15-30           |
| Supabase (Database) | Pro         | $25              |
| **Total**           |             | **$60-75/month** |

### **Scale Phase (100+ Properties/month)**

| Service             | Tier        | Cost              |
| ------------------- | ----------- | ----------------- |
| Vercel (Frontend)   | Pro         | $20               |
| Railway (Backend)   | Usage-based | $50-100           |
| Supabase (Database) | Pro         | $25               |
| **Total**           |             | **$95-145/month** |

---

## 🔒 Security Checklist

### **Backend Security**

- [x] HTTPS only (Railway provides free SSL)
- [x] CORS configured with environment variables
- [x] Authentication with Clerk (JWT tokens)
- [x] Rate limiting (60 requests/minute)
- [x] Input validation with Pydantic
- [x] SQL injection prevention (SQLAlchemy ORM)
- [x] Environment variables for secrets
- [x] No hardcoded API keys

### **Frontend Security**

- [x] HTTPS only (Vercel provides free SSL)
- [x] CSP headers (Vercel auto-configures)
- [x] No API keys in client code
- [x] Clerk authentication middleware
- [x] Protected routes

### **Database Security**

- [x] SSL connection (Supabase enforces)
- [x] Strong password
- [x] IP allowlist (optional)
- [x] Automatic backups
- [x] Row-level security (optional with Supabase)

---

## 📊 Monitoring Setup

### **Vercel Analytics (Built-in)**

```bash
# Automatically enabled in Vercel dashboard
# Shows: Page views, performance, errors
```

### **Railway Logs**

```bash
# Real-time logs in Railway dashboard
# Filter by: Error, Warning, Info
```

### **Supabase Monitoring**

```bash
# Database metrics in Supabase dashboard
# Shows: Connections, queries, storage
```

### **Optional: Sentry (Error Tracking)**

```bash
# Add to backend .env
SENTRY_DSN=https://...@sentry.io/...

# Add to frontend .env
NEXT_PUBLIC_SENTRY_DSN=https://...@sentry.io/...
```

---

## 🚀 Deployment Commands

### **Deploy Backend (Railway)**

```bash
# Automatic on git push
git push origin main

# Or trigger manual deploy in Railway dashboard
```

### **Deploy Frontend (Vercel)**

```bash
# Automatic on git push
git push origin main

# Or use Vercel CLI
npm install -g vercel
vercel --prod
```

### **Run Database Migrations**

```bash
# Railway will run on deploy (configured in deploy command)
# Or manually via Railway CLI:
railway run python -m alembic upgrade head
```

---

## ✅ Deployment Checklist

### **Pre-Deployment**

- [ ] All tests passing locally
- [ ] Environment variables documented
- [ ] Database migrations tested
- [ ] CORS configured correctly
- [ ] API keys for production services

### **Database Setup**

- [ ] Supabase project created
- [ ] Extensions enabled (postgis, pg_trgm)
- [ ] Connection string obtained
- [ ] Migrations run successfully

### **Backend Deployment**

- [ ] Railway project created
- [ ] All environment variables added
- [ ] Build successful
- [ ] Health check endpoint responding
- [ ] Database connection working

### **Frontend Deployment**

- [ ] Vercel project created
- [ ] Environment variables added
- [ ] Build successful
- [ ] Can reach backend API
- [ ] Authentication working

### **Post-Deployment**

- [ ] Test church submission form end-to-end
- [ ] Verify enrichment workflow works
- [ ] Check email notifications
- [ ] Monitor error logs
- [ ] Set up monitoring alerts

---

## 🔄 Rollback Strategy

### **Vercel (Frontend)**

```bash
# In Vercel dashboard:
# Deployments → Click previous deployment → "Promote to Production"
```

### **Railway (Backend)**

```bash
# In Railway dashboard:
# Deployments → Click previous deployment → "Redeploy"
```

### **Database (Supabase)**

```bash
# Downgrade migrations:
railway run python -m alembic downgrade -1
```

---

## 📞 Support & Resources

- **Vercel Docs**: https://vercel.com/docs
- **Railway Docs**: https://docs.railway.app
- **Supabase Docs**: https://supabase.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Next.js Docs**: https://nextjs.org/docs

---

**Your architecture is production-ready! Each service handles what it's best at.** 🚀
