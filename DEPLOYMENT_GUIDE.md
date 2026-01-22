# AWS ECS Fargate Deployment Guide - CORRECTED FOR YOUR PROJECT

**Project:** Property Intelligence Platform  
**Last Updated:** October 17, 2025  
**Status:** Ready for Deployment

---

## ⚠️ CORRECTIONS FROM YOUR PLAN

### Critical Changes Made:

1. **Database Name:** Changed from `property_assessment_prod` → `property_intel_prod` (matches your codebase)
2. **App Name:** Changed from `property-assessment` → `property-intel` (consistency)
3. **RDS Username:** Keep as `admin` (NOT `postgres`) for better security
4. **Redis Required:** Added Redis setup (your app requires it - see requirements.txt)
5. **Environment Variables:** Updated to match your actual `config.py` structure
6. **Health Check Path:** Confirmed `/health` is correct ✅
7. **Port Configuration:** Backend uses 8000, Frontend uses 3000 ✅
8. **Missing Secrets:** Added `REDIS_URL`, `SECRET_KEY`, `SMARTY_WEBSITE_KEY`

---

## Prerequisites (Already Completed ✅)

- ✅ AWS Copilot CLI installed
- ✅ AWS CLI configured
- ✅ Docker running
- ✅ Production build tested (309MB frontend, 1.11GB backend)
- ✅ Database migrations ready (8 migrations tested)

---

## Architecture Overview

```
Internet → Application Load Balancer
    ├── Next.js Frontend (ECS Fargate)
    └── FastAPI Backend (ECS Fargate)
            ├── AWS RDS PostgreSQL + PostGIS
            └── AWS ElastiCache Redis
```

**Key Components:**

- **ECS Fargate**: Serverless containers (no EC2 management)
- **ECR**: Docker image registry
- **RDS PostgreSQL 15**: Managed database with PostGIS
- **ElastiCache Redis**: Managed cache/queue (for ARQ tasks)
- **Application LB**: Auto SSL, traffic routing
- **Secrets Manager**: Secure credential storage
- **CloudWatch Logs**: Centralized logging

---

## 🗄️ PHASE 1: Create AWS RDS Database

### Step 1.1: Create RDS Instance via AWS Console

1. Go to **RDS** → **Create database**

2. **Engine Configuration:**

   - Engine: **PostgreSQL**
   - Version: **15.4** or latest 15.x
   - Template: **Free tier** (if eligible) OR **Dev/Test**

3. **Settings:**

   - DB instance identifier: **`property-intel-prod`** ⚠️ (CORRECTED)
   - Master username: **`admin`** ⚠️ (CORRECTED - NOT postgres)
   - Master password: Generate strong password → **💾 SAVE THIS IMMEDIATELY!**

4. **Instance Configuration:**

   - DB instance class: **`db.t4g.micro`** (1 vCPU, 1 GB RAM)
   - Storage type: **General Purpose SSD (gp3)**
   - Allocated storage: **20 GB**
   - ✅ Enable storage autoscaling (max 100 GB)

5. **Connectivity:**

   - VPC: **Default VPC** (or your existing VPC)
   - Subnet group: **default**
   - Public access: **❌ NO** (security best practice)
   - VPC security group: **Create new**
     - Name: **`property-intel-rds-sg`**
   - Availability Zone: **No preference**

6. **Database Authentication:**

   - Authentication: **Password authentication**

7. **Additional Configuration:**

   - Initial database name: **`property_intel_prod`** ⚠️ (CORRECTED)
   - DB parameter group: **default.postgres15**
   - Backup retention period: **7 days**
   - Backup window: **03:00-04:00 UTC**
   - Maintenance window: **Sun:04:00-Sun:05:00 UTC**
   - ✅ Enable encryption
   - ✅ Enable Enhanced monitoring (60 seconds)
   - ✅ Enable Performance Insights (7 days free)
   - ✅ Enable automatic minor version upgrades

8. Click **Create database** (takes 5-10 minutes)

### Step 1.2: Enable PostGIS Extension (Do This After RDS is Available)

**Important:** You can't enable PostGIS until RDS is created. We'll do this in Phase 9.

### Step 1.3: Note Your RDS Endpoint

1. Wait for database status: **Available** (~5-10 min)
2. Click your database **property-intel-prod**
3. **Copy the Endpoint** from "Connectivity & security" tab
   - Format: `property-intel-prod.xxxxx.us-west-2.rds.amazonaws.com`
   - **💾 SAVE THIS!**

