# 🔧 CORS Configuration Quick Reference

**For Property Intelligence Platform**

---

## 🎯 Current Setup (Already Configured ✅)

Your backend uses **environment variables** for CORS, which is the best practice!

```python
# app/config.py (Already configured)
allowed_origins: List[str] = Field(
    default=["http://localhost:3000"],
    alias="ALLOWED_ORIGINS"
)

@validator("allowed_origins", pre=True)
def parse_cors_origins(cls, v):
    if isinstance(v, str):
        return [origin.strip() for origin in v.split(",")]
    return v
```

---

## 📝 Environment Variable Configurations

### **Local Development**

```env
# .env (backend)
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### **Production (Deployed)**

```env
# Railway Environment Variables
ALLOWED_ORIGINS=https://logos-development.vercel.app
```

### **Production + Preview Deployments** (Recommended)

```env
# Railway Environment Variables
# This allows both production AND all Vercel preview deployments
ALLOWED_ORIGINS=https://logos-development.vercel.app,https://*.vercel.app
```

---

## 🔄 How to Update CORS for New Environments

### **Scenario 1: Add Production Frontend URL**

**After deploying frontend to Vercel:**

1. Get your Vercel URL:

   ```
   https://logos-development.vercel.app
   ```

2. Update Railway environment variable:

   ```bash
   # Railway Dashboard → Your Project → Variables
   # Update ALLOWED_ORIGINS:

   ALLOWED_ORIGINS=https://logos-development.vercel.app,http://localhost:3000
   ```

3. Redeploy backend:
   ```bash
   # Railway will auto-redeploy when you save the variable
   # Or manually trigger in Railway → Deployments → Redeploy
   ```

### **Scenario 2: Add Staging Environment**

```env
ALLOWED_ORIGINS=https://logos-development.vercel.app,https://logos-staging.vercel.app,http://localhost:3000
```

### **Scenario 3: Enable All Vercel Preview Deployments**

When you create PRs, Vercel creates preview URLs like:

```
https://property-intelligence-pr-123.vercel.app
```

To allow ALL preview deployments:

```env
ALLOWED_ORIGINS=https://logos-development.vercel.app,https://*.vercel.app,http://localhost:3000
```

⚠️ **Note:** Wildcard subdomains (`*.vercel.app`) work in most browsers, but some older browsers may require explicit URLs.

---

## 🧪 Testing CORS

### **Test from Browser Console**

```javascript
// Open your frontend in browser
// Open DevTools Console (F12)
// Run this:

fetch('https://your-backend-url.railway.app/health')
  .then((res) => res.json())
  .then((data) => console.log('✅ CORS working:', data))
  .catch((err) => console.error('❌ CORS error:', err));
```

### **Test with curl**

```bash
# Test CORS preflight (OPTIONS request)
curl -X OPTIONS \
  https://your-backend-url.railway.app/health \
  -H "Origin: https://logos-development.vercel.app" \
  -H "Access-Control-Request-Method: GET" \
  -v

# Look for these headers in response:
# Access-Control-Allow-Origin: https://logos-development.vercel.app
# Access-Control-Allow-Credentials: true
```

---

## ⚠️ Common CORS Issues & Fixes

### **Issue 1: CORS Error After Deploying Frontend**

**Error in browser:**

```
Access to fetch at 'https://backend.railway.app/api/...' from origin 'https://logos.vercel.app' has been blocked by CORS policy
```

**Fix:**

1. Add your Vercel URL to `ALLOWED_ORIGINS` in Railway
2. Make sure to include `https://` (not `http://`)
3. Redeploy backend

### **Issue 2: Preview Deployments Not Working**

**Error:**

```
CORS error on https://logos-pr-123.vercel.app
```

**Fix:**
Add wildcard to ALLOWED_ORIGINS:

```env
ALLOWED_ORIGINS=https://logos-development.vercel.app,https://*.vercel.app
```

### **Issue 3: Credentials Not Included**

**Error:**

```
The value of the 'Access-Control-Allow-Origin' header... must not be the wildcard '*' when the request's credentials mode is 'include'.
```

**Fix:**
Your backend is already configured correctly with:

```python
allow_credentials=True  # ✅ Already set in main.py
```

Never use `allow_origins=["*"]` with `allow_credentials=True`.

### **Issue 4: Localhost Not Working**

**Fix:**
Make sure to include BOTH:

```env
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

---

## 🔐 Security Best Practices

### ✅ DO:

- Use environment variables (you're already doing this!)
- List specific domains explicitly
- Use HTTPS in production
- Include `allow_credentials=True` for auth cookies/tokens
- Keep development and production origins separate

### ❌ DON'T:

- Hardcode domains in `main.py`
- Use `allow_origins=["*"]` in production
- Mix `allow_origins=["*"]` with `allow_credentials=True`
- Forget to update after deploying new environments

---

## 📋 Quick Checklist

When deploying new environment:

- [ ] Deploy frontend to Vercel
- [ ] Get Vercel URL (e.g., `https://logos.vercel.app`)
- [ ] Add URL to Railway `ALLOWED_ORIGINS`
- [ ] Separate multiple URLs with commas
- [ ] Include `https://` prefix
- [ ] Test CORS in browser console
- [ ] Verify credentials are sent correctly

---

## 🔄 Environment Variable Reference

### **Development**

```env
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### **Staging**

```env
ALLOWED_ORIGINS=http://localhost:3000,https://logos-staging.vercel.app
```

### **Production**

```env
ALLOWED_ORIGINS=https://logos-development.vercel.app,https://*.vercel.app
```

### **Production + Development**

```env
ALLOWED_ORIGINS=https://logos-development.vercel.app,https://*.vercel.app,http://localhost:3000
```

---

## 💡 Pro Tips

1. **Keep localhost in production ALLOWED_ORIGINS** during development:

   ```env
   ALLOWED_ORIGINS=https://logos.vercel.app,http://localhost:3000
   ```

   This allows you to test against production backend from local frontend.

2. **Use Vercel Environment Variables** to switch between backends:

   ```env
   # Vercel Development
   NEXT_PUBLIC_API_URL=http://localhost:8000

   # Vercel Preview/Production
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   ```

3. **Monitor CORS in Railway Logs**:
   - Railway Dashboard → Logs
   - Search for: "CORS" or "Origin"
   - Look for rejected requests

---

**Your CORS setup is already perfect! Just update `ALLOWED_ORIGINS` when deploying new environments.** ✅
