# Production Database Changes Guide

## Overview

This guide explains the workflow for adding new fields/columns to the production database. Since our production database is managed manually (not through automatic migrations), we follow a specific process to ensure safety and consistency.

---

## Philosophy

- **Production is the source of truth** - Production schema is correct; dev should match it
- **Manual migrations in production** - Never run automatic migrations on production
- **Test locally first** - Always test changes in local Docker environment before production
- **Direct SQL for production** - Apply changes via direct SQL commands for control and safety

---

## Workflow for Adding New Fields

### Step 1: Add Fields to the Code

#### 1.1 Update the Model (`backend/app/models/assessment.py`)

```python
from sqlalchemy import Column, String, JSON

class Assessment(Base):
    __tablename__ = "assessments"

    # ... existing columns ...

    # Add your new fields
    property_improvement_needs = Column(JSON, nullable=True)
    capital_financing_need = Column(String(100), nullable=True)
```

#### 1.2 Update the Schema (`backend/app/schemas/submission.py`)

```python
from pydantic import BaseModel, Field
from typing import Optional, List

class SubmissionCreate(BaseModel):
    # ... existing fields ...

    # Add your new fields
    property_improvement_needs: Optional[List[str]] = Field(default=None)
    capital_financing_need: Optional[str] = Field(default=None)
```

#### 1.3 Update the Frontend Form

Add the form inputs to the appropriate section:

- File: `frontend/src/components/forms/sections/section-2-property-details.tsx`
- Add the new form fields with proper validation

#### 1.4 Update Admin Display (if needed)

If you want to show the new fields in the admin portal:

- File: `frontend/src/app/admin/submissions/[id]/page.tsx`
- Add display cards for the new fields

---

### Step 2: Test Locally

#### 2.1 Create a Migration (for local dev)

```bash
cd backend
docker-compose exec backend alembic revision -m "add_your_field_name"
```

Edit the generated migration file to add your columns:

```python
def upgrade() -> None:
    op.add_column('assessments', sa.Column('property_improvement_needs', sa.JSON(), nullable=True))
    op.add_column('assessments', sa.Column('capital_financing_need', sa.String(100), nullable=True))

def downgrade() -> None:
    op.drop_column('assessments', 'capital_financing_need')
    op.drop_column('assessments', 'property_improvement_needs')
```

#### 2.2 Run Migration Locally

```bash
# Apply the migration to your local database
docker-compose exec backend alembic upgrade head
```

#### 2.3 Test the Changes

1. Start Docker: `docker-compose up`
2. Open the application in your browser
3. Fill out the form with the new fields
4. Submit the form
5. Check that data is saved correctly in local database
6. Generate a PDF report to ensure new fields display properly

---

### Step 3: Apply Changes to Production Database

**⚠️ IMPORTANT: Always backup production data before making schema changes!**

#### 3.1 Review the SQL

