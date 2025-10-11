# 🔐 Authentication Quick Reference

**Quick lookup for using authentication in the Property Intelligence Platform**

---

## 🎯 Common Patterns

### 1. Protect an Endpoint (Require Auth)

```python
from app.middleware.auth import CurrentUser, get_current_user
from fastapi import Depends

@router.post("/resources/")
async def create_resource(
    data: ResourceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)  # ← Add this
):
    resource = Resource(**data.model_dump())
    resource.user_id = current_user.user_id  # ← Track ownership
    db.add(resource)
    await db.commit()
    return resource
```

### 2. Optional Authentication

```python
from app.middleware.auth import get_optional_user

@router.get("/resources/")
async def list_resources(
    current_user: Optional[CurrentUser] = Depends(get_optional_user)  # ← Optional
):
    if current_user:
        # Show user's resources + public resources
        stmt = select(Resource).where(
            or_(Resource.user_id == current_user.user_id, Resource.is_public == True)
        )
    else:
        # Show only public resources
        stmt = select(Resource).where(Resource.is_public == True)
```

### 3. Verify Ownership Before Update/Delete

```python
@router.put("/resources/{id}")
async def update_resource(
    id: int,
    data: ResourceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    resource = await db.get(Resource, id)
    if not resource:
        raise HTTPException(status_code=404, detail="Not found")

    # ← Check ownership
    if resource.user_id != current_user.user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Permission denied")

    # Update the resource
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(resource, field, value)

    await db.commit()
    return resource
```

### 4. Admin-Only Endpoint

```python
from app.middleware.auth import get_current_admin

@router.post("/admin/approve/{id}")
async def admin_approve(
    id: int,
    admin: CurrentUser = Depends(get_current_admin)  # ← Admin required
):
    # Only admins can execute this
    pass
```

### 5. Hierarchical Permission Check

```python
@router.post("/properties/")
async def create_property(
    property_data: PropertyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    # Get the church
    church = await db.get(Church, property_data.church_id)

    # ← Verify user owns the church
    if church.user_id != current_user.user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail="Cannot add properties to churches you don't own"
        )

    property = Property(**property_data.model_dump())
    property.user_id = current_user.user_id
    db.add(property)
    await db.commit()
    return property
```

---

## 🔍 CurrentUser Object

```python
class CurrentUser:
    user_id: str           # Clerk user ID (e.g., "user_2abc123")
    email: str | None      # User's email
    is_admin: bool         # True if user has admin role
    organization_id: str | None  # Clerk organization ID
    metadata: dict         # Additional JWT claims
```

**Access in endpoints:**

```python
async def my_endpoint(current_user: CurrentUser = Depends(get_current_user)):
    user_id = current_user.user_id
    email = current_user.email
    is_admin = current_user.is_admin
```

---

## 🧪 Testing Authentication

### Test 1: Endpoint Requires Auth

```bash
curl -X POST http://localhost:8000/api/v1/churches/ \
  -H "Content-Type: application/json" \
  -d '{}'

# Expected: {"detail": "Missing authentication token"}
```

### Test 2: With Valid Token

```bash
TOKEN="your-jwt-token-here"

curl -X POST http://localhost:8000/api/v1/churches/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Test Church",
    "primary_email": "test@church.com",
    "street_address": "123 Main St",
    "city": "Springfield",
    "state": "IL",
    "zip_code": "62701"
  }'
```

### Test 3: Check Auth System Health

```bash
curl http://localhost:8000/api/v1/auth/health
```

---

## 🎨 Frontend Usage (React + Clerk)

### Setup

```bash
npm install @clerk/clerk-react
```

### Wrap App with ClerkProvider

```jsx
// src/main.jsx
import { ClerkProvider } from '@clerk/clerk-react';

ReactDOM.createRoot(document.getElementById('root')).render(
  <ClerkProvider publishableKey={import.meta.env.VITE_CLERK_PUBLISHABLE_KEY}>
    <App />
  </ClerkProvider>
);
```

### Make Authenticated API Call

```jsx
import { useAuth } from '@clerk/clerk-react';

function MyComponent() {
  const { getToken } = useAuth();

  const createChurch = async (churchData) => {
    const token = await getToken();

    const response = await fetch('http://localhost:8000/api/v1/churches/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(churchData),
    });

    return response.json();
  };

  // ... rest of component
}
```

### Protected Route

```jsx
import { SignedIn, SignedOut, RedirectToSignIn } from '@clerk/clerk-react';

function App() {
  return (
    <Routes>
      <Route
        path='/dashboard'
        element={
          <>
            <SignedIn>
              <Dashboard />
            </SignedIn>
            <SignedOut>
              <RedirectToSignIn />
            </SignedOut>
          </>
        }
      />
    </Routes>
  );
}
```

---

## 📋 Checklist for Protecting a New Endpoint

- [ ] Import auth dependencies
- [ ] Add `current_user: CurrentUser = Depends(get_current_user)` to function
- [ ] Set `resource.user_id = current_user.user_id` on creation
- [ ] Check ownership before updates: `if resource.user_id != current_user.user_id`
- [ ] Allow admin override: `and not current_user.is_admin`
- [ ] Test without token (should fail)
- [ ] Test with valid token (should work)
- [ ] Test accessing another user's resource (should fail)

---

## 🚨 Common Errors

### Error: "Missing authentication token"

**Cause:** No `Authorization` header in request  
**Fix:** Include `Authorization: Bearer <token>` header

### Error: "Token has expired"

**Cause:** JWT token expired  
**Fix:** Request a new token from Clerk

### Error: "Permission denied" / 403

**Cause:** User doesn't own the resource  
**Fix:** Verify ownership or use admin account

### Error: "ModuleNotFoundError: No module named 'jwt'"

**Cause:** Wrong import statement  
**Fix:** Use `from jose import jwt` not `import jwt`

---

## 🔗 Useful Commands

```bash
# Check auth health
curl http://localhost:8000/api/v1/auth/health

# Check database has user_id columns
docker-compose exec postgres psql -U postgres -d property_intel \
  -c "\d churches" | grep user_id

# View backend logs
docker-compose logs backend --tail=50 -f

# Restart backend
docker-compose restart backend

# Run database migration
docker-compose exec backend alembic upgrade head
```

---

## 📚 Related Documentation

- **AUTHENTICATION_TESTING_GUIDE.md** - Comprehensive testing guide
- **AUTHENTICATION_COMPLETE_SUMMARY.md** - Full implementation details
- **AUTHENTICATION_FINAL_STATUS.md** - Project status and metrics
- **Clerk Documentation** - https://clerk.com/docs

---

**Last Updated:** October 3, 2025  
**Status:** Production Ready ✅