---

## 🔐 PHASE 2: Store Secrets in AWS Secrets Manager

### Step 2.1: Create Database Secret

1. Go to **Secrets Manager** → **Store a new secret**
2. Secret type: **Other type of secret**
3. **Key/value pairs** (click "Plaintext" tab and paste):

```json
{
  "username": "admin",
  "password": "YOUR_RDS_PASSWORD_FROM_STEP_1",
  "host": "property-intel-prod.xxxxx.us-west-2.rds.amazonaws.com",
  "port": 5432,
  "database": "property_intel_prod",
  "DATABASE_URL": "postgresql://admin:YOUR_RDS_PASSWORD@property-intel-prod.xxxxx.us-west-2.rds.amazonaws.com:5432/property_intel_prod"
}
```

4. Secret name: **`property-intel/prod/database`**
5. Click **Next** → **Next** → **Store**
6. **💾 Copy the Secret ARN** (e.g., `arn:aws:secretsmanager:us-west-2:123456789012:secret:property-intel/prod/database-AbCdEf`)

### Step 2.2: Create Backend Environment Secret

1. **Secrets Manager** → **Store a new secret**
2. **Key/value pairs** (Plaintext tab):

```json
{
  "SECRET_KEY": "GENERATE_WITH: openssl rand -hex 32",
  "CLERK_SECRET_KEY": "sk_live_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "CLERK_WEBHOOK_SECRET": "whsec_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "OPENAI_API_KEY": "sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "OPENAI_MODEL": "gpt-4o-mini",
  "ATTOM_API_KEY": "YOUR_ATTOM_KEY",
  "SMARTY_AUTH_ID": "YOUR_SMARTY_AUTH_ID",
  "SMARTY_AUTH_TOKEN": "YOUR_SMARTY_AUTH_TOKEN",
  "SMARTY_WEBSITE_KEY": "YOUR_SMARTY_WEBSITE_KEY",
  "CENSUS_API_KEY": "YOUR_CENSUS_KEY",
  "ENVIRONMENT": "production",
  "DEBUG": "false",
  "LOG_LEVEL": "INFO",
  "ALLOWED_ORIGINS": "[\"https://your-domain.com\"]",
  "ALLOWED_HOSTS": "[\"your-domain.com\",\"backend\"]"
}
```

3. Secret name: **`property-intel/prod/backend-env`**
4. **💾 Copy the Secret ARN**

### Step 2.3: Create Redis Secret (We'll populate this in Phase 3)

1. **Secrets Manager** → **Store a new secret**
2. **Key/value pairs**:

```json
{
  "REDIS_URL": "redis://placeholder:6379/0"
}
```

3. Secret name: **`property-intel/prod/redis`**
4. **💾 Copy Secret ARN**
5. ⚠️ **Note:** We'll update this with real Redis endpoint after creating ElastiCache in Phase 3

### Step 2.4: Create Frontend Environment Secret

1. **Secrets Manager** → **Store a new secret**
2. **Key/value pairs**:

```json
{
  "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY": "pk_live_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "NEXT_PUBLIC_API_URL": "https://api.your-domain.com",
  "NEXT_PUBLIC_CLERK_SIGN_IN_URL": "/sign-in",
  "NEXT_PUBLIC_CLERK_SIGN_UP_URL": "/sign-up",
  "NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL": "/submit-property",
  "NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL": "/submit-property"
}
```

3. Secret name: **`property-intel/prod/frontend-env`**
4. **💾 Copy Secret ARN**

---

## 🔴 PHASE 3: Create Redis (ElastiCache)

**⚠️ YOUR APP REQUIRES REDIS** - Your `requirements.txt` includes `redis==5.0.1` and `arq==0.25.0` (task queue).

### Step 3.1: Create ElastiCache Redis Cluster

1. Go to **ElastiCache** → **Redis clusters** → **Create**

2. **Cluster Configuration:**

   - Cluster mode: **Disabled**
   - Name: **`property-intel-redis-prod`**
   - Engine version: **7.0** or latest
   - Node type: **cache.t4g.micro** (free tier eligible)
   - Number of replicas: **0** (for dev) or **1** (for production HA)

3. **Subnet Group:**

   - Create new subnet group OR use default
   - Select same subnets as RDS

4. **Security:**

   - Security group: Create new → **`property-intel-redis-sg`**
   - Encryption at rest: ✅ Enabled
   - Encryption in transit: ✅ Enabled

