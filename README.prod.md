# Production Deployment Guide

**Property Intelligence Platform - AWS ECS Fargate Deployment**  
**Last Updated:** October 17, 2025  
**Version:** 1.0

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Environment Variables Reference](#environment-variables-reference)
4. [AWS Infrastructure Setup](#aws-infrastructure-setup)
5. [Database Setup](#database-setup)
6. [Secrets Management](#secrets-management)
7. [Docker Image Preparation](#docker-image-preparation)
8. [ECS Deployment](#ecs-deployment)
9. [Health Checks & Monitoring](#health-checks--monitoring)
10. [Troubleshooting](#troubleshooting)
11. [Rollback Procedures](#rollback-procedures)

---

## 📖 Overview

This guide covers the complete deployment process for the Property Intelligence Platform to AWS ECS Fargate. The application consists of:

- **Frontend:** Next.js 15.5.4 standalone server (309MB Docker image)
- **Backend:** FastAPI with Gunicorn/Uvicorn (1.11GB Docker image)
- **Database:** PostgreSQL 15 with PostGIS (AWS RDS)
- **Cache:** Redis 7 (AWS ElastiCache or ECS)
- **Queue:** ARQ with Redis backend

### Architecture

```
                                    ┌─────────────────────┐
                                    │   Route 53 (DNS)    │
                                    └──────────┬──────────┘
                                              │
                                    ┌─────────▼──────────┐
                                    │  Application LB    │
                                    │  (port 80/443)     │
                                    └──────────┬─────────┘
                                              │
                        ┌─────────────────────┼─────────────────────┐
                        │                     │                     │
              ┌─────────▼────────┐  ┌────────▼────────┐  ┌────────▼────────┐
              │   Frontend ECS   │  │  Backend ECS    │  │   Redis ECS     │
              │   (port 3000)    │  │  (port 8000)    │  │  (port 6379)    │
              │   309MB image    │  │  1.11GB image   │  │   7-alpine      │
              └──────────────────┘  └────────┬────────┘  └─────────────────┘
                                              │
                                    ┌─────────▼──────────┐
                                    │   RDS PostgreSQL   │
                                    │   (PostGIS 15)     │
                                    └────────────────────┘
```

---

## 🔐 Prerequisites

### Required Tools

- [x] AWS CLI v2 configured with appropriate credentials
- [x] Docker Desktop or Docker Engine
- [x] AWS Copilot CLI (optional but recommended)
- [x] PostgreSQL client (psql) for database operations

### AWS Account Requirements

- [x] AWS Account with admin or sufficient IAM permissions
- [x] ECS, ECR, RDS, ElastiCache, and Secrets Manager access
- [x] VPC with public and private subnets
- [x] NAT Gateway configured for private subnets
- [x] Security groups created

### External Services

- [x] Clerk production account (pk*live*_ and sk*live*_ keys)
- [x] OpenAI API key with billing enabled
- [x] ATTOM API key (property data)
- [x] SmartyStreets API credentials
- [x] US Census API key (optional but recommended)

---

## 🔑 Environment Variables Reference

### Complete Environment Variable List

Copy to `.env.production` and fill in all values:

```bash
# =============================================================================
# PRODUCTION ENVIRONMENT CONFIGURATION
# =============================================================================

# -----------------------------------------------------------------------------
# Application Settings
# -----------------------------------------------------------------------------
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# -----------------------------------------------------------------------------
# Security Settings
# -----------------------------------------------------------------------------
# Generate with: openssl rand -hex 32
SECRET_KEY=your-production-secret-key-64-characters-minimum-random-string

# CORS allowed origins (JSON array format required)
ALLOWED_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]

# Allowed hosts (JSON array format required)
ALLOWED_HOSTS=["yourdomain.com","www.yourdomain.com","backend-service"]

# -----------------------------------------------------------------------------
# Database Configuration
# -----------------------------------------------------------------------------
# Format: postgresql://username:password@host:port/database
DATABASE_URL=postgresql://admin:YourSecurePassword@your-rds-endpoint.region.rds.amazonaws.com:5432/property_intel

# Database pool settings
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=10
DB_POOL_TIMEOUT=30

# -----------------------------------------------------------------------------
# Redis Configuration
# -----------------------------------------------------------------------------
# ElastiCache endpoint or ECS service discovery
REDIS_URL=redis://your-redis-endpoint.cache.amazonaws.com:6379/0

# -----------------------------------------------------------------------------
# Clerk Authentication (Production Keys)
# -----------------------------------------------------------------------------
# Get from: https://dashboard.clerk.com
CLERK_SECRET_KEY=sk_live_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
CLERK_WEBHOOK_SECRET=whsec_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Frontend Clerk key (public)
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Clerk URLs (use your production domain)
NEXT_PUBLIC_CLERK_SIGN_IN_URL=/sign-in
NEXT_PUBLIC_CLERK_SIGN_UP_URL=/sign-up
NEXT_PUBLIC_CLERK_AFTER_SIGN_IN_URL=/submit-property
NEXT_PUBLIC_CLERK_AFTER_SIGN_UP_URL=/submit-property

# -----------------------------------------------------------------------------
# AI Services
# -----------------------------------------------------------------------------
# OpenAI API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# OpenAI settings
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=4000
OPENAI_TEMPERATURE=0.7

# -----------------------------------------------------------------------------
# Property Data APIs
# -----------------------------------------------------------------------------
# ATTOM API from: https://api.gateway.attomdata.com
ATTOM_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
ATTOM_BASE_URL=https://api.gateway.attomdata.com/propertyapi/v1.0.0

# SmartyStreets from: https://www.smarty.com
SMARTY_AUTH_ID=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX
SMARTY_AUTH_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXX
SMARTY_LICENSE=us-core-cloud

# US Census API from: https://api.census.gov/data/key_signup.html
CENSUS_API_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# FEMA API (no key required)
FEMA_BASE_URL=https://www.fema.gov/api/open/v2

# -----------------------------------------------------------------------------
# Task Queue (ARQ)
# -----------------------------------------------------------------------------
ARQ_REDIS_URL=${REDIS_URL}
ARQ_MAX_JOBS=10
ARQ_JOB_TIMEOUT=3600

# -----------------------------------------------------------------------------
# Email Configuration (Optional - for notifications)
# -----------------------------------------------------------------------------
# SMTP_HOST=email-smtp.us-west-2.amazonaws.com
# SMTP_PORT=587
# SMTP_USER=your-ses-smtp-username
# SMTP_PASSWORD=your-ses-smtp-password
# SMTP_FROM=noreply@yourdomain.com

# -----------------------------------------------------------------------------
# Monitoring & Logging
# -----------------------------------------------------------------------------
# Sentry DSN (optional but recommended)
# SENTRY_DSN=https://XXXX@XXXX.ingest.sentry.io/XXXX

# CloudWatch log group (created automatically by ECS)
# LOG_GROUP=/ecs/property-intel

# -----------------------------------------------------------------------------
# Frontend API Endpoint
# -----------------------------------------------------------------------------
# Points to backend ALB or service discovery
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### Required vs Optional Variables

**CRITICAL (Required for startup):**

- `SECRET_KEY`
- `DATABASE_URL`
- `CLERK_SECRET_KEY`
- `CLERK_WEBHOOK_SECRET`
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`
- `OPENAI_API_KEY`

**Important (Required for full functionality):**

- `ATTOM_API_KEY`
- `SMARTY_AUTH_ID`
- `SMARTY_AUTH_TOKEN`
- `REDIS_URL`

**Optional (Enhanced features):**

- `CENSUS_API_KEY`
- `SENTRY_DSN`
- SMTP configuration

---

## 🏗️ AWS Infrastructure Setup

### Step 1: Create VPC and Networking

```bash
# Create VPC with public and private subnets
aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=property-intel-vpc}]'

# Create public subnet (for ALB)
aws ec2 create-subnet \
  --vpc-id vpc-xxxxxxxxx \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-west-2a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=property-intel-public-1a}]'

# Create private subnet (for ECS tasks)
aws ec2 create-subnet \
  --vpc-id vpc-xxxxxxxxx \
  --cidr-block 10.0.10.0/24 \
  --availability-zone us-west-2a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=property-intel-private-1a}]'

# Create and attach Internet Gateway
aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=property-intel-igw}]'

aws ec2 attach-internet-gateway \
  --vpc-id vpc-xxxxxxxxx \
  --internet-gateway-id igw-xxxxxxxxx

# Create NAT Gateway for private subnet egress
aws ec2 allocate-address --domain vpc
aws ec2 create-nat-gateway \
  --subnet-id subnet-xxxxxxxxx \
  --allocation-id eipalloc-xxxxxxxxx
```

### Step 2: Create Security Groups

```bash
# ALB Security Group (allow 80/443 from internet)
aws ec2 create-security-group \
  --group-name property-intel-alb-sg \
  --description "Security group for ALB" \
  --vpc-id vpc-xxxxxxxxx

aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id sg-xxxxxxxxx \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# ECS Tasks Security Group (allow from ALB only)
aws ec2 create-security-group \
  --group-name property-intel-ecs-sg \
  --description "Security group for ECS tasks" \
  --vpc-id vpc-xxxxxxxxx

aws ec2 authorize-security-group-ingress \
  --group-id sg-yyyyyyyyyyy \
  --protocol tcp \
  --port 3000 \
  --source-group sg-xxxxxxxxx

aws ec2 authorize-security-group-ingress \
  --group-id sg-yyyyyyyyyyy \
  --protocol tcp \
  --port 8000 \
  --source-group sg-xxxxxxxxx

# RDS Security Group (allow from ECS only)
aws ec2 create-security-group \
  --group-name property-intel-rds-sg \
  --description "Security group for RDS" \
  --vpc-id vpc-xxxxxxxxx

aws ec2 authorize-security-group-ingress \
  --group-id sg-zzzzzzzzzzz \
  --protocol tcp \
  --port 5432 \
  --source-group sg-yyyyyyyyyyy
```

### Step 3: Create ECS Cluster

```bash
# Create Fargate cluster
aws ecs create-cluster \
  --cluster-name property-intel-prod \
  --capacity-providers FARGATE FARGATE_SPOT \
  --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1,base=1

# Create CloudWatch log groups
aws logs create-log-group --log-group-name /ecs/property-intel-frontend
aws logs create-log-group --log-group-name /ecs/property-intel-backend

# Set retention (optional)
aws logs put-retention-policy \
  --log-group-name /ecs/property-intel-frontend \
  --retention-in-days 30

aws logs put-retention-policy \
  --log-group-name /ecs/property-intel-backend \
  --retention-in-days 30
```

---

## 🗄️ Database Setup

### Step 1: Create RDS PostgreSQL Instance

**Using AWS Console:**

1. Navigate to RDS → Create database
2. Choose PostgreSQL version 15.x
3. Select "Production" template
4. Configure instance:
   - **DB instance identifier:** `property-intel-prod`
   - **Master username:** `admin`
   - **Master password:** Generate secure password (save to Secrets Manager)
   - **DB instance class:** `db.t3.medium` (adjust based on load)
   - **Storage:** 100 GB GP3, enable autoscaling
5. Configure connectivity:
   - **VPC:** Select your VPC
   - **Subnet group:** Private subnets
   - **Public access:** No
   - **VPC security group:** `property-intel-rds-sg`
6. Additional configuration:
   - **Initial database name:** `property_intel`
   - **Backup retention:** 7 days
   - **Backup window:** 03:00-04:00 UTC
   - **Maintenance window:** Sun:04:00-Sun:05:00 UTC
   - **Enable Enhanced monitoring:** Yes
   - **Enable Performance Insights:** Yes (7 days retention)

**Using AWS CLI:**

```bash
aws rds create-db-instance \
  --db-instance-identifier property-intel-prod \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 15.4 \
  --master-username admin \
  --master-user-password $(aws secretsmanager get-random-password --output text) \
  --allocated-storage 100 \
  --storage-type gp3 \
  --storage-encrypted \
  --vpc-security-group-ids sg-zzzzzzzzzzz \
  --db-subnet-group-name property-intel-db-subnet-group \
  --backup-retention-period 7 \
  --preferred-backup-window 03:00-04:00 \
  --preferred-maintenance-window sun:04:00-sun:05:00 \
  --enable-cloudwatch-logs-exports '["postgresql"]' \
  --db-name property_intel \
  --publicly-accessible false
```

### Step 2: Enable PostGIS Extension

```bash
# Connect to RDS instance (from bastion host or ECS task)
psql -h property-intel-prod.xxxxx.us-west-2.rds.amazonaws.com \
     -U admin \
     -d property_intel

# Enable PostGIS
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

# Verify
SELECT postgis_version();
\q
```

### Step 3: Run Database Migrations

**From ECS Task (Recommended):**

```bash
# Create one-off ECS task for migrations
aws ecs run-task \
  --cluster property-intel-prod \
  --task-definition property-intel-backend:latest \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxxxxxxxx],securityGroups=[sg-yyyyyyyyyyy],assignPublicIp=DISABLED}" \
  --overrides '{
    "containerOverrides": [{
      "name": "backend",
      "command": ["alembic", "upgrade", "head"]
    }]
  }'
```

**From Local Machine (via Bastion/VPN):**

```bash
# Set DATABASE_URL to RDS endpoint
export DATABASE_URL=postgresql://admin:password@property-intel-prod.xxxxx.us-west-2.rds.amazonaws.com:5432/property_intel

# Run migrations
cd backend
alembic upgrade head

# Verify current version
alembic current
```

**See Also:** [Database Migrations Guide](./DATABASE_MIGRATIONS_GUIDE.md)

---

## 🔐 Secrets Management

### Using AWS Secrets Manager

**Step 1: Store Database Credentials**

```bash
# Create database secret
aws secretsmanager create-secret \
  --name property-intel/prod/database \
  --description "RDS PostgreSQL credentials" \
  --secret-string '{
    "username": "admin",
    "password": "YourSecurePassword",
    "host": "property-intel-prod.xxxxx.us-west-2.rds.amazonaws.com",
    "port": 5432,
    "database": "property_intel",
    "url": "postgresql://admin:YourSecurePassword@property-intel-prod.xxxxx.us-west-2.rds.amazonaws.com:5432/property_intel"
  }'
```

**Step 2: Store API Keys**

```bash
# Clerk credentials
aws secretsmanager create-secret \
  --name property-intel/prod/clerk \
  --secret-string '{
    "secret_key": "sk_live_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "webhook_secret": "whsec_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "publishable_key": "pk_live_XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
  }'

# OpenAI API key
aws secretsmanager create-secret \
  --name property-intel/prod/openai \
  --secret-string '{
    "api_key": "sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
  }'

# ATTOM API
aws secretsmanager create-secret \
  --name property-intel/prod/attom \
  --secret-string '{
    "api_key": "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
  }'

# SmartyStreets
aws secretsmanager create-secret \
  --name property-intel/prod/smarty \
  --secret-string '{
    "auth_id": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
    "auth_token": "XXXXXXXXXXXXXXXXXXXXXXXX"
  }'
```

**Step 3: Grant ECS Task Role Access**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue",
        "secretsmanager:DescribeSecret"
      ],
      "Resource": [
        "arn:aws:secretsmanager:us-west-2:ACCOUNT_ID:secret:property-intel/prod/*"
      ]
    }
  ]
}
```

**See Also:** [AWS Secrets Manager Setup Guide](./AWS_SECRETS_MANAGER_SETUP.md)

---

## 🐳 Docker Image Preparation

### Step 1: Create ECR Repositories

```bash
# Frontend repository
aws ecr create-repository \
  --repository-name property-intel/frontend \
  --image-scanning-configuration scanOnPush=true \
  --encryption-configuration encryptionType=AES256

# Backend repository
aws ecr create-repository \
  --repository-name property-intel/backend \
  --image-scanning-configuration scanOnPush=true \
  --encryption-configuration encryptionType=AES256

# Get login credentials
aws ecr get-login-password --region us-west-2 | \
  docker login --username AWS --password-stdin ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com
```

### Step 2: Build and Tag Images

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Tag for ECR
docker tag property-intelligence-platform-frontend:latest \
  ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/property-intel/frontend:latest

docker tag property-intelligence-platform-backend:latest \
  ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/property-intel/backend:latest

# Also tag with version/git commit
GIT_COMMIT=$(git rev-parse --short HEAD)
docker tag property-intelligence-platform-frontend:latest \
  ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/property-intel/frontend:${GIT_COMMIT}

docker tag property-intelligence-platform-backend:latest \
  ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/property-intel/backend:${GIT_COMMIT}
```

### Step 3: Push to ECR

```bash
# Push frontend
docker push ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/property-intel/frontend:latest
docker push ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/property-intel/frontend:${GIT_COMMIT}

# Push backend
docker push ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/property-intel/backend:latest
docker push ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/property-intel/backend:${GIT_COMMIT}

# Verify images
aws ecr describe-images \
  --repository-name property-intel/frontend \
  --query 'imageDetails[*].[imageTags[0],imageSizeInBytes,imagePushedAt]' \
  --output table
```

---

## 🚀 ECS Deployment

### Backend Task Definition

Create `backend-task-def.json`:

```json
{
  "family": "property-intel-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::ACCOUNT_ID:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT_ID:role/propertyIntelBackendTaskRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/property-intel/backend:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        { "name": "ENVIRONMENT", "value": "production" },
        { "name": "LOG_LEVEL", "value": "INFO" }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:us-west-2:ACCOUNT_ID:secret:property-intel/prod/database:url::"
        },
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-west-2:ACCOUNT_ID:secret:property-intel/prod/app:secret_key::"
        },
        {
          "name": "CLERK_SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-west-2:ACCOUNT_ID:secret:property-intel/prod/clerk:secret_key::"
        },
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-west-2:ACCOUNT_ID:secret:property-intel/prod/openai:api_key::"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/property-intel-backend",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": [
          "CMD-SHELL",
          "curl -f http://localhost:8000/health || exit 1"
        ],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

### Frontend Task Definition

Create `frontend-task-def.json`:

```json
{
  "family": "property-intel-frontend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::ACCOUNT_ID:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::ACCOUNT_ID:role/propertyIntelFrontendTaskRole",
  "containerDefinitions": [
    {
      "name": "frontend",
      "image": "ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/property-intel/frontend:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 3000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        { "name": "NEXT_PUBLIC_API_URL", "value": "https://api.yourdomain.com" }
      ],
      "secrets": [
        {
          "name": "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-west-2:ACCOUNT_ID:secret:property-intel/prod/clerk:publishable_key::"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/property-intel-frontend",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:3000 || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 40
      }
    }
  ]
}
```

### Register Task Definitions

```bash
# Register backend task definition
aws ecs register-task-definition \
  --cli-input-json file://backend-task-def.json

# Register frontend task definition
aws ecs register-task-definition \
  --cli-input-json file://frontend-task-def.json
```

### Create ECS Services

```bash
# Create backend service
aws ecs create-service \
  --cluster property-intel-prod \
  --service-name backend \
  --task-definition property-intel-backend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-yyyyyyyyyyy],assignPublicIp=DISABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:us-west-2:ACCOUNT_ID:targetgroup/backend-tg/xxx,containerName=backend,containerPort=8000" \
  --health-check-grace-period-seconds 60

# Create frontend service
aws ecs create-service \
  --cluster property-intel-prod \
  --service-name frontend \
  --task-definition property-intel-frontend:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx,subnet-yyy],securityGroups=[sg-yyyyyyyyyyy],assignPublicIp=DISABLED}" \
  --load-balancers "targetGroupArn=arn:aws:elasticloadbalancing:us-west-2:ACCOUNT_ID:targetgroup/frontend-tg/xxx,containerName=frontend,containerPort=3000" \
  --health-check-grace-period-seconds 40
```

---

## 🏥 Health Checks & Monitoring

### Application Load Balancer Health Checks

**Backend Target Group:**

```bash
aws elbv2 modify-target-group \
  --target-group-arn arn:aws:elasticloadbalancing:us-west-2:ACCOUNT_ID:targetgroup/backend-tg/xxx \
  --health-check-enabled \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3
```

**Frontend Target Group:**

```bash
aws elbv2 modify-target-group \
  --target-group-arn arn:aws:elasticloadbalancing:us-west-2:ACCOUNT_ID:targetgroup/frontend-tg/xxx \
  --health-check-enabled \
  --health-check-path / \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3
```

### CloudWatch Alarms

**Create CPU Usage Alarm:**

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name property-intel-backend-high-cpu \
  --alarm-description "Backend CPU usage above 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --dimensions Name=ClusterName,Value=property-intel-prod Name=ServiceName,Value=backend
```

**Create Memory Usage Alarm:**

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name property-intel-backend-high-memory \
  --alarm-description "Backend memory usage above 80%" \
  --metric-name MemoryUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --dimensions Name=ClusterName,Value=property-intel-prod Name=ServiceName,Value=backend
```

### View Logs

```bash
# Backend logs
aws logs tail /ecs/property-intel-backend --follow

# Frontend logs
aws logs tail /ecs/property-intel-frontend --follow

# Filter for errors
aws logs filter-log-events \
  --log-group-name /ecs/property-intel-backend \
  --filter-pattern "\"level\": \"ERROR\"" \
  --start-time $(date -u -d '1 hour ago' +%s)000
```

---

## 🔧 Troubleshooting

### Service Won't Start

**Symptoms:** Tasks start but immediately stop

**Check:**

1. ECS task stopped reason:

   ```bash
   aws ecs describe-tasks \
     --cluster property-intel-prod \
     --tasks TASK_ARN \
     --query 'tasks[0].stoppedReason'
   ```

2. Container logs:
   ```bash
   aws logs get-log-events \
     --log-group-name /ecs/property-intel-backend \
     --log-stream-name ecs/backend/TASK_ID
   ```

**Common Causes:**

- Missing or incorrect environment variables
- Cannot pull image from ECR (check IAM permissions)
- Secrets Manager permissions denied
- Application crash on startup

**Solutions:**

- Verify task execution role has `ecr:GetAuthorizationToken`, `ecr:BatchGetImage`
- Check Secrets Manager ARNs in task definition
- Review application logs for startup errors

### Health Checks Failing

**Symptoms:** Tasks start but ALB marks them unhealthy

**Check:**

1. Container health check:

   ```bash
   docker exec -it CONTAINER_ID curl -f http://localhost:8000/health
   ```

2. Security group rules:
   ```bash
   aws ec2 describe-security-groups --group-ids sg-yyyyyyyyyyy
   ```

**Common Causes:**

- Security group doesn't allow ALB → ECS traffic
- Application not listening on expected port
- Health check endpoint not implemented
- Slow application startup

**Solutions:**

- Verify security group allows ALB SG on container port
- Check `EXPOSE` in Dockerfile matches container port
- Increase `startPeriod` in health check if app takes >60s to start
- Review `/health` endpoint returns 200 status

### Database Connection Errors

**Symptoms:** `Connection refused` or `Network unreachable`

**Check:**

1. RDS endpoint reachable from ECS:

   ```bash
   # From ECS task:
   aws ecs execute-command \
     --cluster property-intel-prod \
     --task TASK_ARN \
     --container backend \
     --interactive \
     --command "/bin/bash"

   # Inside container:
   curl -v telnet://property-intel-prod.xxxxx.rds.amazonaws.com:5432
   ```

2. Security group rules:
   ```bash
   aws ec2 describe-security-groups --group-ids sg-zzzzzzzzzzz
   ```

**Common Causes:**

- RDS security group doesn't allow ECS security group
- Wrong DATABASE_URL (typo in endpoint)
- RDS not in same VPC or accessible subnet
- RDS still initializing

**Solutions:**

- Add inbound rule to RDS SG: Source = ECS SG, Port = 5432
- Verify DATABASE_URL matches RDS endpoint exactly
- Check RDS instance status is "Available"
- Wait 5-10 minutes after RDS creation

### High Response Times

**Symptoms:** Slow API responses, timeout errors

**Check:**

1. ECS task metrics:

   ```bash
   aws cloudwatch get-metric-statistics \
     --namespace AWS/ECS \
     --metric-name CPUUtilization \
     --dimensions Name=ServiceName,Value=backend \
     --start-time $(date -u -d '1 hour ago' --iso-8601=seconds) \
     --end-time $(date -u --iso-8601=seconds) \
     --period 300 \
     --statistics Average,Maximum
   ```

2. RDS Performance Insights:
   - Navigate to RDS → Monitoring → Performance Insights
   - Check top SQL queries
   - Look for lock waits

**Common Causes:**

- Insufficient task CPU/memory
- Too few tasks for load
- Database connection pool exhausted
- Slow external API calls
- Missing database indexes

**Solutions:**

- Scale up: Increase task count or CPU/memory
- Optimize: Add database indexes, cache frequent queries
- Monitor: Enable RDS Enhanced Monitoring
- Profile: Use Application Performance Monitoring (APM) tool

---

## 🔄 Rollback Procedures

### Immediate Rollback (Service Update)

```bash
# Get previous task definition revision
aws ecs describe-services \
  --cluster property-intel-prod \
  --services backend \
  --query 'services[0].deployments[1].taskDefinition'

# Rollback to previous revision
aws ecs update-service \
  --cluster property-intel-prod \
  --service backend \
  --task-definition property-intel-backend:PREVIOUS_REVISION \
  --force-new-deployment
```

### Rollback to Specific Image Tag

```bash
# Update task definition to use previous image
aws ecs register-task-definition \
  --cli-input-json file://backend-task-def.json \
  --container-definitions '[{
    "name": "backend",
    "image": "ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/property-intel/backend:PREVIOUS_COMMIT"
  }]'

