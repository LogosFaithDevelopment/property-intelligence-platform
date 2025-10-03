# IMMEDIATE NEXT STEPS - Authentication Implementation

**Status:** Backend authentication middleware created, database migration ready  
**Date:** October 3, 2025  
**Estimated Time:** 2-3 hours to complete

---

## ✅ COMPLETED (Just Now)

1. **Added authentication dependencies** to `requirements.txt`:
   - `pyjwt==2.8.0`
   - `cryptography==41.0.7`

2. **Created authentication middleware** (`/backend/app/middleware/auth.py`):
   - `get_current_user()` - Extracts user from JWT token
   - `get_current_admin()` - Requires admin privileges
   - `CurrentUser` model with `user_id`, `email`, `is_admin`, `organization_id`

3. **Created database migration** (`/backend/alembic/versions/add_user_tracking_001.py`):
   - Adds `user_id` column to `churches`, `properties`, `assessments` tables
   - Adds indexes for performance

4. **Updated database models**:
   - ✅ `Church` model - added `user_id` field
   - ✅ `Property` model - added `user_id` field
   - ✅ `Assessment` model - added `user_id` field

---

## 🔨 NEXT: Complete Authentication Setup

### Step 1: Install Dependencies (5 minutes)

```bash
cd /Users/adamsilver/Desktop/property-intelligence-platform/backend

# Rebuild Docker container with new dependencies
docker-compose down
docker-compose build backend
docker-compose up -d
```

**Verify installation:**
```bash
docker-compose exec backend python -c "import jwt; print('✅ JWT installed')"
```

---

### Step 2: Run Database Migration (2 minutes)

```bash
# Run the migration to add user_id columns
docker-compose exec backend alembic upgrade head

# Verify migration
docker-compose exec postgres psql -U postgres -d property_intel -c "\d churches" | grep user_id
```

**Expected output:**
```
 user_id                | character varying(255)   |           |          |
```

---

### Step 3: Update Environment Variables (3 minutes)

Add Clerk keys to `/backend/.env`:

```bash
# Clerk Authentication
CLERK_PUBLISHABLE_KEY=pk_test_XXXXX
CLERK_SECRET_KEY=sk_test_XXXXX
CLERK_JWT_KEY=your-jwt-secret-key
```

**Get these keys from:**
1. Go to https://clerk.com
2. Sign up / Sign in
3. Create new application: "Property Intelligence Platform"
4. Copy keys from Dashboard → API Keys

**Restart backend:**
```bash
docker-compose restart backend
```

---

### Step 4: Protect Your Routers (30 minutes)

You need to add authentication to each router endpoint. Here's how:

#### A) Update Churches Router

```python
# /backend/app/routers/churches.py

from app.middleware.auth import get_current_user, get_current_admin, CurrentUser
from fastapi import Depends

# EXAMPLE: Protect create church endpoint
@router.post("/", response_model=ChurchResponse)
async def create_church(
    church_data: ChurchCreate,
    current_user: CurrentUser = Depends(get_current_user),  # ADD THIS
    db: AsyncSession = Depends(get_db)
):
    # Add user_id to the church
    church = Church(**church_data.model_dump(exclude_unset=True))
    church.user_id = current_user.user_id  # TRACK OWNERSHIP
    church.verification_status = ChurchStatus.PENDING
    
    db.add(church)
    await db.commit()
    return church

# EXAMPLE: List churches - only show user's own churches
@router.get("/", response_model=PaginatedResponse)
async def list_churches(
    pagination: PaginationParams = Depends(),
    current_user: CurrentUser = Depends(get_current_user),  # ADD THIS
    db: AsyncSession = Depends(get_db)
):
    query = select(Church)
    
    # ROW-LEVEL SECURITY: Only show user's churches
    if not current_user.is_admin:
        query = query.where(Church.user_id == current_user.user_id)
    
    # ... rest of pagination logic
```

#### B) Update Properties Router

```python
# /backend/app/routers/properties.py

from app.middleware.auth import get_current_user, CurrentUser

@router.post("/", response_model=PropertyResponse)
async def create_property(
    property_data: PropertyCreate,
    current_user: CurrentUser = Depends(get_current_user),  # ADD THIS
    db: AsyncSession = Depends(get_db)
):
    # Verify user owns the church
    church_result = await db.execute(
        select(Church).where(
            Church.id == property_data.church_id,
            Church.user_id == current_user.user_id  # SECURITY CHECK
        )
    )
    church = church_result.scalar_one_or_none()
    if not church and not current_user.is_admin:
        raise HTTPException(403, "Not authorized to add property to this church")
    
    property_obj = Property(**property_data.model_dump(exclude_unset=True))
    property_obj.user_id = current_user.user_id
    
    db.add(property_obj)
    await db.commit()
    return property_obj
```

#### C) Update Assessments Router