5. **Backup:**

   - Automatic backups: ✅ Enabled
   - Retention period: 1 day

6. Click **Create**

### Step 3.2: Update Redis Secret

1. Wait for Redis status: **Available** (~5 min)
2. Click your cluster → Copy **Primary Endpoint**
   - Format: `property-intel-redis-prod.xxxxx.cache.amazonaws.com:6379`
3. Go to **Secrets Manager** → `property-intel/prod/redis`
4. Click **Retrieve secret value** → **Edit**
5. Update:

```json
{
  "REDIS_URL": "redis://property-intel-redis-prod.xxxxx.cache.amazonaws.com:6379/0"
}
```

6. Save

---

## 🚀 PHASE 4: Initialize AWS Copilot Application

### Step 4.1: Navigate to Project Root

```bash
cd /Users/adamsilver/Desktop/property-intelligence-platform
```

### Step 4.2: Initialize Application

```bash
copilot app init property-intel
```

**Expected Output:**

```
✔ Created the infrastructure to manage services and jobs under application property-intel.
```

This creates:

- `copilot/` directory in your project
- CloudFormation stacks in AWS
- Base infrastructure (VPC, subnets, service discovery)

### Step 4.3: Verify Application

```bash
copilot app ls
```

Should show: `property-intel`

---

## 🔧 PHASE 5: Create Backend Service (FastAPI)

### Step 5.1: Initialize Backend Service

```bash
copilot svc init
```

**When prompted:**

- Service type: **Backend Service** (internal, not directly exposed to internet)
- Service name: **`backend`** ⚠️ (SIMPLIFIED)
- Dockerfile: **`./backend/Dockerfile`** (confirm path)

### Step 5.2: Edit Backend Manifest

Open **`copilot/backend/manifest.yml`** and **REPLACE ENTIRE CONTENT** with:

```yaml
name: backend
type: Backend Service

image:
  build:
    dockerfile: ./backend/Dockerfile
    context: .
  port: 8000

cpu: 512 # 0.5 vCPU
memory: 1024 # 1 GB RAM

http:
  path: '/'
  healthcheck:
    path: /health
    port: 8000
    success_codes: '200'
    interval: 30s
    timeout: 5s
    healthy_threshold: 2
    unhealthy_threshold: 3
    start_period: 60s # Backend needs time to start

# Environment variables (non-secret)
variables:
  ENVIRONMENT: production
  DEBUG: false
  LOG_LEVEL: INFO

# Secrets from AWS Secrets Manager
secrets:
  DATABASE_URL: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/database:DATABASE_URL
  REDIS_URL: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/redis:REDIS_URL
  SECRET_KEY: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/backend:SECRET_KEY
  CLERK_SECRET_KEY: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/backend:CLERK_SECRET_KEY
  CLERK_WEBHOOK_SECRET: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/backend:CLERK_WEBHOOK_SECRET
  OPENAI_API_KEY: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/backend:OPENAI_API_KEY
  ATTOM_API_KEY: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/backend:ATTOM_API_KEY
  SMARTY_AUTH_ID: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/backend:SMARTY_AUTH_ID
  SMARTY_AUTH_TOKEN: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/backend:SMARTY_AUTH_TOKEN
  SMARTY_WEBSITE_KEY: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/backend:SMARTY_WEBSITE_KEY
  CENSUS_API_KEY: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/backend:CENSUS_API_KEY
  ALLOWED_ORIGINS: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/backend:ALLOWED_ORIGINS
  ALLOWED_HOSTS: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/backend:ALLOWED_HOSTS

# Service discovery for internal communication
network:
  vpc:
    placement: private

# Scaling configuration
count:
  range: 1-3
  cpu_percentage: 70
  memory_percentage: 80

# Auto-scaling (optional)
environments:
  production:
    count:
      range: 2-4 # Run 2-4 tasks in production
      cpu_percentage: 70
```

---

## 🌐 PHASE 6: Create Frontend Service (Next.js)

### Step 6.1: Initialize Frontend Service

```bash
copilot svc init
```

**When prompted:**

- Service type: **Load Balanced Web Service** (publicly accessible)
- Service name: **`frontend`** ⚠️ (SIMPLIFIED)
- Dockerfile: **`./frontend/Dockerfile`**

### Step 6.2: Edit Frontend Manifest

Open **`copilot/frontend/manifest.yml`** and **REPLACE ENTIRE CONTENT** with:

