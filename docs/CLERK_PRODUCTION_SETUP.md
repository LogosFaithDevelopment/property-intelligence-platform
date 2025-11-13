# Clerk Production Setup Guide

## Overview

This guide walks through creating a production Clerk application and migrating from development to production keys.

---

## Table of Contents

1. [Current Development Setup](#current-development-setup)
2. [Creating Production App](#creating-production-app)
3. [API Keys Migration](#api-keys-migration)
4. [Webhook Configuration](#webhook-configuration)
5. [Environment Variables](#environment-variables)
6. [Testing Checklist](#testing-checklist)
7. [Cost Estimates](#cost-estimates)

---

## Current Development Setup

**Development Keys Currently Used:**

- Frontend: `pk_test_ZXhvdGljLW1pbmstNTAuY2xlcmsuYWNjb3VudHMuZGV2JA`
- Backend: `sk_test_aC7xdnf8HZLpi6erMxMFQdT1RUbX7m7c92tKTTVLhE`

**Current Features Used:**

- User authentication (sign in/sign up)
- Admin role checking via public metadata
- JWT token validation
- User session management

---

## Creating Production App

### Step 1: Access Clerk Dashboard

1. Go to [Clerk Dashboard](https://dashboard.clerk.com)
2. Sign in with your account
3. Click **"+ Create Application"**

### Step 2: Configure Production App

**Application Settings:**

```
Name: Property Intelligence Platform (Production)
Type: Web Application
Environment: Production
```

**Authentication Methods (Enable):**

- ✅ Email + Password
- ✅ Google OAuth (optional, recommended)
- ✅ Email verification required
- ❌ Phone authentication (optional, for later)

**Session Configuration:**

```
Session duration: 7 days
Multi-session handling: Single session per device (recommended)
Refresh token: Enabled (default)
```

### Step 3: Configure User Metadata

**Public Metadata Schema:**

```json
{
  "role": "user", // or "admin"
  "organizationId": null,
  "submissionCount": 0
}
```

**How to Set Admin Role:**

1. Go to **Users** tab in Clerk Dashboard
2. Select a user
3. Click **"Edit"** on Public Metadata
4. Add: `{"role": "admin"}`
5. Save

**Private Metadata (Optional):**

```json
{
  "internalNotes": "",
  "createdVia": "web",
  "lastLoginIp": ""
}
```

### Step 4: Get Production API Keys

Once the application is created:

1. Go to **API Keys** section
2. You'll see two sets of keys:

**Frontend (Publishable Key):**

```
pk_live_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

- ✅ Safe to expose in frontend code
- ✅ Used in browser/client-side
- ⚠️ Starts with `pk_live_` (not `pk_test_`)

**Backend (Secret Key):**

```
sk_live_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

- ⛔ **NEVER** expose publicly
- ⛔ Server-side only
- ⛔ Store in AWS Secrets Manager
- ⚠️ Starts with `sk_live_` (not `sk_test_`)

---

## API Keys Migration

### Development vs Production Keys

| Environment | Frontend Key  | Backend Key   | Usage                      |
| ----------- | ------------- | ------------- | -------------------------- |
| Development | `pk_test_...` | `sk_test_...` | Local development, testing |
| Staging     | `pk_test_...` | `sk_test_...` | Pre-production testing     |
| Production  | `pk_live_...` | `sk_live_...` | Live users, real data      |

### Migration Checklist

**Before Migration:**

- [ ] Verify all admin users are marked in **production** Clerk app
- [ ] Test authentication flow with production keys in staging
- [ ] Set up webhook endpoints (see below)
- [ ] Configure CORS origins in Clerk Dashboard
- [ ] Enable email verification for production

**During Migration:**

- [ ] Update `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` in frontend
- [ ] Update `CLERK_SECRET_KEY` in backend
- [ ] Update `CLERK_WEBHOOK_SECRET` (if using webhooks)
- [ ] Deploy updated environment variables to ECS
- [ ] Restart services

**After Migration:**

- [ ] Test sign-in flow
- [ ] Test sign-up flow
- [ ] Verify admin role checking works
- [ ] Test JWT token validation
- [ ] Monitor Clerk logs for errors

---

## Webhook Configuration

### Why Webhooks?

Webhooks allow your backend to:

- Track user sign-ups in real-time
- Sync user data between Clerk and your database
- Trigger actions on user events (optional)

### Step 1: Create Webhook Endpoint

**Endpoint URL:**

```
https://api.property-intel.example.com/api/v1/webhooks/clerk
```

**Events to Subscribe (Recommended):**

- `user.created` - Track new user registrations
- `user.updated` - Sync user metadata changes
- `session.created` - Track user logins (optional)

### Step 2: Configure in Clerk Dashboard

1. Go to **Webhooks** section
2. Click **"Add Endpoint"**
3. Enter your webhook URL
4. Select events to subscribe
5. Copy the **Signing Secret** (starts with `whsec_`)

**Signing Secret Example:**

```
whsec_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Step 3: Verify Webhook Signature (Backend)

```python
# backend/app/routers/webhooks.py (example)
from fastapi import APIRouter, Request, HTTPException
from svix.webhooks import Webhook, WebhookVerificationError
from app.config import get_settings

router = APIRouter()
settings = get_settings()

@router.post("/api/v1/webhooks/clerk")
async def clerk_webhook(request: Request):
    # Get headers
    svix_id = request.headers.get("svix-id")
    svix_timestamp = request.headers.get("svix-timestamp")
    svix_signature = request.headers.get("svix-signature")

    # Get body
    body = await request.body()

    # Verify webhook signature
    wh = Webhook(settings.clerk_webhook_secret)
    try:
        payload = wh.verify(body, {
            "svix-id": svix_id,
            "svix-timestamp": svix_timestamp,
            "svix-signature": svix_signature
        })
    except WebhookVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    # Process event
    event_type = payload["type"]
    if event_type == "user.created":
        # Handle new user creation
        user_data = payload["data"]
        # Save to database, send welcome email, etc.

    return {"status": "ok"}
```

### Step 4: Test Webhook

Clerk provides a **"Send Test Event"** button in the dashboard:

1. Go to your webhook endpoint
2. Click **"Send Test Event"**
3. Check your backend logs for incoming webhook
4. Verify signature validation works

---

## Environment Variables

### Frontend (.env.production)

```bash
# Clerk Authentication - PRODUCTION KEYS
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_REPLACE_WITH_PRODUCTION_KEY
CLERK_SECRET_KEY=sk_live_REPLACE_WITH_PRODUCTION_KEY
```

### Backend (.env.production or AWS Secrets Manager)

```bash
# Clerk Authentication - PRODUCTION KEYS
CLERK_SECRET_KEY=sk_live_REPLACE_WITH_PRODUCTION_KEY
CLERK_WEBHOOK_SECRET=whsec_REPLACE_IF_USING_WEBHOOKS
```

### Docker Build (Frontend)

When building frontend Docker image, pass as build arg:

```bash
docker build \
  --build-arg NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_XXX \
  -t frontend:latest .
```

### AWS Secrets Manager (Recommended)

Store sensitive keys in AWS Secrets Manager:

```json
{
  "CLERK_SECRET_KEY": "sk_live_XXXXXXXXXX",
  "CLERK_WEBHOOK_SECRET": "whsec_XXXXXXXXXX",
  "SECRET_KEY": "your-app-secret-key",
  "DATABASE_URL": "postgresql://...",
  "OPENAI_API_KEY": "sk-proj-...",
  "ATTOM_API_KEY": "...",
  "SMARTY_AUTH_ID": "...",
  "SMARTY_AUTH_TOKEN": "..."
}
```

---

## Testing Checklist

### Functional Tests

- [ ] **Sign Up Flow**

  - Create new account with valid email
  - Verify email verification works
  - Check user appears in Clerk Dashboard
  - Verify default role is "user"

- [ ] **Sign In Flow**

  - Log in with existing account
  - Verify JWT token is generated
  - Check session persists across page refreshes
  - Test "Remember Me" functionality

- [ ] **Admin Role**

  - Mark a user as admin in Clerk Dashboard
  - Verify admin can access `/admin` routes
  - Verify regular users cannot access admin routes
  - Test middleware protection

- [ ] **Sign Out**
  - Log out successfully
  - Verify session is cleared
  - Confirm redirect to home page

### Security Tests

- [ ] Verify `pk_live_` key works in production frontend
- [ ] Verify `sk_live_` key validates tokens correctly
- [ ] Test that development keys (`pk_test_`, `sk_test_`) are removed
- [ ] Confirm webhook signature validation works
- [ ] Test CORS settings allow production frontend

### Error Handling

- [ ] Test with invalid email format
- [ ] Test with weak password
- [ ] Test with expired session
- [ ] Test network failure during authentication

---

## Cost Estimates

### Clerk Pricing (as of 2025)

**Free Tier:**

- ✅ Up to 10,000 Monthly Active Users (MAU)
- ✅ Unlimited applications
- ✅ Basic authentication methods
- ✅ Community support

**Pro Plan ($25/month):**

- 10,000 MAU included
- $0.02 per additional MAU
- Advanced features (SAML SSO, etc.)
- Priority support

**Estimated Costs for Property Intelligence Platform:**

| Users           | Plan | Monthly Cost      |
| --------------- | ---- | ----------------- |
| 0 - 10,000      | Free | $0                |
| 10,001 - 20,000 | Pro  | $25 + $200 = $225 |
| 20,001 - 50,000 | Pro  | $25 + $800 = $825 |

**Recommendation:** Start with **Free Tier**, upgrade to Pro when approaching 10,000 MAU.

---

## Important Notes

### Security Best Practices

1. **Never commit production keys to Git**

   - Add `.env.production` to `.gitignore`
   - Use AWS Secrets Manager for production
   - Rotate keys if accidentally exposed

2. **Separate Development and Production**

   - Use different Clerk apps for dev/prod
   - Never test with production keys locally
   - Use staging environment with test keys

3. **Monitor Usage**
   - Check Clerk Dashboard for MAU count
   - Set up alerts for approaching limits
   - Review authentication logs regularly

### Migration Timing

**Best Time to Migrate:**

- ✅ Before first production deployment
- ✅ During low-traffic maintenance window
- ❌ Avoid during peak usage hours

**Rollback Plan:**
If migration fails:

1. Revert environment variables to development keys
2. Restart services
3. Investigate issue in staging
4. Retry migration when resolved

---

## Support Resources

- **Clerk Documentation:** https://clerk.com/docs
- **Clerk Dashboard:** https://dashboard.clerk.com
- **Community Discord:** https://clerk.com/discord
- **Email Support:** support@clerk.com (Pro plan only)

---

## Next Steps

After completing Clerk setup:

1. ✅ Production keys generated and stored in Secrets Manager
2. ✅ Webhook endpoint configured (optional)
3. ✅ Admin users marked in production app
4. → Move to AWS Secrets Manager documentation
5. → Configure RDS database
6. → Deploy to AWS ECS Fargate
