# Property Intelligence Platform - Next Steps Roadmap

## Current Status: Phase 1 Complete ✅

### What's Working:

- ✅ Backend API with all endpoints
- ✅ Database models and schemas
- ✅ Property enrichment service (8 external APIs)
- ✅ AI assessment scoring (6 categories, Logos-specific criteria)
- ✅ HUD API integration (Crosswalk, Income Limits, FMR)
- ✅ Docker containerization
- ✅ Comprehensive documentation

---

## 🎯 Phase 2: Testing & Refinement (Week 1-2)

### Priority 1: End-to-End Validation ⚡ **START HERE**

#### **Task 2.1: Run Integration Test**

**Time:** 30 minutes  
**Goal:** Verify complete user journey works

```bash
# Test the full flow
cd /Users/adamsilver/Desktop/property-intelligence-platform/backend
docker-compose exec backend python test_end_to_end_flow.py
```

**Expected Results:**

- Church created successfully
- Property added and enriched with HUD data
- Assessment completed with score 0-100
- All Logos metrics calculated correctly

**If Issues Found:**

- Debug specific API failures
- Fix scoring logic bugs
- Adjust weights if needed

---

#### **Task 2.2: Test with Real Los Angeles Property**

**Time:** 15 minutes  
**Goal:** Validate with actual church address

```bash
# Manual API test
curl -X POST "http://localhost:8000/api/v1/churches/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test LA Church",
    "primary_contact_name": "Pastor John",
    "primary_email": "test@lachurch.org",
    "primary_phone": "310-555-0123",
    "street_address": "123 Main St",
    "city": "Los Angeles",
    "state": "CA",
    "zip_code": "90001",
    "tax_exempt_id": "12-3456789",
    "is_501c3_verified": true,
    "congregation_size": 250
  }'

# Save the church_id from response, then:

curl -X POST "http://localhost:8000/api/v1/properties/" \
  -H "Content-Type: application/json" \
  -d '{
    "church_id": <CHURCH_ID>,
    "name": "Church Parking Lot",
    "street_address": "123 Main St",
    "city": "Los Angeles",
    "state": "CA",
    "zip_code": "90001",
    "lot_size_sqft": 25000,
    "property_type": "PARKING_LOT",
    "ownership_status": "OWNED_OUTRIGHT"
  }'

# Wait 30 seconds for enrichment, then check results
curl "http://localhost:8000/api/v1/properties/<PROPERTY_ID>/enrichment"
```

**What to Verify:**

- Los Angeles County FIPS code retrieved (06037)
- HUD Income Limits for LA County
- Fair Market Rents for LA area
- Demographics populated
- Coordinates accurate

---

#### **Task 2.3: Review Scoring Logic**

**Time:** 30 minutes  
**Goal:** Ensure scores align with Logos' expectations

**Review These Files:**

1. `backend/app/services/ai_assessment.py` - Lines 300-600 (financial scoring)
2. Check weight distribution:
   - Financial: 30% ✅
   - Section 8: 20% ✅
   - Location: 15% ✅
   - Market: 15% ✅
   - Partnership: 10% ✅
   - Risk: 10% ✅

**Questions to Answer:**

- Should 10K sqft disqualification be absolute? (Currently: yes)
- Is 40-140 unit range correct? (Currently: yes, based on Logos criteria)
- Is $325K/unit target accurate? (Currently: yes)
- Should Section 8 be weighted higher? (Currently: 20%)

---

### Priority 2: Fix Any Bugs Found

#### **Common Issues to Watch For:**

**Issue #1: HUD API Rate Limits**

- HUD allows 1,200 requests/day
- Each property enrichment = 3 HUD calls
- Solution: Cache HUD data for 30 days (already implemented)

**Issue #2: OpenAI Token Limits**

- Each assessment = ~2,000 tokens per category
- 6 categories = 12,000 tokens
- Solution: Use GPT-3.5-turbo to reduce costs (currently configured)

**Issue #3: Geocoding Failures**

- Invalid addresses won't geocode
- Solution: Add address validation before submission

**Issue #4: Background Task Timing**

- Property enrichment should take 30-90 seconds
- AI assessment should take 2-5 minutes
- If slower: Check API timeouts

---

## 🎯 Phase 3: Frontend Development (Week 2-4)

### Priority 3: Build Next.js Frontend

#### **Task 3.1: Initialize Next.js Project**

**Time:** 1 hour

```bash
cd /Users/adamsilver/Desktop/property-intelligence-platform

# Create frontend folder
npx create-next-app@latest frontend --typescript --tailwind --app

cd frontend

# Install additional dependencies
npm install @clerk/nextjs axios react-query lucide-react
npm install -D @types/node
```

**File Structure to Create:**