```yaml
name: frontend
type: Load Balanced Web Service

image:
  build:
    dockerfile: ./frontend/Dockerfile
    context: .
  port: 3000

cpu: 512 # 0.5 vCPU
memory: 1024 # 1 GB RAM

http:
  path: '/'
  healthcheck:
    path: /
    port: 3000
    success_codes: '200,301,302'
    interval: 30s
    timeout: 5s
    healthy_threshold: 2
    unhealthy_threshold: 3
    start_period: 40s # Next.js needs time to start

# Secrets from AWS Secrets Manager
secrets:
  NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/frontend:NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
  NEXT_PUBLIC_API_URL: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/frontend:NEXT_PUBLIC_API_URL
  NEXT_PUBLIC_CLERK_SIGN_IN_URL: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/frontend:NEXT_PUBLIC_CLERK_SIGN_IN_URL
  NEXT_PUBLIC_CLERK_SIGN_UP_URL: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/frontend:NEXT_PUBLIC_CLERK_SIGN_UP_URL
  NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/frontend:NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL
  NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/frontend:NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL

# Public internet access
network:
  vpc:
    placement: public

# Scaling configuration
count:
  range: 1-3
  cpu_percentage: 70

environments:
  production:
    count:
      range: 2-4
      cpu_percentage: 70
```

---

## 🏗️ PHASE 7: Create Production Environment

### Step 7.1: Initialize Environment

```bash
copilot env init --name production
```

**When prompted:**

- Credential source: **[profile default]** (use your AWS credentials)
- Would you like to use the default configuration: **Yes**

### Step 7.2: Deploy Environment Infrastructure

```bash
copilot env deploy --name production
```

**This creates:**

- VPC with public/private subnets across 2 AZs
- NAT Gateways for private subnet internet access
- Application Load Balancer
- Security groups
- Service discovery namespace
- CloudWatch log groups

**⏱️ Takes 10-15 minutes**

---

## 🔗 PHASE 8: Link Secrets to Copilot Environment

### Step 8.1: Link Database Secret

```bash
copilot secret init --name database --values production=arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:property-intel/prod/database-XXXXXX
```

Replace with your actual Secret ARN from Step 2.1.

### Step 8.2: Link Backend Secret

```bash
copilot secret init --name backend --values production=arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:property-intel/prod/backend-env-XXXXXX
```

### Step 8.3: Link Redis Secret

```bash
copilot secret init --name redis --values production=arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:property-intel/prod/redis-XXXXXX
```

### Step 8.4: Link Frontend Secret

```bash
copilot secret init --name frontend --values production=arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:property-intel/prod/frontend-env-XXXXXX
```

---

## 🔓 PHASE 9: Update Security Groups

### Step 9.1: Allow ECS → RDS Communication

1. **Get ECS Security Group ID:**

   - Go to **EC2** → **Security Groups**
   - Find: `copilot-property-intel-production-Cluster-xxxxx`
   - **💾 Copy Security Group ID** (e.g., `sg-0abc123def456`)

2. **Update RDS Security Group:**
   - Find: `property-intel-rds-sg`
   - Click **Edit inbound rules**
   - **Add rule:**
     - Type: **PostgreSQL**
     - Protocol: TCP
     - Port: **5432**
     - Source: **Custom** → Paste ECS Security Group ID
   - **Save rules**

### Step 9.2: Allow ECS → Redis Communication

1. **Find Redis Security Group:**

   - Go to **ElastiCache** → Your cluster → **Security groups**
   - OR find `property-intel-redis-sg` in EC2 Security Groups

2. **Edit Inbound Rules:**
   - Type: **Custom TCP**
   - Port: **6379**
   - Source: **Custom** → Paste ECS Security Group ID from Step 9.1
   - **Save rules**

---

## 🗃️ PHASE 10: Run Database Migrations

**⚠️ Important:** PostGIS extension must be enabled before migrations!

### Step 10.1: Enable PostGIS Extension

**Option A: From Local Machine (Temporary Bastion)**

1. **Temporarily enable RDS public access:**

   - Go to **RDS** → **property-intel-prod** → **Modify**
   - Public access: **Yes**
   - Apply immediately
   - Wait 5 minutes

2. **Add your IP to security group:**

   - RDS security group → Edit inbound rules
   - Add rule: PostgreSQL, Source = **My IP**

3. **Connect and enable PostGIS:**

```bash
# Install PostgreSQL client if needed
brew install postgresql@15  # macOS

# Connect to RDS
psql -h property-intel-prod.xxxxx.us-west-2.rds.amazonaws.com \
     -U admin \
     -d property_intel_prod \
     -p 5432

# Enter password when prompted

# Enable PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

# Verify
SELECT postgis_version();

# Exit
\q
```

