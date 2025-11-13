# Clerk Build Fix - What Changed & Why

## The Problem

Your Docker build was failing with this error:

```
Error occurred prerendering page "/_not-found"
[Error: @clerk/clerk-react: Missing publishableKey...]
```

### Why This Happened

1. **Next.js Prerendering**: During `npm run build`, Next.js tries to prerender pages (including error pages like `/_not-found`)
2. **Clerk Initialization**: The Clerk React component runs during prerendering
3. **Missing Key**: `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` wasn't available during the Docker build process
4. **Build Failure**: Without the key, Clerk throws an error and Next.js exits with code 1

## The Solution

We made 3 changes to pass environment variables during the Docker build:

### 1. Updated `frontend/Dockerfile`

Added build arguments (ARG) and set them as environment variables during the build stage:

```dockerfile
# Build arguments - these are needed during the build process
ARG NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_ENVIRONMENT

# Set environment variables from build args
ENV NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=$NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_ENVIRONMENT=$NEXT_PUBLIC_ENVIRONMENT
```

### 2. Updated `docker-compose.prod.yml`

Added `args:` section to pass environment variables as build arguments:

```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
    args:
      - NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=${NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-http://backend:8000}
      - NEXT_PUBLIC_ENVIRONMENT=production
```

### 3. Updated Documentation

- Added note in `.env.production.local.example` that Clerk key is required during build
- Added troubleshooting section in `docs/DOCKER_PRODUCTION_TESTING.md`
- Added prerequisite note about Clerk publishable key

## What You Need to Do

### 1. Create `.env.production.local` (if not done already)

```bash
cp .env.production.local.example .env.production.local
```

### 2. Get Your Clerk Publishable Key

Visit: https://dashboard.clerk.com/last-active?path=api-keys

- For testing: Use `pk_test_*` key
- For production: Use `pk_live_*` key

### 3. Add the Key to `.env.production.local`

```bash
# Add or update this line:
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_actual_key_here
```

### 4. Rebuild and Test

```bash
# Clean build (recommended after this fix)
docker-compose -f docker-compose.prod.yml build --no-cache frontend

# Or rebuild everything
docker-compose -f docker-compose.prod.yml build --no-cache

# Start services
docker-compose -f docker-compose.prod.yml up
```

## Why This Works

### Build Arguments vs Environment Variables

- **Build Arguments (ARG)**: Available during `docker build` time
- **Environment Variables (ENV)**: Available during container runtime

Next.js needs these variables during **build time** (not just runtime) because:

1. It prerenders pages
2. It bundles environment variables into the JavaScript
3. It validates that required variables are present

### Docker Compose Integration

Docker Compose reads your `.env.production.local` file and passes those values as build arguments to the Dockerfile, which then sets them as environment variables during the build process.

## Key Takeaway

**All `NEXT_PUBLIC_*` variables are needed during build time**, not just runtime, because Next.js bakes them into the client-side bundle during the build process.

---

## Next Steps After Successful Build

1. ✅ Build completes successfully
2. ✅ Verify image sizes: `docker images | grep property-intel`
3. ✅ Test health endpoints
4. ✅ Move to Phase 4: Production logging and security