# Deploy new task definition
aws ecs update-service \
  --cluster property-intel-prod \
  --service backend \
  --task-definition property-intel-backend:NEW_REVISION
```

### Database Migration Rollback

```bash
# Connect to RDS
psql -h property-intel-prod.xxxxx.rds.amazonaws.com -U admin -d property_intel

# Check current version
SELECT * FROM alembic_version;

# Downgrade one version
alembic downgrade -1

# Or downgrade to specific version
alembic downgrade abc123def456
```

**Important:** Test rollback procedures in staging environment first!

---

## 📊 Deployment Checklist

### Pre-Deployment

- [ ] All tests passing in CI/CD
- [ ] Environment variables verified in Secrets Manager
- [ ] RDS database created and accessible
- [ ] Database migrations tested
- [ ] Docker images built and pushed to ECR
- [ ] Task definitions registered
- [ ] Security groups configured correctly
- [ ] IAM roles have required permissions
- [ ] Clerk production app configured with correct URLs
- [ ] Health check endpoints tested locally

### Deployment

- [ ] Create ECS services with 2+ tasks for HA
- [ ] Monitor task startup in ECS console
- [ ] Check CloudWatch logs for errors
- [ ] Verify all tasks reach "RUNNING" state
- [ ] Confirm health checks passing in target groups
- [ ] Test application through ALB URL
- [ ] Run smoke tests on critical endpoints
- [ ] Monitor metrics for 15-30 minutes

### Post-Deployment

- [ ] Update DNS to point to ALB
- [ ] Test production domain
- [ ] Verify SSL certificate
- [ ] Run full integration test suite
- [ ] Check Sentry for any errors
- [ ] Document deployment (version, timestamp, changes)
- [ ] Notify team of successful deployment
- [ ] Monitor logs and metrics for 24 hours

---

## 📞 Support & Resources

### AWS Documentation

- [ECS Best Practices](https://docs.aws.amazon.com/AmazonECS/latest/bestpracticesguide/)
- [RDS PostgreSQL Guide](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html)
- [Secrets Manager User Guide](https://docs.aws.amazon.com/secretsmanager/latest/userguide/)

### Project Documentation

- [Database Migrations Guide](./DATABASE_MIGRATIONS_GUIDE.md)
- [AWS RDS Setup](./AWS_RDS_SETUP.md)
- [AWS Secrets Manager Setup](./AWS_SECRETS_MANAGER_SETUP.md)
- [Clerk Production Setup](./CLERK_PRODUCTION_SETUP.md)
- [API Keys Verification](./API_KEYS_VERIFICATION.md)

### Getting Help

- **Application Errors:** Check CloudWatch Logs
- **Infrastructure Issues:** Review CloudWatch Metrics & Alarms
- **Database Problems:** Check RDS Performance Insights
- **Deployment Failures:** Review ECS Events and Task Stopped Reasons

---

**Last Updated:** October 17, 2025  
**Version:** 1.0  
**Status:** ✅ Ready for Production Deployment
