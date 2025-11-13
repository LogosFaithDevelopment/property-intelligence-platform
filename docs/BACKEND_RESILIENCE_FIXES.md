# Backend Resilience Fixes - Deployment Summary

## Changes Made (October 18, 2025)

### Problem

ECS tasks were failing with Exit Code 3 and Circuit Breaker triggered because:

1. Database connection attempted at startup before security groups configured
2. Too many Gunicorn workers for 512 CPU / 1024 MB memory
3. Container crashed instead of staying alive for health checks

### Solution Applied

#### 1. Database Connection Retry Logic (`backend/app/database.py`)

- ✅ Added `connect_with_retry()` function
- ✅ Exponential backoff: 1s → 2s → 4s → 8s → 16s → 30s (max)
- ✅ Max 10 retry attempts before giving up
- ✅ Never exits on failure - logs error and continues
- ✅ Returns True/False for readiness tracking

#### 2. FastAPI Startup Resilience (`backend/app/main.py`)

- ✅ Changed lifespan to call `connect_with_retry()` instead of `create_tables()`
- ✅ Added `_ready` dict to track dependency states
- ✅ Updated `/` endpoint to simple liveness probe (always 200 OK)
- ✅ Added `/readyz` endpoint for readiness checks (returns 503 if DB not ready)
- ✅ Added `/info` endpoint for API information
- ✅ Added environment variable validation logging (logs missing vars, doesn't exit)
- ✅ Added early `logging.basicConfig()` for CloudWatch capture

#### 3. Gunicorn Optimization (`backend/Dockerfile`)

- ✅ Reduced workers from 4 to 2 (appropriate for 512 CPU units)
- ✅ Changed CMD to use `sh -c` wrapper for `${PORT:-8000}` variable expansion
- ✅ Added `--graceful-timeout 30` for clean shutdowns

#### 4. Health Check Configuration (`copilot/backend/manifest.yml`)

- ✅ Changed `healthcheck` from string to object with explicit parameters
- ✅ Changed `path` from `/health` to `/` (simplest guaranteed 200)
- ✅ Set `interval: 10s` (check every 10 seconds)
- ✅ Set `timeout: 5s` (fail if no response in 5 seconds)
- ✅ Set `healthy_threshold: 2` (2 consecutive passes = healthy)
- ✅ Set `unhealthy_threshold: 2` (2 consecutive fails = unhealthy)

### Endpoints Available

| Endpoint     | Purpose                           | Returns                        |
| ------------ | --------------------------------- | ------------------------------ |
| `/`          | Liveness probe (ALB health check) | Always 200 OK                  |
| `/readyz`    | Readiness probe (K8s-style)       | 200 if ready, 503 if not       |
| `/info`      | API information                   | Version, docs links, endpoints |
| `/health`    | Legacy health check               | Still works, detailed status   |
| `/health/db` | Database connectivity check       | Tests actual DB connection     |

### Expected Behavior After Deployment

1. **Container starts** → Immediately responds to `/` with 200 OK
2. **ALB health check passes** → Task marked as HEALTHY
3. **Database connection retries** → Up to 10 attempts over ~2 minutes
4. **If DB fails** → Container stays alive, `/readyz` returns 503, `/` still returns 200
5. **After security groups configured** → Next health check succeeds, DB becomes ready

### What This Fixes

✅ **Circuit Breaker issue** - Container no longer exits on DB failure  
✅ **Exit Code 3** - Container stays alive to serve health checks  
✅ **Missing logs** - Early logging to stdout/CloudWatch  
✅ **Resource thrashing** - Reduced workers from 4 to 2  
✅ **Port flexibility** - Honors ${PORT} environment variable

### Next Steps

1. Deploy with `copilot svc deploy --name backend --env production --force`
2. Monitor logs with `copilot svc logs --name backend --env production --follow`
3. Verify task reaches RUNNING state (no more EXIT 3)
4. Configure security groups to allow ECS → RDS (port 5432) and ECS → Redis (port 6379)
5. Watch `/readyz` endpoint transition from 503 to 200 after DB connection succeeds

### Rollback Plan (if needed)

All changes are backward compatible. If issues occur:

1. Previous `/health` endpoint still works
2. Database retry logic is non-breaking
3. Worker count reduction is conservative (can increase if needed)
4. Can revert manifest healthcheck to simple string format

### Monitoring Commands

```bash
# Check service status
copilot svc status --name backend --env production

# Follow logs in real-time
copilot svc logs --name backend --env production --follow

# Check previous task logs (if crashed)
copilot svc logs --name backend --env production --previous

# Test liveness endpoint (after ALB URL obtained)
curl http://<backend-alb-url>/

# Test readiness endpoint
curl http://<backend-alb-url>/readyz

# Test database health (after SG configured)
curl http://<backend-alb-url>/health/db
```

## Risk Assessment

**Low Risk Changes:**

- Liveness probe change (/ instead of /health)
- Environment variable logging
- Early stdout logging configuration

**Medium Risk Changes:**

- Database retry logic (new code path)
- Worker count reduction (performance impact)

**Mitigation:**

- All changes are non-breaking
- Legacy endpoints still work
- Can increase workers if performance insufficient
- Retry logic has max attempts to prevent infinite loops

## Success Criteria

✅ ECS task reaches RUNNING state  
✅ ALB health check passes  
✅ Logs appear in CloudWatch  
✅ No Exit Code 3 errors  
✅ No Circuit Breaker triggered  
✅ Container stays alive even if DB unreachable
