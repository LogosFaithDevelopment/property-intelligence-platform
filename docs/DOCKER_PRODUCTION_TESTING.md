# Docker Production Build & Testing Guide

## Overview

This guide helps you build, test, and optimize production Docker images locally before AWS deployment.

---

## Prerequisites

- Docker 20.10+ installed
- Docker Compose 2.0+ installed
- PostgreSQL database accessible (local or RDS)
- All required API keys (Clerk, OpenAI, ATTOM, Smarty Streets)
- **Clerk Publishable Key**: Required during build process (pk*test*_ or pk*live*_)

---

## Quick Start

### 1. Setup Environment Variables

```bash
# Copy the production environment template
cp .env.production.local.example .env.production.local

# Edit with your values
nano .env.production.local  # or use your preferred editor
```

**Important:**

- Update `DATABASE_URL` to point to an accessible PostgreSQL instance
- Set `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` - this is required during the build process for Next.js prerendering

### 2. Build Production Images

```bash
# Build both frontend and backend
docker-compose -f docker-compose.prod.yml build

# Build individually
docker-compose -f docker-compose.prod.yml build backend
docker-compose -f docker-compose.prod.yml build frontend
```

### 3. Start Services

```bash
# Start all services (with build)
docker-compose -f docker-compose.prod.yml up --build

# Start in detached mode (background)
docker-compose -f docker-compose.prod.yml up -d

# Start specific service
docker-compose -f docker-compose.prod.yml up backend
```

### 4. Verify Health

```bash
# Backend health check
curl http://localhost:8000/health

# Backend database health
curl http://localhost:8000/health/db

# Frontend health check
curl http://localhost:3000/api/health
```

### 5. Access Application

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Backend Docs:** http://localhost:8000/docs (disabled in production)

---

## Image Size Comparison

### Before Optimization

```
Backend:  ~1.2GB (single-stage build)
Frontend: ~1.5GB (full node_modules)
Total:    ~2.7GB
```

### After Optimization

```
Backend:  ~400MB (multi-stage, slim base)
Frontend: ~150MB (alpine + standalone)
Total:    ~550MB (80% reduction!)
```

### Check Your Image Sizes

```bash
# List all images with sizes
docker images | grep property-intel

# Expected output:
# property-intel-backend-prod   latest   400MB
# property-intel-frontend-prod  latest   150MB
```

---

## Testing Production Features

### 1. Test Gunicorn + Uvicorn Workers

```bash
# Check backend is using gunicorn
docker-compose -f docker-compose.prod.yml logs backend | grep gunicorn

# You should see:
# [INFO] Starting gunicorn 21.2.0
# [INFO] Listening at: http://0.0.0.0:8000
# [INFO] Using worker: uvicorn.workers.UvicornWorker
# [INFO] Booted worker with pid: X (x4 workers)
```

### 2. Test Health Checks

```bash
# Watch health check status
docker-compose -f docker-compose.prod.yml ps

# Should show "healthy" status:
# NAME                        STATUS
# property-intel-backend-prod   Up XX seconds (healthy)
# property-intel-frontend-prod  Up XX seconds (healthy)
```

### 3. Test Security Headers

```bash
# Check frontend security headers
curl -I http://localhost:3000

# Should include:
# X-Frame-Options: DENY
# X-Content-Type-Options: nosniff
# Strict-Transport-Security: max-age=31536000
# X-XSS-Protection: 1; mode=block
```

### 4. Test Database Connection

```bash
# Test backend database connectivity
curl http://localhost:8000/health/db

# Expected response:
# {
#   "status": "healthy",
#   "service": "property-intelligence-platform-backend",
#   "database": "connected"
# }
```

### 5. Load Testing (Optional)

```bash
# Install Apache Bench
brew install apache-bench  # macOS
sudo apt-get install apache2-utils  # Linux

# Test backend endpoints (100 requests, 10 concurrent)
ab -n 100 -c 10 http://localhost:8000/health

# Expected: All requests successful, no 5xx errors
```

---

## Debugging & Logs

### View Logs

```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend

# Last 100 lines
docker-compose -f docker-compose.prod.yml logs --tail=100 backend
```

### Execute Commands in Containers

```bash
# Backend container shell
docker-compose -f docker-compose.prod.yml exec backend sh

# Check Python version
docker-compose -f docker-compose.prod.yml exec backend python --version

# Check installed packages
docker-compose -f docker-compose.prod.yml exec backend pip list

# Frontend container shell
docker-compose -f docker-compose.prod.yml exec frontend sh

# Check Node version
docker-compose -f docker-compose.prod.yml exec frontend node --version
```

### Inspect Container Resources

```bash
# Real-time resource usage
docker stats

# Specific container
docker stats property-intel-backend-prod
```

---

## Stopping & Cleanup

### Stop Services

```bash
# Stop all services (keeps containers)
docker-compose -f docker-compose.prod.yml stop

# Stop and remove containers
docker-compose -f docker-compose.prod.yml down

# Stop and remove containers + volumes
docker-compose -f docker-compose.prod.yml down -v
```

### Clean Up Images

```bash
# Remove built images
docker rmi property-intel-backend-prod
docker rmi property-intel-frontend-prod

# Remove all unused images
docker image prune -a

# Full cleanup (use with caution!)
docker system prune -a --volumes
```