4. **Disable public access again:**
   - RDS → Modify → Public access: **No**
   - Remove your IP from security group

**Option B: From ECS Task (After Backend Deployment)**

We'll do this after deploying backend service - you can exec into a running container.

### Step 10.2: Run Alembic Migrations

**After PostGIS is enabled:**

```bash
# Set DATABASE_URL
export DATABASE_URL="postgresql://admin:YOUR_PASSWORD@property-intel-prod.xxxxx.us-west-2.rds.amazonaws.com:5432/property_intel_prod"

# Navigate to backend
cd backend

# Run migrations
alembic upgrade head

# Verify
alembic current
```

**Expected output:**

```
INFO  [alembic.runtime.migration] Running upgrade  -> 000000000000, initial_schema
INFO  [alembic.runtime.migration] Running upgrade 000000000000 -> 001..., add_users_table
...
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> head
```

---

## 🚢 PHASE 11: Deploy Services

### Step 11.1: Deploy Backend Service

```bash
copilot svc deploy --name backend --env production
```

**What happens:**

1. Builds Docker image locally (1.11GB)
2. Pushes to Amazon ECR
3. Creates ECS task definition
4. Launches Fargate tasks
5. Registers with service discovery
6. Configures health checks

**⏱️ Takes 5-10 minutes**

**Monitor deployment:**

```bash
copilot svc status --name backend --env production
```

### Step 11.2: Verify Backend Health

```bash
# View logs
copilot svc logs --name backend --env production --follow

# Check for successful startup:
# ✅ "Logging configured"
# ✅ "Database tables created successfully"
# ✅ "Application startup complete"
```

### Step 11.3: Get Backend Internal URL

```bash
copilot svc show --name backend --env production
```

**Copy the Service Discovery URL:**

- Format: `backend.production.property-intel.local:8000`
- **💾 Save this for frontend configuration**

### Step 11.4: Update Frontend Secret with Backend URL

1. Go to **Secrets Manager** → `property-intel/prod/frontend-env`
2. **Edit secret value**
3. Update:

```json
{
  "NEXT_PUBLIC_API_URL": "http://backend.production.property-intel.local:8000",
  ...
}
```

4. **Save**

⚠️ **Note:** Use `http://` (not `https://`) for internal service-to-service communication.

### Step 11.5: Deploy Frontend Service

```bash
copilot svc deploy --name frontend --env production
```

**⏱️ Takes 5-10 minutes**

### Step 11.6: Get Frontend Public URL

```bash
copilot svc show --name frontend --env production
```

**Copy the Load Balancer URL:**

- Format: `http://property-intel-Publi-XXXXX.us-west-2.elb.amazonaws.com`
- **🎉 This is your public application URL!**

### Step 11.7: Test Application

1. **Open frontend URL in browser**
2. **Verify:**
   - ✅ Page loads
   - ✅ Clerk authentication works
   - ✅ Can submit property form
   - ✅ Admin portal accessible
   - ✅ Backend API calls work

---

## 🌐 PHASE 12: Configure Custom Domain (Optional)

### Step 12.1: Add Domain to Route 53

1. **Route 53** → **Hosted zones** → **Create hosted zone**
2. Domain name: `yourdomain.com`
3. **Copy the 4 nameservers** (e.g., `ns-123.awsdns-12.com`)
4. **Update at your domain registrar** (GoDaddy, Namecheap, etc.)
   - Replace nameservers with AWS Route 53 ones
   - ⏱️ Takes 24-48 hours to propagate

### Step 12.2: Request SSL Certificate

1. **Certificate Manager** → **Request certificate**
2. Certificate type: **Public certificate**
3. Domain names:
   - `yourdomain.com`
   - `*.yourdomain.com` (wildcard for subdomains)
4. Validation method: **DNS validation**
5. **Request**
6. Click **Create records in Route 53** (adds CNAME automatically)
7. Wait for status: **Issued** (~5-10 minutes)

### Step 12.3: Add Custom Domain to Frontend

Edit **`copilot/frontend/manifest.yml`**:

```yaml
http:
  path: '/'
  alias: yourdomain.com # Add this line
  healthcheck: ...
```

### Step 12.4: Redeploy Frontend

```bash
copilot svc deploy --name frontend --env production
```

Copilot will:

