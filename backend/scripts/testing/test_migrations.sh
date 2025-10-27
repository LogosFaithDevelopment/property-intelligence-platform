#!/bin/bash
# Test Alembic migrations on a clean database

set -e  # Exit on error

echo "=========================================="
echo "Alembic Migration Testing Script"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the backend directory
if [ ! -f "alembic.ini" ]; then
    echo -e "${RED}ERROR: alembic.ini not found. Please run this script from the backend/ directory.${NC}"
    exit 1
fi

# Database configuration
DB_NAME="${TEST_DB_NAME:-property_intel_test}"
DB_USER="${TEST_DB_USER:-postgres}"
DB_PASSWORD="${TEST_DB_PASSWORD:-postgres}"
DB_HOST="${TEST_DB_HOST:-localhost}"
DB_PORT="${TEST_DB_PORT:-5432}"

echo "Database Configuration:"
echo "  Host: $DB_HOST:$DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""

# Test database connection
echo -e "${YELLOW}[1/6] Testing database connection...${NC}"
if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres -c '\q' 2>/dev/null; then
    echo -e "${GREEN}✓ Database connection successful${NC}"
else
    echo -e "${RED}✗ Cannot connect to database. Please ensure PostgreSQL is running.${NC}"
    echo ""
    echo "Try running: docker-compose up -d postgres"
    echo "Or: brew services start postgresql@14"
    exit 1
fi
echo ""

# Drop test database if exists
echo -e "${YELLOW}[2/6] Creating clean test database...${NC}"
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d postgres << EOF
DROP DATABASE IF EXISTS $DB_NAME;
CREATE DATABASE $DB_NAME;
EOF
echo -e "${GREEN}✓ Clean database '$DB_NAME' created${NC}"
echo ""

# Set DATABASE_URL for Alembic
export DATABASE_URL="postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"

# Check current migration status (should be empty)
echo -e "${YELLOW}[3/6] Checking initial migration status...${NC}"
alembic current
echo ""

# Run all migrations
echo -e "${YELLOW}[4/6] Running all migrations (alembic upgrade head)...${NC}"
if alembic upgrade head; then
    echo -e "${GREEN}✓ All migrations applied successfully${NC}"
else
    echo -e "${RED}✗ Migration failed${NC}"
    exit 1
fi
echo ""

# Show current migration status
echo -e "${YELLOW}[5/6] Current migration status:${NC}"
alembic current
echo ""

# Show migration history
echo "Migration history:"
alembic history
echo ""

# Test rollback (downgrade one step)
echo -e "${YELLOW}[6/6] Testing rollback (alembic downgrade -1)...${NC}"
if alembic downgrade -1; then
    echo -e "${GREEN}✓ Rollback successful${NC}"
else
    echo -e "${RED}✗ Rollback failed${NC}"
    exit 1
fi
echo ""

# Show status after rollback
echo "Status after rollback:"
alembic current
echo ""

# Re-upgrade to head
echo -e "${YELLOW}Re-applying last migration...${NC}"
if alembic upgrade head; then
    echo -e "${GREEN}✓ Re-upgrade successful${NC}"
else
    echo -e "${RED}✗ Re-upgrade failed${NC}"
    exit 1
fi
echo ""

# Verify final state
echo -e "${YELLOW}Final database state:${NC}"
alembic current
echo ""

# List all tables
echo "Tables created:"
PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "\dt" | grep -v "Did not find"
echo ""

echo -e "${GREEN}=========================================="
echo "✓ All migration tests passed!"
echo "==========================================${NC}"
echo ""
echo "Summary:"
echo "  • All migrations applied successfully"
echo "  • Rollback tested and working"
echo "  • Re-upgrade tested and working"
echo ""
echo "To inspect the database:"
echo "  PGPASSWORD='$DB_PASSWORD' psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME"
echo ""
echo "To clean up:"
echo "  PGPASSWORD='$DB_PASSWORD' psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d postgres -c 'DROP DATABASE $DB_NAME;'"
echo ""
