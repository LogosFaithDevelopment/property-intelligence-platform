# AWS Secrets Manager Setup Guide

## Overview

AWS Secrets Manager securely stores and manages sensitive credentials (API keys, database passwords, etc.) for production deployments. This guide covers setup, integration with ECS, and best practices.

---

## Table of Contents

1. [Why Secrets Manager?](#why-secrets-manager)
2. [Creating Secrets](#creating-secrets)
3. [IAM Permissions](#iam-permissions)
4. [ECS Integration](#ecs-integration)
5. [Accessing Secrets in Code](#accessing-secrets-in-code)
6. [Cost Estimates](#cost-estimates)
7. [Alternative: AWS Systems Manager Parameter Store](#alternative-parameter-store)

---

## Why Secrets Manager?

### Benefits

- ✅ **Security:** Encrypted at rest (AES-256) and in transit
- ✅ **Rotation:** Automatic secret rotation (optional)
- ✅ **Access Control:** Fine-grained IAM permissions
- ✅ **Audit:** CloudTrail logging of all access
- ✅ **Version Control:** Track secret changes over time
- ✅ **ECS Integration:** Seamless injection into containers

### vs Environment Variables

| Method                    | Security  | Rotation  | Audit | Cost                |
| ------------------------- | --------- | --------- | ----- | ------------------- |
| `.env` files              | ❌ Low    | Manual    | None  | Free                |
| ECS Environment Variables | ⚠️ Medium | Manual    | Basic | Free                |
| Secrets Manager           | ✅ High   | Automatic | Full  | ~$0.40/secret/month |
| Parameter Store           | ✅ High   | Manual    | Full  | Free (Standard)     |

---

## Creating Secrets

### Option 1: AWS Console (Easiest)

#### Step 1: Navigate to Secrets Manager

1. Go to [AWS Secrets Manager Console](https://console.aws.amazon.com/secretsmanager)
2. Select your region (e.g., `us-east-1`)
3. Click **"Store a new secret"**

#### Step 2: Choose Secret Type

**Select:** `Other type of secret` (for JSON)

**Key-Value Pairs:**

Click **"Plaintext"** tab and enter:

```json
{
  "SECRET_KEY": "your-super-secret-production-key",
  "DATABASE_URL": "postgresql://username:password@property-intel-db.abc123.us-east-1.rds.amazonaws.com:5432/property_intel",
  "REDIS_URL": "redis://property-intel-redis.abc123.cache.amazonaws.com:6379",
  "CLERK_SECRET_KEY": "sk_live_XXXXXXXXXXXXXXXXXXXXXXXXXX",
  "CLERK_WEBHOOK_SECRET": "whsec_XXXXXXXXXXXXXXXXXXXXXXXXXX",
  "OPENAI_API_KEY": "sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXX",
  "ATTOM_API_KEY": "XXXXXXXXXXXXXXXXXXXXXXXXXX",
  "SMARTY_AUTH_ID": "XXXXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
  "SMARTY_AUTH_TOKEN": "XXXXXXXXXXXXXXXXXXXX",
  "HUD_API_KEY": "eyJXXXXXXXXXXXXXXXXXXXXXXXXXX...",
  "GOOGLE_MAPS_API_KEY": "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "CENSUS_API_KEY": ""
}
```

**Encryption Key:**

- Select **"aws/secretsmanager"** (default, free)
- Or create a custom KMS key (additional cost)

#### Step 3: Configure Secret

**Secret Name:**

```
property-intel/production/backend-secrets
```

**Naming Convention:**

```
<app-name>/<environment>/<service>-secrets
```

**Description:**

```
Production secrets for Property Intelligence Platform backend
```

**Tags (Optional but Recommended):**

```
Environment: production
Application: property-intel
ManagedBy: terraform  # if using IaC
```

#### Step 4: Configure Rotation (Optional)

**Automatic Rotation:**

- ✅ Enable for `DATABASE_URL` (requires Lambda function)
- ❌ Skip for other secrets (manual rotation fine)

**Rotation Schedule:**

- Every 30 days (default)
- Custom interval as needed

**Note:** We'll skip automatic rotation for now (adds complexity).

#### Step 5: Review and Store

1. Review your secret configuration
2. Click **"Store"**
3. **Copy the Secret ARN** (you'll need this for ECS):
   ```
   arn:aws:secretsmanager:us-east-1:123456789012:secret:property-intel/production/backend-secrets-AbCdEf
   ```

---

### Option 2: AWS CLI (Faster for Multiple Secrets)

#### Install AWS CLI

```bash
# macOS
brew install awscli

# Verify installation
aws --version
```

#### Configure AWS CLI

```bash
aws configure
# AWS Access Key ID: YOUR_ACCESS_KEY
# AWS Secret Access Key: YOUR_SECRET_KEY
# Default region: us-east-1
# Default output format: json
```

#### Create Secret

```bash
aws secretsmanager create-secret \
  --name property-intel/production/backend-secrets \
  --description "Production secrets for Property Intelligence Platform" \
  --secret-string '{
    "SECRET_KEY": "your-secret-key",
    "DATABASE_URL": "postgresql://...",
    "CLERK_SECRET_KEY": "sk_live_...",
    "OPENAI_API_KEY": "sk-proj-...",
    "ATTOM_API_KEY": "...",
    "SMARTY_AUTH_ID": "...",
    "SMARTY_AUTH_TOKEN": "..."
  }' \
  --tags Key=Environment,Value=production Key=Application,Value=property-intel
```

#### Retrieve Secret ARN

```bash
aws secretsmanager describe-secret \
  --secret-id property-intel/production/backend-secrets \
  --query 'ARN' \
  --output text
```

---

## IAM Permissions

### ECS Task Execution Role

Your ECS task needs permission to read secrets. Create or update the **ECS Task Execution Role**.

#### Step 1: Create IAM Policy

**Policy Name:** `PropertyIntelSecretsAccess`

**Policy JSON:**

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
        "arn:aws:secretsmanager:us-east-1:123456789012:secret:property-intel/production/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": ["kms:Decrypt"],
      "Resource": "arn:aws:kms:us-east-1:123456789012:key/*",
      "Condition": {
        "StringEquals": {
          "kms:ViaService": "secretsmanager.us-east-1.amazonaws.com"
        }
      }
    }
  ]
}
```

**Replace:**

- `123456789012` with your AWS Account ID
- `us-east-1` with your region

#### Step 2: Attach Policy to ECS Task Execution Role

**Using AWS Console:**

1. Go to IAM → Roles
2. Find your ECS Task Execution Role (e.g., `ecsTaskExecutionRole`)
3. Click **"Attach policies"**
4. Search for `PropertyIntelSecretsAccess`
5. Click **"Attach policy"**

**Using AWS CLI:**

```bash
# Get your ECS task execution role ARN
aws iam get-role --role-name ecsTaskExecutionRole

# Attach the policy
aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::123456789012:policy/PropertyIntelSecretsAccess
```

---

## ECS Integration

### Method 1: ECS Task Definition (Recommended)

#### Update Task Definition

Add secrets to your ECS task definition:

```json
{
  "family": "property-intel-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/property-intel-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        },
        {
          "name": "DEBUG",
          "value": "false"
        },
        {
          "name": "LOG_LEVEL",
          "value": "INFO"
        }
      ],
      "secrets": [
        {
          "name": "SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:property-intel/production/backend-secrets:SECRET_KEY::"
        },
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:property-intel/production/backend-secrets:DATABASE_URL::"
        },
        {
          "name": "CLERK_SECRET_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:property-intel/production/backend-secrets:CLERK_SECRET_KEY::"
        },
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:property-intel/production/backend-secrets:OPENAI_API_KEY::"
        },
        {
          "name": "ATTOM_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:property-intel/production/backend-secrets:ATTOM_API_KEY::"
        },
        {
          "name": "SMARTY_AUTH_ID",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:property-intel/production/backend-secrets:SMARTY_AUTH_ID::"
        },
        {
          "name": "SMARTY_AUTH_TOKEN",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:123456789012:secret:property-intel/production/backend-secrets:SMARTY_AUTH_TOKEN::"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/property-intel-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

**Secret ARN Format:**

```
arn:aws:secretsmanager:REGION:ACCOUNT_ID:secret:SECRET_NAME:KEY_NAME::
```

**Note the double colon `::` at the end!**

### Method 2: AWS Copilot (Easier)

If using AWS Copilot CLI:

**copilot/backend/manifest.yml:**

```yaml
name: backend
type: Backend Service

image:
  build: ./backend/Dockerfile
  port: 8000

cpu: 512
memory: 1024
count: 2

variables:
  ENVIRONMENT: production
  DEBUG: false
  LOG_LEVEL: INFO

secrets:
  SECRET_KEY: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/SECRET_KEY
  DATABASE_URL: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/DATABASE_URL
  CLERK_SECRET_KEY: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/CLERK_SECRET_KEY
  OPENAI_API_KEY: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/OPENAI_API_KEY
  ATTOM_API_KEY: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/ATTOM_API_KEY
  SMARTY_AUTH_ID: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/SMARTY_AUTH_ID
  SMARTY_AUTH_TOKEN: /copilot/${COPILOT_APPLICATION_NAME}/${COPILOT_ENVIRONMENT_NAME}/secrets/SMARTY_AUTH_TOKEN
```

**Store secrets with Copilot:**

```bash
copilot secret init --name SECRET_KEY
copilot secret init --name DATABASE_URL
copilot secret init --name CLERK_SECRET_KEY
# ... etc for each secret
```

---

## Accessing Secrets in Code

### In ECS (Automatic)

When using ECS task definition with `secrets` section, environment variables are **automatically injected** into the container. Your FastAPI app can read them normally:

```python
# backend/app/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    secret_key: str = Field(..., alias="SECRET_KEY")
    database_url: str = Field(..., alias="DATABASE_URL")
    clerk_secret_key: str = Field(..., alias="CLERK_SECRET_KEY")
    # ... etc
```

**No boto3 code needed!** ECS handles everything.

### Manual Retrieval (If Needed)

If you need to fetch secrets programmatically:

```python
import boto3
import json

def get_secret(secret_name: str, region_name: str = "us-east-1"):
    """Retrieve secret from AWS Secrets Manager"""

    client = boto3.client('secretsmanager', region_name=region_name)

    try:
        response = client.get_secret_value(SecretId=secret_name)

        # Parse JSON secret
        if 'SecretString' in response:
            secret = json.loads(response['SecretString'])
            return secret
        else:
            # Binary secret (less common)
            import base64
            return base64.b64decode(response['SecretBinary'])

    except Exception as e:
        print(f"Error retrieving secret: {e}")
        raise

# Usage
secrets = get_secret("property-intel/production/backend-secrets")
DATABASE_URL = secrets["DATABASE_URL"]
```

**Note:** This requires `boto3` package and IAM permissions.

---

## Cost Estimates

### Secrets Manager Pricing (as of 2025)

**Secret Storage:**

- $0.40 per secret per month
- Prorated for partial months

**API Calls:**

- $0.05 per 10,000 API calls
- First 10,000 calls per month are free

### Cost Calculation for Property Intelligence Platform

**Secrets Needed:**

1. `backend-secrets` (single JSON secret with 10+ keys)

**Monthly Cost:**

```
Storage: $0.40 × 1 secret = $0.40
API Calls: ~10,000 per month (ECS task restarts) = Free
───────────────────────────────
Total: ~$0.40 per month
```

**Annual Cost:** ~$5 per year

**Alternative:** Use AWS Systems Manager Parameter Store (free for standard parameters)

---

## Alternative: Parameter Store

### When to Use Parameter Store

✅ **Use Parameter Store if:**

- Cost-sensitive ($0 for standard parameters)
- Don't need automatic rotation
- OK with manual secret updates

❌ **Use Secrets Manager if:**

- Need automatic rotation
- Want better secret versioning
- Prefer dedicated secret management service

### Creating Parameters

```bash
# Create parameter
aws ssm put-parameter \
  --name /property-intel/production/SECRET_KEY \
  --value "your-secret-key" \
  --type SecureString \
  --tier Standard

# Repeat for each secret
aws ssm put-parameter \
  --name /property-intel/production/DATABASE_URL \
  --value "postgresql://..." \
  --type SecureString
```

### ECS Integration with Parameter Store

Same as Secrets Manager, but use different ARN format:

```json
{
  "secrets": [
    {
      "name": "SECRET_KEY",
      "valueFrom": "arn:aws:ssm:us-east-1:123456789012:parameter/property-intel/production/SECRET_KEY"
    }
  ]
}
```

**Cost:** Free for standard parameters (up to 4KB each)

---

## Security Best Practices

### 1. Least Privilege Access

Only grant ECS tasks access to secrets they need:

```json
{
  "Resource": [
    "arn:aws:secretsmanager:us-east-1:123456789012:secret:property-intel/production/backend-secrets-*"
  ]
}
```

### 2. Enable CloudTrail Logging

Monitor who accesses secrets:

```bash
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=ResourceName,AttributeValue=property-intel/production/backend-secrets \
  --max-items 20
```

### 3. Rotate Secrets Regularly

**Manual Rotation Schedule:**

- `SECRET_KEY`: Every 90 days
- `DATABASE_URL` password: Every 90 days
- API keys: When compromised or annually

### 4. Use Separate Secrets Per Environment

```
property-intel/development/backend-secrets
property-intel/staging/backend-secrets
property-intel/production/backend-secrets
```

### 5. Never Log Secret Values

```python
# ❌ BAD
logger.info(f"Using secret: {SECRET_KEY}")

# ✅ GOOD
logger.info("Secret loaded successfully")
```

---

## Troubleshooting

### Issue: ECS Task Fails to Start

**Error:** `ResourceInitializationError: unable to pull secrets`

**Solution:**

1. Verify ECS Task Execution Role has Secrets Manager permissions
2. Check secret ARN is correct (including double `::` at end)
3. Verify secret exists in the same region as ECS

### Issue: Access Denied

**Error:** `AccessDeniedException: User is not authorized`

**Solution:**

1. Add `secretsmanager:GetSecretValue` to IAM policy
2. Add `kms:Decrypt` for KMS-encrypted secrets
3. Verify resource ARN matches in policy

### Issue: Secret Not Found

**Error:** `ResourceNotFoundException`

**Solution:**

1. Check secret name spelling
2. Verify secret exists in correct region
3. Use AWS Console to confirm secret ARN

---

## Next Steps

After setting up Secrets Manager:

1. ✅ Secrets created and stored in AWS
2. ✅ IAM permissions configured
3. ✅ ECS task definition updated with secret references
4. → Document RDS database setup
5. → Create deployment guide
6. → Test full production deployment

---

## Support Resources

- **AWS Secrets Manager Docs:** https://docs.aws.amazon.com/secretsmanager/
- **ECS Secrets Tutorial:** https://docs.aws.amazon.com/AmazonECS/latest/developerguide/specifying-sensitive-data-secrets.html
- **IAM Best Practices:** https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html
- **AWS Support:** https://console.aws.amazon.com/support/
