# Database Migrations Guide

## Overview

This guide covers Alembic database migrations for the Property Intelligence Platform, including testing procedures, rollback strategies, and production deployment best practices for AWS RDS.

---

## Table of Contents

1. [Migration Architecture](#migration-architecture)
2. [Local Development](#local-development)
3. [Testing Migrations](#testing-migrations)
4. [Production Deployment](#production-deployment)
5. [Rollback Procedures](#rollback-procedures)
6. [Troubleshooting](#troubleshooting)

---

## Migration Architecture

### Migration History

The project uses Alembic for database schema version control with the following migration chain:

```
000000000000 (initial_schema)
    ↓
71dd657881e1 (add_available_build_space_to_assessments)
    ↓
manual_overrides_2025 (add_manual_overrides_tracking)
    ↓
0e265bd5510a (add_assessment_submission_fields)
    ↓
ef2bce464a78 (add_admin_users_table)
    ↓
c273519300a9 (convert_admin_users_to_clerk)
    ↓
a1b2c3d4e5f6 (add_phase2_deal_breaker_fields)
    ↓
b2c3d4e5f6g7 (add_phase3_partnership_fields)
    ↓
d3e4f5g6h7i8 (add_demolish_and_multi_address_support) ← HEAD
```

### Initial Schema (000000000000)

The initial migration creates the base tables:

- `api_cache` - API response caching
- `churches` - Church information
- `properties` - Property data
- `assessments` - Property assessments
- `reports` - Generated reports

**Important**: The initial schema does NOT include fields added by subsequent migrations. Each migration builds upon the previous one.

### Configuration

**alembic.ini:**

- Located at: `backend/alembic.ini`
- Default DATABASE_URL: `postgresql://postgres:postgres@localhost:5432/property_intel`
- Override with environment variable: `DATABASE_URL`

**alembic/env.py:**

- Automatically converts async database URLs (`postgresql+asyncpg://`) to sync (`postgresql+psycopg2://`)
- Loads settings from `app.config`
- Imports all models to ensure SQLAlchemy registers them

---

## Local Development

### Prerequisites

```bash
# Ensure PostgreSQL is running
docker-compose up -d postgres

# Activate virtual environment
cd backend
source venv/bin/activate  # or: . venv/bin/activate

# Install dependencies (if not already)
pip install -r requirements.txt
```

### Check Migration Status

```bash
# View current migration version
alembic current

# View migration history
alembic history

# View all head revisions (should be one)
alembic heads
```

### Creating New Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description_of_changes"

# Create empty migration (manual)
alembic revision -m "description_of_changes"

# Edit the generated file in alembic/versions/
# Review upgrade() and downgrade() functions
```

**Best Practices:**

- ✅ Always review auto-generated migrations before applying
- ✅ Test both `upgrade()` and `downgrade()` functions
- ✅ Use descriptive migration messages
- ✅ Keep migrations small and focused
- ✅ Never edit applied migrations (create new ones instead)

### Applying Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific number of migrations
alembic upgrade +2

# Apply to specific revision
alembic upgrade 71dd657881e1
```

### Rolling Back Migrations

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade 71dd657881e1

# Rollback all migrations
alembic downgrade base
```

---

## Testing Migrations

### Comprehensive Migration Test

We've created a test script that validates the entire migration chain:

**Location:** `backend/scripts/testing/test_migrations.sh`

**Usage:**

```bash
cd backend
./scripts/testing/test_migrations.sh
```

**What it tests:**

1. Database connection
2. Creates clean test database (`property_intel_test`)
3. Runs all migrations from scratch (`alembic upgrade head`)
4. Verifies migration status
5. Tests rollback (`alembic downgrade -1`)
6. Tests re-upgrade (`alembic upgrade head`)
7. Lists all created tables

### Manual Testing

```bash
# 1. Create clean test database
PGPASSWORD=postgres psql -h localhost -p 5432 -U postgres << EOF
DROP DATABASE IF EXISTS property_intel_test;
CREATE DATABASE property_intel_test;
EOF

# 2. Run migrations
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/property_intel_test"
alembic upgrade head

# 3. Verify tables
PGPASSWORD=postgres psql -h localhost -p 5432 -U postgres -d property_intel_test -c "\dt"

# 4. Test rollback
alembic downgrade -1
alembic current  # Should show previous version

# 5. Re-upgrade
alembic upgrade head
alembic current  # Should show head

# 6. Clean up (optional)
PGPASSWORD=postgres psql -h localhost -p 5432 -U postgres -c "DROP DATABASE property_intel_test;"
```

### Testing Checklist

Before deploying to production:

- [ ] All migrations run successfully on clean database
- [ ] Rollback tested for last 3 migrations
- [ ] Re-upgrade works after rollback
- [ ] All expected tables created
- [ ] Foreign key constraints work
- [ ] Indexes created correctly
- [ ] No duplicate constraints or indexes
- [ ] Data types match models

---

## Production Deployment

### Pre-Deployment Checklist

**1. Backup Production Database**

```bash
# RDS snapshot (via AWS Console or CLI)
aws rds create-db-snapshot \
  --db-instance-identifier property-intel-db-production \
  --db-snapshot-identifier pre-migration-$(date +%Y%m%d-%H%M%S)
```

**2. Test Migrations on Staging**

```bash
# Run migrations on staging database first
export DATABASE_URL="postgresql://USER:PASS@staging-db.rds.amazonaws.com:5432/property_intel"
alembic upgrade head
```

**3. Schedule Maintenance Window**

- Notify users of potential downtime
- Choose low-traffic time (e.g., 2 AM - 4 AM)
- Estimate migration duration (test locally first)

### Deployment Methods

#### Method 1: Direct from ECS Task (Recommended)

**Step 1: Create migration task definition**

```json
{
  "family": "property-intel-migration",
  "taskRoleArn": "arn:aws:iam::ACCOUNT:role/PropertyIntelTaskRole",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/PropertyIntelExecutionRole",
  "networkMode": "awsvpc",
  "cpu": "256",
  "memory": "512",
  "requiresCompatibilities": ["FARGATE"],
  "containerDefinitions": [
    {
      "name": "migration",
      "image": "ACCOUNT.dkr.ecr.REGION.amazonaws.com/property-intel-backend:latest",
      "command": ["alembic", "upgrade", "head"],
      "environment": [],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:REGION:ACCOUNT:secret:property-intel/production/backend-secrets:DATABASE_URL::"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/property-intel-migration",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "migration"
        }
      }
    }
  ]
}
```

**Step 2: Run migration task**

```bash
aws ecs run-task \
  --cluster property-intel-cluster \
  --task-definition property-intel-migration \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx]}"
```

**Step 3: Monitor logs**

```bash
aws logs tail /ecs/property-intel-migration --follow
```

#### Method 2: AWS Copilot Job

**Create migration job:**

```bash
# copilot/jobs/migrate/manifest.yml
name: migrate
type: Scheduled Job

on:
  schedule: none  # Manual trigger only

image:
  build: backend/Dockerfile

cpu: 256
memory: 512

command: ["alembic", "upgrade", "head"]

secrets:
  DATABASE_URL: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/DATABASE_URL
```

**Run migration:**

```bash
copilot job run --name migrate --env production
```

#### Method 3: Local Connection to RDS (Emergency Only)

**⚠️ Only use if ECS methods fail**

```bash
# 1. Enable temporary public access or SSH tunnel
aws rds modify-db-instance \
  --db-instance-identifier property-intel-db-production \
  --publicly-accessible \
  --apply-immediately

# 2. Add your IP to security group
aws ec2 authorize-security-group-ingress \
  --group-id sg-xxx \
  --protocol tcp \
  --port 5432 \
  --cidr YOUR_IP/32

# 3. Run migrations
export DATABASE_URL="postgresql://USER:PASS@property-intel-db.rds.amazonaws.com:5432/property_intel"
alembic upgrade head

# 4. Remove public access
aws rds modify-db-instance \
  --db-instance-identifier property-intel-db-production \
  --no-publicly-accessible \
  --apply-immediately
```

### Post-Deployment Verification

```bash
# 1. Verify migration version
alembic current

# 2. Check application health
curl https://api.property-intel.example.com/health/db

# 3. Test database queries
# Run smoke tests on critical endpoints

# 4. Monitor CloudWatch logs for errors
aws logs tail /ecs/property-intel-backend --follow --since 5m

# 5. Check RDS metrics
# CPU, connections, disk space, IOPS
```

---

## Rollback Procedures

### When to Rollback

Rollback if you encounter:

- Migration errors during deployment
- Data corruption or inconsistencies
- Application errors after migration
- Performance degradation
- Failed foreign key constraints

### Rollback Strategy

**Option 1: Rollback Migration (Preferred)**

```bash
# Rollback to previous version
alembic downgrade -1

# Verify version
alembic current

# Restart application
aws ecs update-service \
  --cluster property-intel-cluster \
  --service backend \
  --force-new-deployment
```

**Option 2: Restore from Snapshot**

```bash
# 1. Stop application
aws ecs update-service \
  --cluster property-intel-cluster \
  --service backend \
  --desired-count 0

# 2. Restore RDS snapshot
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier property-intel-db-production-restored \
  --db-snapshot-identifier pre-migration-TIMESTAMP

# 3. Update DNS/endpoint to point to restored instance

# 4. Restart application with restored database
```

**Option 3: Point-in-Time Recovery**

```bash
# Restore to specific time before migration
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier property-intel-db-production \
  --target-db-instance-identifier property-intel-db-production-pitr \
  --restore-time 2025-10-16T01:30:00Z
```

### Rollback Testing

**Before deploying to production, test rollback:**

```bash
# 1. Apply migration
alembic upgrade head

# 2. Add test data
# Insert sample records

# 3. Rollback
alembic downgrade -1

# 4. Verify data integrity
# Ensure no data loss (if migration doesn't affect existing data)

# 5. Re-upgrade
alembic upgrade head
```

---

## Troubleshooting

### Common Issues

#### 1. Multiple Head Revisions

**Error:** `Multiple head revisions are present`

**Cause:** Branch in migration history (two migrations with same parent)

**Solution:**

```bash
# Find all heads
alembic heads

# Merge branches (if both should be applied)
alembic merge -m "merge_branches" HEAD1 HEAD2

# Or delete duplicate migration file
rm alembic/versions/DUPLICATE_FILE.py
```

#### 2. Migration Dependency Errors

**Error:** `Can't locate revision identified by 'XXXXX'`

**Cause:** Missing migration file or incorrect `down_revision`

**Solution:**

```bash
# Check all migrations exist
ls alembic/versions/

# Verify migration chain
alembic history

# Fix down_revision in migration file if needed
```

#### 3. Database Connection Errors

**Error:** `could not connect to server`

**Cause:** Database not running or connection string incorrect

**Solution:**

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Verify DATABASE_URL
echo $DATABASE_URL

# Test connection
psql $DATABASE_URL -c "SELECT 1;"
```

#### 4. Schema Conflicts

**Error:** `relation "table_name" already exists`

**Cause:** Table already exists in database

**Solution:**

```bash
# Check current version
alembic current

# Stamp database with correct version (CAREFUL!)
alembic stamp head

# Or drop and recreate database (development only)
```

#### 5. Foreign Key Violations

**Error:** `violates foreign key constraint`

**Cause:** Migration adds foreign key to existing data that doesn't match

**Solution:**

- Fix data before applying migration
- Or make foreign key nullable initially
- Or use data migration to clean up first

### Migration Best Practices

**Do:**

- ✅ Test migrations on clean database before production
- ✅ Backup database before applying migrations
- ✅ Keep migrations small and atomic
- ✅ Add both `upgrade()` and `downgrade()` functions
- ✅ Use transactions (Alembic does this by default)
- ✅ Test rollback procedures

**Don't:**

- ❌ Edit applied migrations (create new ones)
- ❌ Delete migration files from history
- ❌ Apply untested migrations to production
- ❌ Skip testing rollback
- ❌ Run migrations manually on production (use automation)
- ❌ Forget to backup before migrations

### Getting Help

**Check Alembic logs:**

```bash
# Enable verbose logging
alembic -v upgrade head
```

**Check database state:**

```bash
# View alembic_version table
psql $DATABASE_URL -c "SELECT * FROM alembic_version;"

# List all tables
psql $DATABASE_URL -c "\dt"

# Check table structure
psql $DATABASE_URL -c "\d table_name"
```

**Resources:**

- Alembic Documentation: https://alembic.sqlalchemy.org/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- PostgreSQL Documentation: https://www.postgresql.org/docs/

---

## Summary

### Quick Reference

```bash
# Development
alembic current                    # Check current version
alembic history                    # View migration history
alembic upgrade head               # Apply all migrations
alembic downgrade -1               # Rollback one migration

# Testing
./scripts/testing/test_migrations.sh

# Production (via ECS task)
aws ecs run-task --task-definition property-intel-migration ...

# Emergency rollback
alembic downgrade -1
aws ecs update-service --force-new-deployment
```

### Migration Checklist

**Pre-Production:**

- [ ] Migrations tested on clean local database
- [ ] Rollback tested for recent migrations
- [ ] Staging environment updated successfully
- [ ] Database backup created
- [ ] Maintenance window scheduled

**Production:**

- [ ] Application scaled down (optional, for large migrations)
- [ ] Migration task deployed via ECS
- [ ] Migration logs monitored
- [ ] Application health checks passing
- [ ] Database metrics normal

**Post-Production:**

- [ ] Migration version verified
- [ ] Application functionality tested
- [ ] Rollback procedure documented (if needed)
- [ ] Team notified of completion

---

## Next Steps

- **Phase 7:** Code cleanup (console.logs, ESLint fixes)
- **Phase 8:** Production deployment documentation (README.prod.md)
- **Future:** Set up automated migration testing in CI/CD pipeline