Generate the SQL that will be run (don't execute yet):

```bash
cd backend
alembic upgrade head --sql > migration.sql
cat migration.sql  # Review what will be executed
```

#### 3.2 Connect to Production Database

```bash
psql 'postgresql://dbadmin:PASSWORD@property-intel-prod.c0b86a8gscnf.us-east-1.rds.amazonaws.com:5432/property_assessment_prod?sslmode=require'
```

#### 3.3 Run the ALTER TABLE Commands

Execute the column additions manually:

```sql
-- Add new columns (IF NOT EXISTS prevents errors if column already exists)
ALTER TABLE assessments
ADD COLUMN IF NOT EXISTS property_improvement_needs JSON;

ALTER TABLE assessments
ADD COLUMN IF NOT EXISTS capital_financing_need VARCHAR(100);

-- Verify the columns were added
\d assessments
```

#### 3.4 Verify the Changes

```sql
-- Check the table structure
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'assessments'
AND column_name IN ('property_improvement_needs', 'capital_financing_need');
```

---

### Step 4: Deploy the Application

#### 4.1 Ensure Dockerfile is Configured Correctly

The Dockerfile should NOT run automatic migrations:

```dockerfile
# backend/Dockerfile
# NOTE: Migrations are run manually in production for safety and control
CMD ["sh", "-c", "gunicorn app.main:app --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} ..."]
```

**NOT this:**

```dockerfile
CMD ["sh", "-c", "alembic upgrade head && gunicorn ..."]  # ❌ Don't do this
```

#### 4.2 Deploy Backend

```bash
copilot svc deploy --name backend --env production
```

Wait for deployment to complete successfully.

#### 4.3 Deploy Frontend (if you made frontend changes)

```bash
copilot svc deploy --name frontend --env production
```

---

### Step 5: Verify in Production

1. **Test the form submission:**

   - Go to your production site
   - Fill out a new submission with the new fields
   - Submit the form
   - Check that data saves correctly

2. **Check the admin portal:**

   - View the submission in the admin portal
   - Verify new fields display correctly

3. **Test PDF generation:**

   - Download a PDF report
   - Verify new fields appear in the report (if applicable)

4. **Check existing data:**
   - Verify old submissions still work
   - Ensure new nullable columns don't break existing records

---

## Troubleshooting

### Issue: "column already exists" error

**Cause:** You tried to add a column that already exists in production.

**Solution:** Use `IF NOT EXISTS` in your ALTER TABLE statement:

```sql
ALTER TABLE assessments ADD COLUMN IF NOT EXISTS field_name VARCHAR(100);
```

### Issue: Deployment fails with migration errors

**Cause:** Automatic migrations are enabled in Dockerfile.

**Solution:**

1. Check that Dockerfile does NOT have `alembic upgrade head` in the CMD
2. Redeploy with migrations disabled
3. Run migrations manually via direct SQL

### Issue: Local database out of sync with production

**Cause:** Production has fields that local doesn't, or vice versa.

**Solution:**

1. Connect to production and export schema: `pg_dump --schema-only`
2. Compare with local schema
3. Manually sync the differences or rebuild local database

### Issue: Old submissions break after adding new fields

**Cause:** New fields are NOT NULL but old records don't have values.

**Solution:** Always make new columns nullable:

```python
new_field = Column(String(100), nullable=True)  # ✅ Good
new_field = Column(String(100), nullable=False)  # ❌ Bad - will break old records
```

---

## Best Practices

### ✅ DO:

- Always use `nullable=True` for new columns unless absolutely necessary
- Test changes locally in Docker before applying to production
- Use `IF NOT EXISTS` when adding columns to production
- Keep production and dev schemas documented
- Backup production database before major changes
- Review SQL before executing on production
- Use descriptive migration names

### ❌ DON'T:

- Never enable automatic migrations in production Dockerfile
- Don't add NOT NULL columns without default values
- Don't drop columns without backing up data first
- Don't rush - take time to review changes
- Don't assume dev and prod schemas match
- Don't run untested migrations on production

---

## Quick Reference

### Add a simple nullable column:

```sql
-- Production
ALTER TABLE assessments ADD COLUMN IF NOT EXISTS field_name VARCHAR(100);

-- Local (via migration)
op.add_column('assessments', sa.Column('field_name', sa.String(100), nullable=True))
```

### Add a JSON column:

```sql
-- Production
ALTER TABLE assessments ADD COLUMN IF NOT EXISTS field_name JSON;

-- Local (via migration)
op.add_column('assessments', sa.Column('field_name', sa.JSON(), nullable=True))
```

### Add a column with a default value:

```sql
-- Production
ALTER TABLE assessments ADD COLUMN IF NOT EXISTS field_name BOOLEAN DEFAULT FALSE;

-- Local (via migration)
op.add_column('assessments', sa.Column('field_name', sa.Boolean(), server_default='false'))
```

---

## Related Documentation

- [Database Migrations Guide](DATABASE_MIGRATIONS_GUIDE.md)
- [AWS RDS Setup](AWS_RDS_SETUP.md)
- [Production Ready Summary](PRODUCTION_READY_SUMMARY.md)

---

## Notes

- **Alembic Version Table:** Production does NOT have an `alembic_version` table. This is intentional since we manage migrations manually.
- **Migration Files:** Migration files exist for local development but are not used in production.
- **Schema Source of Truth:** The production database schema is the authoritative schema. Dev environments should match it.