- Attach SSL certificate to load balancer
- Create Route 53 A record pointing to ALB
- Enable HTTPS automatically

### Step 12.5: Verify Custom Domain

1. Wait 5-10 minutes for DNS propagation
2. Visit: `https://yourdomain.com`
3. Verify SSL certificate (🔒 in browser)

---

## 🔐 PHASE 13: Update Clerk Production Settings

### Step 13.1: Add Production URLs to Clerk

1. Go to **[Clerk Dashboard](https://dashboard.clerk.com)**
2. Select your **production application**
3. Navigate to **API Keys** → Confirm you're using production keys (`pk_live_*`, `sk_live_*`)

4. **Paths** → Update:

   - Sign-in URL: `/sign-in`
   - Sign-up URL: `/sign-up`
   - After sign-in URL: `/submit-property`
   - After sign-up URL: `/submit-property`

5. **Domains** → Add allowed domains:

   - `https://yourdomain.com` (or your ALB URL)
   - Click **Add domain**

6. **Webhooks** → Update endpoint:
   - URL: `http://backend.production.property-intel.local:8000/webhooks/clerk`
   - Subscribe to events: `user.created`, `user.updated`, `user.deleted`
   - ⚠️ Use internal URL (backend service discovery)

---

## ✅ PHASE 14: Verify Full Deployment

### Step 14.1: Check All Services Running

```bash
# List all services
copilot svc ls

# Check backend status
copilot svc status --name backend --env production

# Check frontend status
copilot svc status --name frontend --env production
```

**Expected:**

```
✔ Service: backend
  Status:    ACTIVE
  Running:   2 / 2 tasks
  Health:    ✔ Healthy

✔ Service: frontend
  Status:    ACTIVE
  Running:   2 / 2 tasks
  Health:    ✔ Healthy
```

### Step 14.2: View CloudWatch Logs

```bash
# Backend logs (follow)
copilot svc logs --name backend --env production --follow

# Frontend logs (follow)
copilot svc logs --name frontend --env production --follow

# Filter for errors
copilot svc logs --name backend --env production --filter "ERROR"
```

### Step 14.3: End-to-End Testing

**Test Checklist:**

- [ ] **Frontend loads** at public URL
- [ ] **Clerk authentication:**
  - [ ] Sign up new user
  - [ ] Sign in existing user
  - [ ] Sign out
- [ ] **Submit property form:**
  - [ ] Fill all fields
  - [ ] Upload documents
  - [ ] Submit successfully
- [ ] **Admin portal:**
  - [ ] Login as admin
  - [ ] View submissions list
  - [ ] View submission details
  - [ ] Generate AI assessment
  - [ ] Download PDF report
- [ ] **Backend APIs:**
  - [ ] Health check: `/health`
  - [ ] Database health: `/health/db`

### Step 14.4: Monitor Performance

1. **CloudWatch** → **Dashboards**

   - View CPU/Memory usage
   - Check request count
   - Monitor error rates

2. **ECS** → **Clusters** → **property-intel-production**

   - View service metrics
   - Check task count
   - Monitor deployments

3. **RDS** → **property-intel-prod**
   - Performance Insights
   - Database connections
   - Query performance

---

## 📊 PHASE 15: Set Up Monitoring & Alarms

### Step 15.1: Create CloudWatch Alarms

**Backend High CPU:**

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name property-intel-backend-high-cpu \
  --alarm-description "Backend CPU above 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --dimensions Name=ServiceName,Value=backend Name=ClusterName,Value=property-intel-production-Cluster
```

**Backend High Memory:**

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name property-intel-backend-high-memory \
  --alarm-description "Backend memory above 80%" \
  --metric-name MemoryUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --dimensions Name=ServiceName,Value=backend Name=ClusterName,Value=property-intel-production-Cluster
```

**RDS High CPU:**

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name property-intel-rds-high-cpu \
  --alarm-description "RDS CPU above 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/RDS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --dimensions Name=DBInstanceIdentifier,Value=property-intel-prod
```

### Step 15.2: Enable AWS Cost Alerts

1. **Billing** → **Budgets** → **Create budget**
2. Budget type: **Cost budget**
3. Budget amount: **$100/month** (adjust as needed)
4. Alert threshold: **80%** of budgeted amount
5. Email: Your email for notifications

---

## 🛠️ Useful Commands

### Service Management

```bash
# List all services
copilot svc ls

# Show service details
copilot svc show --name backend --env production

# View service status
copilot svc status --name backend --env production

# View logs (live)
copilot svc logs --name backend --env production --follow

# View logs (last hour)
copilot svc logs --name backend --env production --since 1h

# Execute command in running container
copilot svc exec --name backend --env production --command "/bin/bash"
```

### Deployment & Updates

```bash
# Deploy service (after code changes)
copilot svc deploy --name backend --env production

# Force new deployment (same image)
copilot svc deploy --name backend --env production --force

# Deploy specific image tag
copilot svc deploy --name backend --env production --tag v1.2.3
```

### Scaling

```bash
# Scale manually (edit manifest.yml first)
vim copilot/backend/manifest.yml
# Change: count: range: 2-6
copilot svc deploy --name backend --env production
```

### Troubleshooting

```bash
# Check task stopped reason
copilot svc status --name backend --env production --json | jq '.tasks[].stoppedReason'

# View recent events
copilot svc status --name backend --env production

# Check health check failures
copilot svc logs --name backend --env production --filter "health"
```

### Cleanup (If Needed)

```bash
# Delete a service
copilot svc delete --name backend --env production

# Delete environment
copilot env delete --name production

# Delete entire application (⚠️ CAREFUL!)
copilot app delete
```

---

## 💰 Monthly Cost Estimate

| Resource                      | Configuration                    | Monthly Cost |
| ----------------------------- | -------------------------------- | ------------ |
| **ECS Fargate**               | 2 backend tasks (0.5 vCPU, 1GB)  | ~$25         |
| **ECS Fargate**               | 2 frontend tasks (0.5 vCPU, 1GB) | ~$25         |
| **RDS PostgreSQL**            | db.t4g.micro (20GB)              | ~$18         |
| **ElastiCache Redis**         | cache.t4g.micro                  | ~$12         |
| **Application Load Balancer** | 1 ALB                            | ~$16         |
| **NAT Gateway**               | 2 AZs                            | ~$64         |
| **ECR Storage**               | ~2 GB images                     | ~$0.20       |
| **CloudWatch Logs**           | 5 GB/month                       | ~$2.50       |
| **Data Transfer**             | 10 GB out                        | ~$0.90       |
| **Secrets Manager**           | 4 secrets                        | ~$1.60       |

**Total: ~$165/month** (low-medium traffic)

**💡 Cost Savings Tips:**

- Use 1 NAT Gateway instead of 2 (-$32/month)
- Use Fargate Spot for non-critical tasks (-30% compute)
- Enable S3 Intelligent-Tiering for document storage
- Set CloudWatch Logs retention to 7 days
- Use RDS Reserved Instances for 1-year commitment (-35%)

---

## 🔥 Common Issues & Solutions

### Issue 1: Service Won't Start

**Symptoms:** Tasks keep stopping, never reach "RUNNING"

**Check:**

```bash
copilot svc status --name backend --env production
copilot svc logs --name backend --env production --since 30m
```

**Common Causes:**

- Missing environment variables → Check Secrets Manager mappings
- Can't pull Docker image → Check ECR permissions
- Health check failing immediately → Verify `/health` endpoint works
- Database connection failed → Check security group rules

**Solutions:**

1. Verify all secret ARNs are correct in manifest.yml
2. Check ECS task execution role has `secretsmanager:GetSecretValue`
3. Ensure health check `start_period` is long enough (60s for backend)
4. Verify RDS security group allows ECS security group

### Issue 2: Health Checks Failing

**Symptoms:** Tasks reach RUNNING but ALB marks unhealthy

**Check:**

```bash
# Test health endpoint from within task
copilot svc exec --name backend --env production --command "curl http://localhost:8000/health"
```

**Common Causes:**

- Security group blocks ALB → ECS traffic
- Application not listening on correct port
- Health check path wrong
- Database connection slow

**Solutions:**

1. Check ECS security group allows inbound from ALB security group
2. Verify `EXPOSE 8000` in Dockerfile
3. Confirm `/health` returns 200 OK
4. Increase `start_period` and `timeout` in manifest

### Issue 3: Can't Connect to RDS

**Symptoms:** `Connection refused` or `Network unreachable`

**Check:**

```bash
# From ECS task
copilot svc exec --name backend --env production --command "/bin/bash"
# Inside container:
curl -v telnet://property-intel-prod.xxxxx.rds.amazonaws.com:5432
```

**Solutions:**

1. **Add ECS SG to RDS inbound rules:**
   - RDS security group → Allow port 5432 from ECS security group
2. **Verify DATABASE_URL format:**
   - `postgresql://admin:PASSWORD@ENDPOINT:5432/property_intel_prod`
3. **Check RDS status:**
   - Must be "Available" (not "Backing up" or "Modifying")

### Issue 4: Frontend Can't Reach Backend

**Symptoms:** API calls fail, CORS errors

**Check browser console:**

```javascript
// Look for:
// "Failed to fetch" or "CORS error"
```

**Solutions:**

1. **Update `NEXT_PUBLIC_API_URL` in frontend secret:**
   - Use internal service discovery: `http://backend.production.property-intel.local:8000`
2. **Update backend `ALLOWED_ORIGINS`:**
   - Add frontend public URL: `["https://yourdomain.com"]`
3. **Redeploy both services:**

```bash
copilot svc deploy --name backend --env production
copilot svc deploy --name frontend --env production
```

### Issue 5: High Costs

**Monitor:**

```bash
# Check current spend
aws ce get-cost-and-usage \
  --time-period Start=2025-10-01,End=2025-10-17 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=SERVICE
```

**Cost Optimization:**

1. **Reduce NAT Gateway:**
   - Use 1 instead of 2 (-$32/month)
   - Or use VPC endpoints for AWS services
2. **Use Fargate Spot:**
   - Edit manifest: `capacity: FARGATE_SPOT` (-30% compute)
3. **Scale down in off-hours:**
   - Set count to 1 during nights/weekends
4. **Optimize Docker images:**
   - Already done: 309MB frontend, 1.11GB backend ✅
5. **Set log retention:**

```bash
aws logs put-retention-policy \
  --log-group-name /copilot/property-intel/production/backend \
  --retention-in-days 7
```

---

## ✅ Production Checklist

### Pre-Deployment

- [x] Production Docker build tested locally
- [x] Database migrations tested
- [x] All environment variables documented
- [x] Clerk production app created with production keys
- [x] All API keys obtained (OpenAI, ATTOM, SmartyStreets)

### Infrastructure

- [ ] AWS account configured
- [ ] RDS PostgreSQL created
- [ ] PostGIS extension enabled
- [ ] ElastiCache Redis created
- [ ] Security groups configured
- [ ] Secrets Manager populated

### Deployment

- [ ] Copilot app initialized
- [ ] Backend service deployed
- [ ] Frontend service deployed
- [ ] Database migrations run
- [ ] Health checks passing

### Configuration

- [ ] Custom domain configured (optional)
- [ ] SSL certificate attached
- [ ] Clerk URLs updated
- [ ] CORS origins configured

### Monitoring

- [ ] CloudWatch alarms created
- [ ] Cost budget alerts set
- [ ] Log retention configured
- [ ] Performance metrics reviewed

### Testing

- [ ] Frontend loads correctly
- [ ] Authentication working
- [ ] Form submission working
- [ ] Admin portal accessible
- [ ] PDF generation working
- [ ] Backend APIs responding

---

## 🎯 Next Steps After Deployment

1. **Set up CI/CD Pipeline:**

   - GitHub Actions → Build → Push to ECR → Deploy via Copilot
   - Auto-deploy on merge to `main` branch

2. **Add Staging Environment:**

```bash
copilot env init --name staging
copilot svc deploy --name backend --env staging
```

3. **Implement Blue/Green Deployments:**

   - Zero-downtime updates
   - Automated rollback on failure

4. **Enhanced Monitoring:**

   - Sentry for error tracking
   - DataDog/New Relic for APM
   - Custom CloudWatch dashboards

5. **Backup & Disaster Recovery:**

   - Automated RDS snapshots (already enabled ✅)
   - Cross-region backup replication
   - Documented recovery procedures

6. **Performance Optimization:**
   - Enable CloudFront CDN
   - Implement Redis caching
   - Add database read replicas

---

## 📚 Additional Resources

- [AWS Copilot CLI Docs](https://aws.github.io/copilot-cli/)
- [Your README.prod.md](../README.prod.md) - Manual AWS CLI guide
- [Database Migrations Guide](./DATABASE_MIGRATIONS_GUIDE.md)
- [Clerk Production Setup](./CLERK_PRODUCTION_SETUP.md)
- [AWS Secrets Manager Setup](./AWS_SECRETS_MANAGER_SETUP.md)

---

**Ready to deploy?** Start with Phase 1: Create RDS Database! 🚀

**Questions or issues?** Check the troubleshooting section or review CloudWatch logs.

**Good luck with your deployment!** 🎉