```
frontend/
├── app/
│   ├── (auth)/
│   │   ├── sign-in/[[...sign-in]]/page.tsx
│   │   └── sign-up/[[...sign-up]]/page.tsx
│   ├── dashboard/
│   │   ├── page.tsx
│   │   ├── properties/page.tsx
│   │   └── assessments/page.tsx
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── ChurchForm.tsx
│   ├── PropertyForm.tsx
│   ├── AssessmentForm.tsx
│   ├── ScoreCard.tsx
│   └── ResultsDashboard.tsx
├── lib/
│   ├── api.ts
│   └── types.ts
└── middleware.ts
```

---

#### **Task 3.2: Implement Core Pages**

**Time:** 8-12 hours

**Pages to Build:**

1. **Landing Page** (`app/page.tsx`)

   - Value proposition for churches
   - "Get Started" CTA → Sign up
   - Features overview
   - Testimonials placeholder

2. **Sign Up/Sign In** (Clerk)

   - Use Clerk components (pre-built)
   - Configure in `middleware.ts`

3. **Church Profile** (`app/onboarding/page.tsx`)

   - Multi-step form
   - POST to `/api/v1/churches`
   - Save church_id to user metadata

4. **Property Submission** (`app/dashboard/properties/new/page.tsx`)

   - Property form
   - POST to `/api/v1/properties`
   - Show "Enriching..." status
   - Poll for enrichment completion

5. **Assessment Form** (`app/dashboard/assessments/new/page.tsx`)

   - Questionnaire (8 questions)
   - POST to `/api/v1/assessments`
   - Show "Processing..." status
   - Poll for completion

6. **Results Dashboard** (`app/dashboard/assessments/[id]/page.tsx`)

   - Display overall score with gauge chart
   - Show 6 category breakdowns
   - Logos metrics table
   - Download PDF button

7. **Logos Admin Dashboard** (`app/admin/page.tsx`)
   - List all assessments
   - Filter by score/compliance
   - Approve/Decline buttons
   - Detailed view modal

---

#### **Task 3.3: Create Reusable Components**

**Time:** 4-6 hours

**Key Components:**

```typescript
// components/ScoreGauge.tsx
// Circular progress gauge for overall score

// components/CategoryScores.tsx
// Horizontal bar charts for 6 categories

// components/LogosMetrics.tsx
// Table with lot size, units, cost per unit, etc.

// components/ComplianceChecklist.tsx
// Visual checklist: ✅ Lot size, ⚠️ Unit count, ✅ Cost/unit

// components/PropertyCard.tsx
// Card showing property summary with enrichment status

// components/AssessmentCard.tsx
// Card showing assessment with score badge
```

---

### Priority 4: Connect Frontend to Backend

#### **Task 4.1: API Client Setup**

**Time:** 2 hours

```typescript
// lib/api.ts
import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add Clerk token to requests
api.interceptors.request.use(async (config) => {
  const token = await window.Clerk?.session?.getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const churchesAPI = {
  create: (data) => api.post('/api/v1/churches/', data),
  list: (params) => api.get('/api/v1/churches/', { params }),
  get: (id) => api.get(`/api/v1/churches/${id}`),
};

export const propertiesAPI = {
  create: (data) => api.post('/api/v1/properties/', data),
  list: (params) => api.get('/api/v1/properties/', { params }),
  get: (id) => api.get(`/api/v1/properties/${id}`),
  getEnrichment: (id) => api.get(`/api/v1/properties/${id}/enrichment`),
};

export const assessmentsAPI = {
  create: (data) => api.post('/api/v1/assessments/', data),
  list: (params) => api.get('/api/v1/assessments/', { params }),
  get: (id) => api.get(`/api/v1/assessments/${id}`),
  process: (id) => api.post(`/api/v1/assessments/${id}/process`),
};
```

---

#### **Task 4.2: Environment Configuration**

**Time:** 15 minutes

```bash
# frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_ZXhvdGljLW1pbmstNTAuY2xlcmsuYWNjb3VudHMuZGV2JA
CLERK_SECRET_KEY=sk_test_aC7xdnf8HZLpi6erMxMFQdT1RUbX7m7c92tKTTVLhE
```

---

## 🎯 Phase 4: Backend Enhancements (Week 3-4)

### Priority 5: Background Task Queue

**Current Issue:** Property enrichment and AI assessment run synchronously

**Solution:** Implement Arq task queue with Redis

#### **Task 4.1: Install Arq**

**Time:** 2 hours

```bash
# Add to requirements.txt
arq==0.25.0

# Install
pip install arq
```

**Create `app/tasks/worker.py`:**