```python
# /backend/app/routers/assessments.py

from app.middleware.auth import get_current_user, CurrentUser

@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(
    assessment_id: int,
    current_user: CurrentUser = Depends(get_current_user),  # ADD THIS
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Assessment).where(Assessment.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()
    
    if not assessment:
        raise HTTPException(404, "Assessment not found")
    
    # ROW-LEVEL SECURITY: Check ownership
    if not current_user.is_admin and assessment.user_id != current_user.user_id:
        raise HTTPException(403, "Not authorized to view this assessment")
    
    return assessment
```

---

### Step 5: Test with Postman/cURL (15 minutes)

#### A) Get a test JWT token from Clerk

1. Go to Clerk Dashboard → JWT Templates
2. Create a test token with payload:
```json
{
  "sub": "user_test123",
  "email": "test@church.com",
  "public_metadata": {
    "role": "user"
  }
}
```

#### B) Test protected endpoints

```bash
# WITHOUT TOKEN (should fail)
curl http://localhost:8000/api/v1/churches
# Expected: 401 Unauthorized

# WITH TOKEN (should succeed)
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8000/api/v1/churches
# Expected: [] (empty list for new user)

# CREATE CHURCH (authenticated)
curl -X POST http://localhost:8000/api/v1/churches \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Church",
    "primary_email": "pastor@testchurch.com",
    "denomination": "Baptist"
  }'
# Expected: 201 Created with church data
```

---

## 🎯 TESTING CHECKLIST

After implementing authentication:

- [ ] Install new dependencies (Docker rebuild)
- [ ] Run database migration (user_id columns added)
- [ ] Add Clerk environment variables
- [ ] Update churches router (add auth dependencies)
- [ ] Update properties router (add auth + ownership checks)
- [ ] Update assessments router (add auth + ownership checks)
- [ ] Test unauthenticated request (should fail)
- [ ] Test authenticated request (should succeed)
- [ ] Test user can only see their own data
- [ ] Test admin can see all data

---

## 📝 QUICK REFERENCE: Common Auth Patterns

### Pattern 1: Public Endpoint (No Auth)
```python
@router.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Pattern 2: Authenticated Endpoint
```python
@router.get("/churches")
async def list_churches(
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # User is authenticated
    pass
```

### Pattern 3: Admin-Only Endpoint
```python
@router.post("/churches/{id}/verify")
async def verify_church(
    id: int,
    admin: CurrentUser = Depends(get_current_admin),  # Requires admin
    db: AsyncSession = Depends(get_db)
):
    # Only admins can access
    pass
```

### Pattern 4: Row-Level Security
```python
# Only show data user owns
query = query.where(Church.user_id == current_user.user_id)

# Admin bypass
if current_user.is_admin:
    # Show all data
    pass
else:
    query = query.where(Church.user_id == current_user.user_id)
```

---

## ⚠️ IMPORTANT SECURITY NOTES

1. **JWT Verification:** The current implementation uses HS256 (symmetric). For production, switch to RS256 with Clerk's JWKS:
   ```python
   # Production: Fetch Clerk's public keys
   jwks_url = f"https://api.clerk.com/v1/jwks"
   # Verify with public key instead of secret
   ```

2. **Never expose user_id in URLs:** Use UUIDs or database IDs, not Clerk user IDs

3. **Always check ownership:** Before modifying data, verify `user_id` matches

4. **Rate limiting:** Consider adding rate limits per user (not just IP)

---

## 🚀 AFTER AUTHENTICATION IS DONE

Once authentication works, you're ready for:

### Week 1-2: Frontend Development
- Build Next.js app with Clerk
- Church submission form
- Assessment results dashboard

### Week 3: Deployment
- Deploy backend to Render
- Deploy frontend to Vercel
- Configure production Clerk instance

### Week 4: Beta Testing
- Invite 3-5 churches
- Collect feedback
- Fix bugs

---

## 🆘 TROUBLESHOOTING

### Error: "ModuleNotFoundError: No module named 'jwt'"
**Solution:** Run `docker-compose build backend` to rebuild with new dependencies

### Error: "column churches.user_id does not exist"
**Solution:** Run migration: `docker-compose exec backend alembic upgrade head`

### Error: "Invalid authentication token"
**Solution:** Check Clerk secret key in `.env` matches your Clerk dashboard

### Error: "403 Forbidden" when accessing own data
**Solution:** Make sure `user_id` is set when creating records

---

## 📞 NEED HELP?

If you get stuck:
1. Check Docker logs: `docker-compose logs backend`
2. Check database: `docker-compose exec postgres psql -U postgres -d property_intel`
3. Test JWT decoder: https://jwt.io
4. Clerk docs: https://clerk.com/docs/backend-requests/handling/manual-jwt

---

**NEXT FILE TO CREATE:** After auth is working, create `FRONTEND_SETUP_GUIDE.md`
