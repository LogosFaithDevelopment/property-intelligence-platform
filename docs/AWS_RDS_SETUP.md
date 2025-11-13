# AWS RDS PostgreSQL Setup Guide

## Overview

This guide covers setting up AWS RDS PostgreSQL for production use with the Property Intelligence Platform. We'll configure a cost-effective `db.t4g.micro` instance suitable for early production workloads.

---

## Table of Contents

1. [Instance Specifications](#instance-specifications)
2. [Creating RDS Instance](#creating-rds-instance)
3. [Security Configuration](#security-configuration)
4. [Connection String Format](#connection-string-format)
5. [Backup and Maintenance](#backup-and-maintenance)
6. [Cost Estimates](#cost-estimates)
7. [Monitoring and Alerts](#monitoring-and-alerts)
8. [Scaling Strategy](#scaling-strategy)

---

## Instance Specifications

### Recommended Configuration

**Instance Class:**

```
db.t4g.micro (2 vCPU, 1 GB RAM)
```

**Why db.t4g.micro?**

- ✅ ARM-based Graviton2 (20-40% cheaper than Intel)
- ✅ Burstable performance (good for variable workloads)
- ✅ Sufficient for 100-500 concurrent users
- ✅ ~$17-22/month (cheapest production option)

**Storage:**

```
Type: General Purpose SSD (gp3)
Size: 20 GB (minimum)
IOPS: 3000 (default)
Throughput: 125 MB/s (default)
```

**Engine:**

```
Engine: PostgreSQL
Version: 16.1 (latest stable)
```

**Deployment:**

```
Multi-AZ: No (single instance for cost savings)
Read Replicas: None initially
```

### Alternative Configurations

| Use Case            | Instance                | Storage | Monthly Cost |
| ------------------- | ----------------------- | ------- | ------------ |
| Development/Testing | db.t4g.micro            | 20 GB   | ~$17         |
| Early Production    | db.t4g.micro            | 20 GB   | ~$20         |
| Growing Production  | db.t4g.small            | 50 GB   | ~$45         |
| High Availability   | db.t4g.small (Multi-AZ) | 100 GB  | ~$110        |
| High Performance    | db.r6g.large            | 200 GB  | ~$280        |

**Recommendation:** Start with `db.t4g.micro`, scale up as needed.

---

## Creating RDS Instance

### Option 1: AWS Console (Step-by-Step)

#### Step 1: Navigate to RDS

1. Go to [AWS RDS Console](https://console.aws.amazon.com/rds)
2. Select your region (e.g., `us-east-1`)
3. Click **"Create database"**

#### Step 2: Database Creation Method

**Choose:** Standard create

#### Step 3: Engine Options

```
Engine type: PostgreSQL
Edition: PostgreSQL
Engine Version: PostgreSQL 16.1-R3 (or latest)
```

#### Step 4: Templates

**Choose:** Free tier (if eligible) **OR** Production

**Note:** Free tier gives 750 hours/month of `db.t3.micro` (limited to 12 months)

#### Step 5: Settings

**DB Instance Identifier:**

```
property-intel-db-production
```

**Master Username:**

```
postgres  (default, or choose custom)
```

**Master Password:**

```
Generate secure password (use AWS Secrets Manager)
```

**Password Requirements:**

- At least 8 characters
- Include uppercase, lowercase, numbers, special characters
- Store in AWS Secrets Manager immediately

#### Step 6: Instance Configuration

**DB Instance Class:**

```
Burstable classes (includes t classes)
db.t4g.micro (2 vCPU, 1 GiB RAM)
```

**Storage:**

```
Storage type: General Purpose SSD (gp3)
Allocated storage: 20 GiB
Storage autoscaling: Enabled
Maximum storage threshold: 100 GiB
```

#### Step 7: Connectivity

**Compute Resource:**

```
Don't connect to an EC2 compute resource
```

**Network Type:**

```
IPv4
```

**Virtual Private Cloud (VPC):**

```
Create new VPC  OR  Select existing VPC
```

**DB Subnet Group:**

```
Create new DB subnet group
```

**Public Access:**

```
No (for security)
```

**VPC Security Group:**

```
Create new security group
Name: property-intel-db-sg
```

**Availability Zone:**

```
No preference  (let AWS choose)
```

**Database Port:**

```
5432 (PostgreSQL default)
```

#### Step 8: Database Authentication

**Choose:** Password authentication

**Optionally Enable:**

- IAM database authentication (for passwordless access)

#### Step 9: Monitoring

```
✅ Enable Enhanced Monitoring
Granularity: 60 seconds
Monitoring Role: Create new role
```

```
✅ Enable Performance Insights
Retention period: 7 days (free tier)
```

#### Step 10: Additional Configuration

**Database Options:**

```
Initial database name: property_intel
```

**DB Parameter Group:**

```
default.postgres16 (or create custom)
```

**Option Group:**

```
default:postgres-16
```

**Backup:**

```
✅ Enable automated backups
Backup retention period: 7 days
Backup window: No preference (let AWS choose off-peak)
✅ Copy tags to snapshots
```

**Encryption:**

```
✅ Enable encryption
AWS KMS key: (default) aws/rds
```

**Performance Insights:**

```
✅ Enable Performance Insights
Retention: 7 days (free)
```

**Monitoring:**

```
✅ Enable Enhanced Monitoring
Granularity: 60 seconds
```

**Log Exports:**

```
✅ PostgreSQL log
✅ Upgrade log
```

**Maintenance:**

```
✅ Enable auto minor version upgrade
Maintenance window: No preference
```

**Deletion Protection:**

```
✅ Enable deletion protection (recommended)
```

#### Step 11: Review and Create

1. Review all settings
2. Click **"Create database"**
3. Wait 5-10 minutes for instance to become available

#### Step 12: Retrieve Connection Details

Once status is **"Available"**:

1. Click on your DB instance
2. Go to **"Connectivity & security"** tab
3. Copy the **Endpoint** (e.g., `property-intel-db-production.abc123.us-east-1.rds.amazonaws.com`)
4. Note the **Port** (5432)

---

### Option 2: AWS CLI (Faster)

```bash
# Create RDS instance
aws rds create-db-instance \
  --db-instance-identifier property-intel-db-production \
  --db-instance-class db.t4g.micro \
  --engine postgres \
  --engine-version 16.1 \
  --master-username postgres \
  --master-user-password 'YourSecurePassword123!' \
  --allocated-storage 20 \
  --storage-type gp3 \
  --storage-encrypted \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00" \
  --preferred-maintenance-window "mon:04:00-mon:05:00" \
  --vpc-security-group-ids sg-0123456789abcdef0 \
  --db-subnet-group-name property-intel-db-subnet-group \
  --db-name property_intel \
  --enable-cloudwatch-logs-exports '["postgresql","upgrade"]' \
  --enable-performance-insights \
  --performance-insights-retention-period 7 \
  --deletion-protection \
  --tags Key=Environment,Value=production Key=Application,Value=property-intel

# Wait for instance to be available
aws rds wait db-instance-available \
  --db-instance-identifier property-intel-db-production

# Get connection endpoint
aws rds describe-db-instances \
  --db-instance-identifier property-intel-db-production \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text
```

---

## Security Configuration

### 1. Security Group Configuration

**Allow Inbound Traffic Only From ECS:**

```bash
# Get your ECS security group ID
ECS_SG_ID="sg-xxxxxxxxxxxxxxxxx"

# Get your RDS security group ID
RDS_SG_ID="sg-yyyyyyyyyyyyyyyyy"

# Allow PostgreSQL traffic from ECS to RDS
aws ec2 authorize-security-group-ingress \
  --group-id $RDS_SG_ID \
  --protocol tcp \
  --port 5432 \
  --source-group $ECS_SG_ID
```

**Security Group Rules:**

| Type       | Protocol | Port | Source             | Description     |
| ---------- | -------- | ---- | ------------------ | --------------- |
| PostgreSQL | TCP      | 5432 | ECS Security Group | Allow ECS tasks |

**❌ DO NOT:**

- Allow `0.0.0.0/0` (public internet access)
- Allow your home IP (use bastion host or VPN instead)

### 2. Subnet Configuration

**Use Private Subnets:**

- Place RDS in private subnets (no internet gateway)
- ECS tasks can access via VPC internal routing
- Use NAT Gateway for ECS tasks to access internet

**DB Subnet Group:**

```
Subnets: At least 2 private subnets in different AZs
```

### 3. IAM Authentication (Optional)

Enable IAM database authentication for passwordless access:

```sql
-- Create IAM user in PostgreSQL
CREATE USER iam_user;
GRANT rds_iam TO iam_user;
GRANT CONNECT ON DATABASE property_intel TO iam_user;
```

### 4. SSL/TLS Encryption

**Force SSL Connections:**

```sql
-- Connect as superuser and modify parameter group
ALTER SYSTEM SET ssl = on;
```

**In Application (FastAPI):**

```python
# backend/app/database.py
DATABASE_URL = f"{settings.database_url}?sslmode=require"
```

---

## Connection String Format

### Standard Connection String

```
postgresql://USERNAME:PASSWORD@ENDPOINT:PORT/DATABASE
```

### Example

```
postgresql://postgres:SecurePassword123@property-intel-db-production.abc123.us-east-1.rds.amazonaws.com:5432/property_intel
```

### With SSL (Recommended)

```
postgresql://postgres:SecurePassword123@property-intel-db-production.abc123.us-east-1.rds.amazonaws.com:5432/property_intel?sslmode=require
```

### Environment Variable

```bash
DATABASE_URL=postgresql://postgres:SecurePassword123@property-intel-db-production.abc123.us-east-1.rds.amazonaws.com:5432/property_intel?sslmode=require
```

### In AWS Secrets Manager

```json
{
  "DATABASE_URL": "postgresql://postgres:SecurePassword123@property-intel-db-production.abc123.us-east-1.rds.amazonaws.com:5432/property_intel?sslmode=require"
}
```

---

## Backup and Maintenance

### Automated Backups

**Backup Configuration:**

```
Retention Period: 7 days (free)
Backup Window: 03:00-04:00 UTC (automatic, off-peak)
```

**What's Backed Up:**

- Entire database instance
- Transaction logs
- DB snapshots

**Backup Storage:**

- Free up to 100% of allocated storage
- Additional storage: $0.095/GB-month

### Manual Snapshots

**Create Snapshot:**

```bash
aws rds create-db-snapshot \
  --db-instance-identifier property-intel-db-production \
  --db-snapshot-identifier property-intel-db-snapshot-$(date +%Y%m%d-%H%M%S)
```

**Restore from Snapshot:**

```bash
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier property-intel-db-restored \
  --db-snapshot-identifier property-intel-db-snapshot-20250116-120000
```

### Maintenance Windows

**Preferred Maintenance Window:**

```
Monday 04:00-05:00 UTC (automatic updates)
```

**What Happens During Maintenance:**

- Minor version upgrades
- Security patches
- ~1-2 minutes of downtime

**How to Update:**

```bash
aws rds modify-db-instance \
  --db-instance-identifier property-intel-db-production \
  --preferred-maintenance-window mon:04:00-mon:05:00 \
  --apply-immediately
```

---

## Cost Estimates

### Monthly Cost Breakdown

**RDS Instance:**

```
db.t4g.micro (On-Demand): $0.017/hour
720 hours/month × $0.017 = $12.24/month
```

**Storage:**

```
20 GB gp3 SSD: $0.115/GB-month
20 GB × $0.115 = $2.30/month
```

**Backup Storage:**

```
7-day retention (20 GB): Free (up to DB size)
```

**Data Transfer:**

```
Within same AZ (ECS → RDS): Free
Internet egress: $0.09/GB (minimal for DB)
```

**Total Monthly Cost:**

```
Instance:      $12.24
Storage:       $ 2.30
Backups:       $ 0.00 (within free tier)
Data Transfer: $ 1.00 (estimated)
───────────────────────
Total:         ~$15.54/month
```

**Annual Cost:** ~$186/year

### Cost Optimization Tips

1. **Use Reserved Instances** (1-year commitment):

   - Save 30-40%
   - db.t4g.micro: ~$8-9/month (vs $12)

2. **Use Graviton2 (ARM)** instead of Intel:

   - db.t4g.micro vs db.t3.micro
   - 20-40% cheaper for same performance

3. **Right-Size Storage:**

   - Start with 20 GB
   - Enable auto-scaling
   - Monitor usage monthly

4. **Optimize Backup Retention:**
   - 7 days is free
   - Longer retention adds cost

### Scaling Costs

| Instance      | vCPU | RAM   | Storage | Monthly Cost |
| ------------- | ---- | ----- | ------- | ------------ |
| db.t4g.micro  | 2    | 1 GB  | 20 GB   | ~$15         |
| db.t4g.small  | 2    | 2 GB  | 50 GB   | ~$45         |
| db.t4g.medium | 2    | 4 GB  | 100 GB  | ~$90         |
| db.t4g.large  | 2    | 8 GB  | 200 GB  | ~$180        |
| db.r6g.large  | 2    | 16 GB | 500 GB  | ~$280        |

---

## Monitoring and Alerts

### CloudWatch Metrics

**Key Metrics to Monitor:**

- `CPUUtilization` - Should stay < 80%
- `FreeableMemory` - Should stay > 100 MB
- `DatabaseConnections` - Track concurrent connections
- `ReadIOPS` / `WriteIOPS` - Monitor disk I/O
- `FreeStorageSpace` - Alert when < 2 GB

### Create CloudWatch Alarms

**High CPU Alert:**

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name rds-high-cpu \
  --alarm-description "RDS CPU > 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/RDS \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=DBInstanceIdentifier,Value=property-intel-db-production \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:rds-alerts
```

**Low Storage Alert:**

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name rds-low-storage \
  --alarm-description "RDS Storage < 2GB" \
  --metric-name FreeStorageSpace \
  --namespace AWS/RDS \
  --statistic Average \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 2147483648 \
  --comparison-operator LessThanThreshold \
  --dimensions Name=DBInstanceIdentifier,Value=property-intel-db-production \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:rds-alerts
```

### Performance Insights

**Enable Performance Insights:**

- Free for 7 days retention
- Detailed query performance metrics
- Identify slow queries and bottlenecks

**Access Performance Insights:**

1. RDS Console → Select DB instance
2. Click "Performance Insights" tab
3. View top SQL queries, waits, and load

---

## Scaling Strategy

### When to Scale Up

**Scale Instance (Vertical):**

- ⚠️ CPU consistently > 80%
- ⚠️ Freeable memory < 100 MB
- ⚠️ Slow query performance

**Scale Storage (Increase Size):**

- ⚠️ Free storage < 10%
- ⚠️ Rapid data growth
- Enable storage autoscaling (recommended)

**Add Read Replica (Horizontal):**

- ⚠️ High read load (read/write ratio > 5:1)
- ⚠️ Analytical queries slowing down app
- ⚠️ Need geographic distribution

### Scaling Process

**Vertical Scaling (Change Instance Class):**

```bash
aws rds modify-db-instance \
  --db-instance-identifier property-intel-db-production \
  --db-instance-class db.t4g.small \
  --apply-immediately
```

**Downtime:** ~5-10 minutes

**Storage Scaling (Increase Size):**

```bash
aws rds modify-db-instance \
  --db-instance-identifier property-intel-db-production \
  --allocated-storage 50 \
  --apply-immediately
```

**Downtime:** None (online operation)

**Multi-AZ (High Availability):**

```bash
aws rds modify-db-instance \
  --db-instance-identifier property-intel-db-production \
  --multi-az \
  --apply-immediately
```

**Downtime:** None (adds standby replica)

---

## Migration from Docker PostgreSQL

### Step 1: Export Data

```bash
# From development Docker container
docker exec property_intel-db-1 pg_dump -U postgres property_intel > backup.sql
```

### Step 2: Create RDS Database

```bash
# Connect to RDS
psql "postgresql://postgres:password@rds-endpoint.rds.amazonaws.com:5432/postgres"

# Create database
CREATE DATABASE property_intel;
```

### Step 3: Import Data

```bash
# Import to RDS
psql "postgresql://postgres:password@rds-endpoint.rds.amazonaws.com:5432/property_intel" < backup.sql
```

### Step 4: Update Connection String

Update `DATABASE_URL` in AWS Secrets Manager to point to RDS.

### Step 5: Test Connection

```bash
# From ECS task or EC2 instance
psql "postgresql://postgres:password@rds-endpoint.rds.amazonaws.com:5432/property_intel" -c "SELECT 1;"
```

---

## Troubleshooting

### Issue: Cannot Connect to RDS

**Error:** `could not connect to server`

**Solutions:**

1. Check security group allows traffic from ECS
2. Verify RDS is in same VPC as ECS
3. Confirm RDS status is "Available"
4. Test connectivity from ECS task:
   ```bash
   nc -zv rds-endpoint 5432
   ```

### Issue: Authentication Failed

**Error:** `password authentication failed`

**Solutions:**

1. Verify username/password correct
2. Check DATABASE_URL format
3. Confirm user exists:
   ```sql
   SELECT * FROM pg_user;
   ```

### Issue: SSL Required

**Error:** `SSL connection is required`

**Solution:**
Add `?sslmode=require` to connection string:

```
postgresql://...?sslmode=require
```

---

## Next Steps

After RDS setup:

1. ✅ RDS instance created and available
2. ✅ Security groups configured
3. ✅ Connection string stored in Secrets Manager
4. ✅ Backups configured
5. → Test Alembic migrations (Phase 6)
6. → Update ECS task definition with RDS connection
7. → Deploy to production

---

## Support Resources

- **AWS RDS Docs:** https://docs.aws.amazon.com/rds/
- **PostgreSQL on RDS:** https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html
- **RDS Best Practices:** https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_BestPractices.html
- **AWS Support:** https://console.aws.amazon.com/support/
