# API Keys Verification and Management

## Overview

This document provides a checklist for verifying all external API keys before production deployment and managing them securely.

---

## Table of Contents

1. [API Keys Inventory](#api-keys-inventory)
2. [Verification Checklist](#verification-checklist)
3. [Production Key Requirements](#production-key-requirements)
4. [Key Rotation Schedule](#key-rotation-schedule)
5. [Emergency Procedures](#emergency-procedures)

---

## API Keys Inventory

### Current API Keys

| Service        | Environment Variable                  | Status      | Production Ready          | Cost             |
| -------------- | ------------------------------------- | ----------- | ------------------------- | ---------------- |
| Clerk          | `CLERK_SECRET_KEY`                    | ✅ Active   | ⚠️ Need pk*live*/sk*live* | Free (< 10K MAU) |
| OpenAI         | `OPENAI_API_KEY`                      | ✅ Active   | ✅ Yes                    | Pay-as-you-go    |
| ATTOM          | `ATTOM_API_KEY`                       | ✅ Active   | ✅ Yes                    | Subscription     |
| Smarty Streets | `SMARTY_AUTH_ID`, `SMARTY_AUTH_TOKEN` | ✅ Active   | ✅ Yes                    | Subscription     |
| HUD            | `HUD_API_KEY`                         | ✅ Active   | ✅ Yes                    | Free             |
| Google Maps    | `GOOGLE_MAPS_API_KEY`                 | ✅ Active   | ⚠️ Check limits           | Pay-as-you-go    |
| Census         | `CENSUS_API_KEY`                      | ⚠️ Optional | ✅ Yes                    | Free (most APIs) |

---

## Verification Checklist

### 1. Clerk Authentication

**Current Keys (Development):**

- Frontend: `pk_test_ZXhvdGljLW1pbmstNTAuY2xlcmsuYWNjb3VudHMuZGV2JA`
- Backend: `sk_test_aC7xdnf8HZLpi6erMxMFQdT1RUbX7m7c92tKTTVLhE`

**Production Requirements:**

- [ ] Create production Clerk application
- [ ] Get `pk_live_*` publishable key
- [ ] Get `sk_live_*` secret key
- [ ] Mark admin users in production app
- [ ] Test authentication flow
- [ ] Store keys in AWS Secrets Manager

**Verification Test:**

```bash
# Test Clerk JWT validation
curl -H "Authorization: Bearer YOUR_CLERK_JWT" \
  https://api.property-intel.example.com/health
```

**Cost:** Free up to 10,000 MAU

---

### 2. OpenAI API

**Current Key:**

- `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`

**Production Checklist:**

- [ ] Verify key is valid and active
- [ ] Check usage limits and quotas
- [ ] Confirm billing method is set up
- [ ] Test gpt-4o-mini model access
- [ ] Set up usage alerts ($50, $100, $200)
- [ ] Store key in AWS Secrets Manager

**Verification Test:**

```python
import openai
openai.api_key = "your-key"
response = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Test"}]
)
print(response.choices[0].message.content)
```

**Cost Estimates:**

- gpt-4o-mini: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
- Average assessment (1000 tokens): ~$0.001
- 1,000 assessments/month: ~$1-2

**Production Requirements:**

- ✅ Valid for production use
- ⚠️ Monitor usage (set alerts)
- ⚠️ Consider prepaid credits for cost control

---

### 3. ATTOM Property Data API

**Current Key:**

- `4192abd990678013d974cbca764cc376`

**Production Checklist:**

- [ ] Verify key is active
- [ ] Check subscription tier and limits
- [ ] Confirm allowed API endpoints
- [ ] Test property data retrieval
- [ ] Verify geocoding works
- [ ] Store key in AWS Secrets Manager

**Verification Test:**

```bash
curl -X GET "https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/address" \
  -H "apikey: YOUR_ATTOM_KEY" \
  -H "Accept: application/json" \
  -d "address1=123 Main St" \
  -d "address2=Los Angeles, CA 90001"
```

**Cost:** Subscription-based (varies by tier)

- Basic: ~$50-100/month
- Professional: ~$200-500/month

**Production Requirements:**

- ✅ Valid for production use
- ⚠️ Confirm subscription is active
- ⚠️ Verify query limits

---

### 4. Smarty Streets API

**Current Keys:**

- Auth ID: `a1a2af20-c56b-28ea-589e-42ae0c6a5f7d`
- Auth Token: `fTu0dqsoi39YClAcKg19`
- Website Key: `248956812188552196`

**Production Checklist:**

- [ ] Verify auth credentials are valid
- [ ] Check subscription tier and limits
- [ ] Test US Street Address API
- [ ] Test US Property Data API
- [ ] Verify SmartyKey lookup works
- [ ] Store keys in AWS Secrets Manager

**Verification Test:**

```bash
curl "https://us-street.api.smarty.com/street-address" \
  -d "auth-id=YOUR_AUTH_ID" \
  -d "auth-token=YOUR_AUTH_TOKEN" \
  -d "street=123 Main St" \
  -d "city=Los Angeles" \
  -d "state=CA" \
  -d "zipcode=90001"
```

**Cost:** Subscription-based

- Lookups: ~$0.50-1.00 per 1000 lookups
- Property Data: Additional cost per lookup

**Production Requirements:**

- ✅ Valid for production use
- ⚠️ Verify subscription covers property data API
- ⚠️ Check monthly lookup limits

---

### 5. HUD API

**Current Key:**

- `eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9...` (JWT token)

**Production Checklist:**

- [ ] Verify token is valid
- [ ] Check token expiration date
- [ ] Test HUD data API endpoints
- [ ] Verify no rate limits
- [ ] Store key in AWS Secrets Manager

**Verification Test:**

```bash
curl "https://hudgis-hud.opendata.arcgis.com/api/v3/datasets" \
  -H "Authorization: Bearer YOUR_HUD_TOKEN"
```

**Cost:** Free

**Production Requirements:**

- ✅ Valid for production use
- ✅ Free, no limits
- ⚠️ Token may expire (check expiration)

---

### 6. Google Maps API

**Current Key:**

- `AIzaSyAtmHnvq1hQWk6td3NJITxRQzVsZHrIgCo`

**Production Checklist:**

- [ ] Verify key is valid
- [ ] Check API restrictions (HTTP referrers, IP addresses)
- [ ] Confirm enabled APIs (Maps JavaScript, Geocoding, Places)
- [ ] Test geocoding requests
- [ ] Set up billing alerts
- [ ] Store key in AWS Secrets Manager

**Verification Test:**

```bash
curl "https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=YOUR_API_KEY"
```

**Cost Estimates:**

- Geocoding: $5 per 1000 requests
- First $200/month free (Google Cloud credit)

**Production Requirements:**

- ✅ Valid for production use
- ⚠️ Set API restrictions (HTTP referrers only)
- ⚠️ Enable billing and set alerts

---

### 7. Census API

**Current Key:**

- Empty (most Census APIs don't require a key)

**Production Checklist:**

- [ ] Verify Census API endpoints work without key
- [ ] Test demographic data retrieval
- [ ] Check rate limits (500 requests/IP/day)
- [ ] (Optional) Request Census API key for higher limits

**Verification Test:**

```bash
curl "https://api.census.gov/data/2020/acs/acs5?get=NAME,B01001_001E&for=county:*"
```

**Cost:** Free

**Production Requirements:**

- ✅ Valid for production use (no key needed)
- ✅ Free, no authentication required
- ⚠️ Rate limited to 500 requests/day/IP

---

## Production Key Requirements

### Security Requirements

**All Production Keys Must:**

- ✅ Be stored in AWS Secrets Manager (NOT in code or .env files)
- ✅ Have unique keys per environment (dev/staging/prod)
- ✅ Be rotated regularly (see schedule below)
- ✅ Have access logs enabled (CloudTrail)
- ✅ Be restricted by IP/domain where possible

**Never:**

- ❌ Commit keys to Git
- ❌ Share keys via email/Slack
- ❌ Use development keys in production
- ❌ Log key values in application logs

### Access Control

**Who Has Access:**

- AWS IAM users with `SecretsManager:GetSecretValue` permission
- ECS tasks via task execution role
- Emergency on-call engineers (with MFA)

**Audit Log:**

```bash
# Check who accessed secrets
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=property-intel/production/backend-secrets
```

---

## Key Rotation Schedule

### Recommended Rotation Schedule

| Service           | Rotation Frequency | Priority | Notes                         |
| ----------------- | ------------------ | -------- | ----------------------------- |
| Clerk Secret Key  | 90 days            | High     | Coordinate with user sessions |
| OpenAI API Key    | 180 days           | Medium   | No user impact                |
| ATTOM API Key     | As needed          | Low      | Contact support for rotation  |
| Smarty Streets    | As needed          | Low      | Contact support for rotation  |
| HUD Token         | When expired       | Medium   | Check expiration date         |
| Google Maps       | 180 days           | Medium   | Update API restrictions       |
| Database Password | 90 days            | High     | Use RDS automated rotation    |
| App SECRET_KEY    | 90 days            | High     | Invalidates all sessions      |

### Rotation Process

#### 1. Generate New Key

```bash
# Example: Rotate app SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

#### 2. Update AWS Secrets Manager

```bash
aws secretsmanager update-secret \
  --secret-id property-intel/production/backend-secrets \
  --secret-string '{"SECRET_KEY":"NEW_KEY",...}'
```

#### 3. Deploy Updated Secret

```bash
# Restart ECS service to pick up new secret
aws ecs update-service \
  --cluster property-intel-cluster \
  --service backend \
  --force-new-deployment
```

#### 4. Verify

```bash
# Check service health
aws ecs describe-services \
  --cluster property-intel-cluster \
  --services backend
```

#### 5. Revoke Old Key

After confirming new key works, revoke/delete old key.

---

## Emergency Procedures

### Key Compromise

If a key is exposed (e.g., committed to GitHub):

#### Immediate Actions (Within 1 Hour)

1. **Rotate the key immediately:**

   ```bash
   # Update in Secrets Manager
   aws secretsmanager update-secret --secret-id ... --secret-string '...'

   # Force ECS deployment
   aws ecs update-service --service backend --force-new-deployment
   ```

2. **Revoke compromised key:**

   - Clerk: Revoke in dashboard
   - OpenAI: Delete key in dashboard
   - ATTOM/Smarty: Contact support
   - Google Maps: Restrict key immediately

3. **Notify stakeholders:**
   - Email dev team
   - Post in Slack #incidents channel
   - Document incident in wiki

#### Follow-Up Actions (Within 24 Hours)

1. **Audit access logs:**

   ```bash
   # Check for unauthorized usage
   aws cloudtrail lookup-events --start-time ... --end-time ...
   ```

2. **Review CloudWatch logs:**

   - Check for suspicious API calls
   - Monitor for unusual patterns

3. **Update security policies:**
   - Add to .gitignore if missing
   - Enable pre-commit hooks
   - Update team training

### Service Outage

If an API service is down:

1. **Check Status Pages:**

   - Clerk: https://status.clerk.dev
   - OpenAI: https://status.openai.com
   - ATTOM: Contact support
   - Smarty: https://status.smarty.com
   - Google Maps: https://status.cloud.google.com

2. **Enable Graceful Degradation:**

   - Clerk: Show maintenance message
   - OpenAI: Use cached assessments
   - ATTOM/Smarty: Fall back to basic validation
   - Google Maps: Use alternative geocoder

3. **Monitor Recovery:**
   - Set up CloudWatch alarms
   - Check service health endpoints
   - Verify functionality after recovery

---

## Summary Checklist

### Pre-Production Deployment

- [ ] All API keys verified and working
- [ ] Production Clerk app created (pk*live*/sk*live*)
- [ ] All keys stored in AWS Secrets Manager
- [ ] ECS task execution role has Secrets Manager permissions
- [ ] API restrictions configured (IP, domain, HTTP referrer)
- [ ] Billing alerts set up for pay-as-you-go services
- [ ] Usage monitoring enabled (CloudWatch, service dashboards)
- [ ] Key rotation schedule documented
- [ ] Emergency procedures reviewed with team
- [ ] Backup authentication methods configured

### Post-Production Deployment

- [ ] Verify all APIs responding correctly
- [ ] Check CloudWatch logs for errors
- [ ] Monitor API usage and costs
- [ ] Set up alerts for approaching limits
- [ ] Schedule first key rotation (90 days)
- [ ] Document any issues or workarounds
- [ ] Update runbook with lessons learned

---

## Support Contacts

| Service      | Support URL                                 | Email                 | Phone                       |
| ------------ | ------------------------------------------- | --------------------- | --------------------------- |
| Clerk        | https://clerk.com/support                   | support@clerk.com     | N/A                         |
| OpenAI       | https://help.openai.com                     | N/A                   | N/A                         |
| ATTOM        | https://api.developer.attomdata.com/support | support@attomdata.com | (800) 977-5337              |
| Smarty       | https://www.smarty.com/contact              | support@smarty.com    | (800) 370-8856              |
| Google Cloud | https://cloud.google.com/support            | N/A                   | Available with support plan |

---

## Next Steps

After API key verification:

1. ✅ All keys verified and documented
2. ✅ Production keys stored in Secrets Manager
3. ✅ Access controls configured
4. → Test database migrations (Phase 6)
5. → Final code cleanup and testing (Phase 7)
6. → Create production deployment guide (Phase 8)