---

## Common Issues & Solutions

### Issue: Frontend Build Fails - Missing Clerk Publishable Key

**Error:**

```
Error occurred prerendering page "/_not-found". Read more: https://nextjs.org/docs/messages/prerender-error
[Error: @clerk/clerk-react: Missing publishableKey...]
```

**Cause:** Next.js needs `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` during the build process for prerendering pages.

**Solutions:**

```bash
# 1. Ensure .env.production.local has the key
cat .env.production.local | grep NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY

# 2. Get a test key from Clerk Dashboard
# Visit: https://dashboard.clerk.com/last-active?path=api-keys
# Use pk_test_* for testing (pk_live_* for production)

# 3. Add to .env.production.local
echo "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_your_key_here" >> .env.production.local

# 4. Rebuild with the key
docker-compose -f docker-compose.prod.yml build frontend
```

### Issue: Database Connection Failed

**Error:** `Database connection failed` in health check

**Solutions:**

```bash
# 1. Check DATABASE_URL format
echo $DATABASE_URL

# 2. Test connection from host
psql $DATABASE_URL -c "SELECT 1"

# 3. Use host.docker.internal for local PostgreSQL
DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/property_intel

# 4. Check PostgreSQL is accepting connections
sudo service postgresql status  # Linux
brew services list  # macOS
```

### Issue: Port Already in Use

**Error:** `Bind for 0.0.0.0:8000 failed: port is already allocated`

**Solutions:**

```bash
# Check what's using the port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>

# Or change port in docker-compose.prod.yml
ports:
  - "8001:8000"  # Use different host port
```

### Issue: Frontend Can't Reach Backend

**Error:** `Failed to fetch` or connection refused

**Solutions:**

```bash
# 1. Verify backend is running
curl http://localhost:8000/health

# 2. Check NEXT_PUBLIC_API_URL uses container name
NEXT_PUBLIC_API_URL=http://backend:8000  # ✅ Correct
NEXT_PUBLIC_API_URL=http://localhost:8000  # ❌ Wrong (won't work between containers)

# 3. Verify both services are on same network
docker network inspect property-intel-network
```

### Issue: Health Check Failing

**Error:** `unhealthy` status in `docker ps`

**Solutions:**

```bash
# 1. Wait for start_period to elapse (30-40 seconds)
docker-compose -f docker-compose.prod.yml ps

# 2. Check logs for errors
docker-compose -f docker-compose.prod.yml logs backend

# 3. Test health endpoint manually
docker-compose -f docker-compose.prod.yml exec backend curl http://localhost:8000/health

# 4. Increase start_period in docker-compose.prod.yml
healthcheck:
  start_period: 60s  # Increase if services take longer to start
```

### Issue: Out of Memory

**Error:** Container exits with code 137 (OOM killed)

**Solutions:**

```bash
# 1. Increase memory limit in docker-compose.prod.yml
deploy:
  resources:
    limits:
      memory: 4G  # Increase as needed

# 2. Check Docker daemon memory allocation
docker info | grep Memory

# 3. Reduce gunicorn workers if memory constrained
CMD ["gunicorn", "app.main:app", "--workers", "2", ...]  # Reduce from 4 to 2
```

---

## Performance Optimization

### Adjust Gunicorn Workers

```dockerfile
# backend/Dockerfile
# Formula: (2 x CPU cores) + 1

# For 1-core instance
--workers 3

# For 2-core instance (current)
--workers 4

# For 4-core instance
--workers 9
```

### Enable Docker BuildKit (Faster Builds)

```bash
# Enable BuildKit
export DOCKER_BUILDKIT=1

# Or add to ~/.bashrc or ~/.zshrc
echo 'export DOCKER_BUILDKIT=1' >> ~/.zshrc
source ~/.zshrc

# Build with BuildKit
docker-compose -f docker-compose.prod.yml build
```

### Use Build Cache

```bash
# Build with cache (default)
docker-compose -f docker-compose.prod.yml build

# Build without cache (clean build)
docker-compose -f docker-compose.prod.yml build --no-cache

# Pull latest base images before building
docker-compose -f docker-compose.prod.yml build --pull
```

---

## Preparing for AWS Deployment

### Tag Images for ECR

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag images
docker tag property-intel-backend-prod:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/property-intel-backend:latest
docker tag property-intel-frontend-prod:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/property-intel-frontend:latest

# Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/property-intel-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/property-intel-frontend:latest
```

### Test with Production-Like Configuration

```bash
# Use production environment variables (without DEBUG=true)
ENVIRONMENT=production DEBUG=false docker-compose -f docker-compose.prod.yml up

# Test with real API keys (not test keys)
# Update .env.production.local with:
# CLERK_SECRET_KEY=sk_live_...
# OPENAI_API_KEY=sk-proj-...
```

---

## Next Steps

1. ✅ Test all endpoints work correctly
2. ✅ Verify health checks pass
3. ✅ Check logs for errors
4. ✅ Test user authentication flow
5. ✅ Test property submission workflow
6. ✅ Run database migrations (see Phase 6)
7. ✅ Proceed to Phase 4: Logging & Security

**Ready for Phase 4?** Let me know when you want to continue! 🚀