```python
from arq import create_pool
from arq.connections import RedisSettings

async def enrich_property_task(ctx, property_id: int):
    """Background task for property enrichment"""
    from app.services.property_enrichment import PropertyEnrichmentService
    service = PropertyEnrichmentService(ctx['db'])
    await service.enrich_property(property_id)

async def process_assessment_task(ctx, assessment_id: int):
    """Background task for AI assessment"""
    from app.services.ai_assessment import AIAssessmentService
    service = AIAssessmentService(ctx['db'])
    await service.process_assessment(assessment_id)

class WorkerSettings:
    redis_settings = RedisSettings(host='localhost', port=6379)
    functions = [enrich_property_task, process_assessment_task]
```

**Update docker-compose.yml:**

```yaml
worker:
  build: ./backend
  command: arq app.tasks.worker.WorkerSettings
  depends_on:
    - postgres
    - redis
  env_file:
    - ./backend/.env
```

---

### Priority 6: Add Status Endpoints

#### **Task 5.1: Real-Time Status Polling**

**Time:** 1 hour

**Add to `routers/properties.py`:**

```python
@router.get("/{property_id}/enrichment/status")
async def get_enrichment_status(
    property_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get real-time enrichment status"""
    property_obj = await db.get(Property, property_id)

    return {
        "property_id": property_id,
        "status": property_obj.enrichment_status,  # PENDING/PROCESSING/COMPLETED/FAILED
        "progress": property_obj.enrichment_progress,  # 0-100
        "data_sources_completed": len(property_obj.data_sources or {})
    }
```

**Frontend polls this endpoint:**

```typescript
// Hook: useEnrichmentStatus
const { data, isLoading } = useQuery(
  ['enrichment-status', propertyId],
  () => propertiesAPI.getEnrichmentStatus(propertyId),
  {
    refetchInterval: 2000, // Poll every 2 seconds
    enabled: status === 'PROCESSING',
  }
);
```

---

## 🎯 Phase 5: Production Readiness (Week 4-5)

### Priority 7: Authentication & Security

#### **Task 6.1: Implement JWT Verification**

**Time:** 3 hours

```python
# app/utils/auth.py
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx

security = HTTPBearer()

async def verify_clerk_token(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """Verify Clerk JWT token"""
    token = credentials.credentials

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"https://api.clerk.com/v1/tokens/{token}/verify",
            headers={"Authorization": f"Bearer {settings.clerk_secret_key}"}
        )

    if response.status_code != 200:
        raise HTTPException(status_code=401, detail="Invalid token")

    return response.json()

# Protect endpoints
@router.post("/")
async def create_property(
    property_data: PropertyCreate,
    user: dict = Depends(verify_clerk_token),  # 👈 Add this
    db: AsyncSession = Depends(get_db)
):
    # user['sub'] = Clerk user ID
    # Link to church via user metadata
```

---

#### **Task 6.2: Row-Level Security**

**Time:** 2 hours

**Ensure churches only see their own data:**

```python
# Add to all list endpoints
@router.get("/")
async def list_properties(
    user: dict = Depends(verify_clerk_token),
    db: AsyncSession = Depends(get_db)
):
    # Get user's church_id from metadata
    church_id = user.get('public_metadata', {}).get('church_id')

    # Filter by church
    stmt = select(Property).where(Property.church_id == church_id)
    result = await db.execute(stmt)
    return result.scalars().all()
```

---

### Priority 8: Error Handling & Logging

#### **Task 7.1: Structured Logging**

**Time:** 1 hour

```python
# app/utils/logging.py
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "message": record.getMessage(),
            "service": "property-intelligence-backend",
        }
        if hasattr(record, 'user_id'):
            log_obj['user_id'] = record.user_id
        if hasattr(record, 'church_id'):
            log_obj['church_id'] = record.church_id
        return json.dumps(log_obj)

# Configure in main.py
logging.basicConfig(level=logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logging.getLogger().addHandler(handler)
```

---

#### **Task 7.2: Graceful Error Responses**

**Time:** 1 hour

```python
# app/main.py
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred",
            "request_id": request.headers.get("X-Request-ID"),
            "support_email": "support@logosfaith.com"
        }
    )
```

---

### Priority 9: Performance Optimization

#### **Task 8.1: Database Indexing**

**Time:** 30 minutes

```python
# Add to models
class Property(Base):
    __tablename__ = "properties"

    # Add indexes
    __table_args__ = (
        Index('idx_property_church_id', 'church_id'),
        Index('idx_property_coordinates', 'latitude', 'longitude'),
        Index('idx_property_lot_size', 'lot_size_sqft'),
    )

class Assessment(Base):
    __tablename__ = "assessments"

    __table_args__ = (
        Index('idx_assessment_church_id', 'church_id'),
        Index('idx_assessment_status', 'status'),
        Index('idx_assessment_score', 'overall_score'),
    )
```

---

#### **Task 8.2: Response Caching**

**Time:** 1 hour

```python
# app/utils/cache.py
from functools import wraps
import json
import redis

redis_client = redis.from_url(settings.redis_url)

def cache_response(ttl: int = 300):
    """Cache endpoint responses"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{json.dumps(kwargs)}"

            # Check cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function
            result = await func(*args, **kwargs)

            # Store in cache
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator

# Use on expensive endpoints
@router.get("/{property_id}/enrichment")
@cache_response(ttl=1800)  # Cache for 30 minutes
async def get_enrichment(property_id: int):
    # ...
```

---

## 🎯 Phase 6: Deployment (Week 5)

### Priority 10: Deploy to Production

#### **Task 9.1: Choose Hosting Provider**

**Recommended: Railway.app or Render.com**

**Railway.app** (Easier):

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
cd /Users/adamsilver/Desktop/property-intelligence-platform
railway init
railway up
```

**Render.com** (More control):

1. Create `render.yaml` in project root
2. Push to GitHub
3. Connect Render to repo
4. Auto-deploys on push

---

#### **Task 9.2: Production Environment Variables**

**Set in hosting dashboard:**

```env
# Production values
DATABASE_URL=postgresql://user:pass@host:5432/prod_db
REDIS_URL=redis://host:6379
SECRET_KEY=<generate-with-openssl-rand-hex-32>
ENVIRONMENT=production

# API Keys (same as development)
OPENAI_API_KEY=sk-proj-...
HUD_API_KEY=eyJ0eXAi...
GOOGLE_MAPS_API_KEY=AIzaSy...
CLERK_SECRET_KEY=sk_live_...  # Use LIVE key, not test

# CORS for production
ALLOWED_ORIGINS=["https://yourdomain.com"]
```

---

#### **Task 9.3: Set Up Monitoring**

**Time:** 2 hours

**Option 1: Sentry (Error Tracking)**

```bash
pip install sentry-sdk

# app/main.py
import sentry_sdk
sentry_sdk.init(
    dsn=settings.sentry_dsn,
    traces_sample_rate=0.1,
)
```

**Option 2: PostHog (Product Analytics)**

```bash
pip install posthog

# Track key events
posthog.capture('assessment_completed', {
    'church_id': church_id,
    'score': overall_score,
})
```

---

## 📊 Success Metrics to Track

Once deployed, monitor:

1. **API Performance:**

   - Average response time < 200ms
   - P95 response time < 500ms
   - Error rate < 1%

2. **Feature Usage:**

   - Churches registered per week
   - Properties submitted per week
   - Assessments completed per week
   - Average score distribution

3. **Data Quality:**

   - % of properties successfully enriched
   - % of assessments with all HUD data
   - Average enrichment time
   - Average assessment time

4. **Business Metrics:**
   - Properties scoring A (≥85): \_\_\_%
   - Properties scoring B (75-84): \_\_\_%
   - Properties meeting all 3 Logos criteria: \_\_\_%
   - Conversion rate (submitted → approved): \_\_\_%

---

## 🎯 Quick Win Priorities

**If you have limited time, focus on:**

1. ✅ **Test end-to-end flow** (30 min) → Validate Phase 1 works
2. ✅ **Build basic frontend** (2 days) → Get something visual
3. ✅ **Add authentication** (3 hours) → Secure the platform
4. ✅ **Deploy to Railway** (1 hour) → Get online
5. ✅ **Test with 5 real churches** (1 week) → Get feedback

**Everything else can be iterated on!**

---

## 🚀 Timeline Summary

| Phase    | Tasks                | Time      | Outcome                           |
| -------- | -------------------- | --------- | --------------------------------- |
| Phase 2A | Testing & Validation | 2-4 hours | Backend verified working          |
| Phase 3  | Frontend Development | 1-2 weeks | User interface complete           |
| Phase 4  | Backend Enhancements | 3-5 days  | Background jobs, status endpoints |
| Phase 5  | Production Readiness | 3-5 days  | Auth, security, logging           |
| Phase 6  | Deployment           | 1-2 days  | Live on the internet              |

**Total Time to MVP:** 3-4 weeks of focused work

---

## 📞 Need Help?

**Stuck on something?** Common bottlenecks:

- Frontend design → Use Tailwind UI or shadcn/ui
- Authentication → Clerk docs are excellent
- Deployment → Railway has great guides
- Database performance → Ask for optimization help

**Ready to start?** Begin with:

```bash
cd /Users/adamsilver/Desktop/property-intelligence-platform/backend
docker-compose exec backend python test_end_to_end_flow.py
```

This will validate Phase 1 is solid before moving forward! 🎉
