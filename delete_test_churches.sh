#!/bin/bash
# Delete Test Churches Script
# Safely deletes jack@rbc.org and john@gracecc.com with all related data

echo "🗑️  Deleting test churches: jack@rbc.org, john@gracecc.com"
echo ""
echo "📊 Checking what will be deleted..."
echo ""

# Get the postgres container name
POSTGRES_CONTAINER=$(docker ps --filter "ancestor=postgis/postgis:15-3.3" --format "{{.Names}}")

if [ -z "$POSTGRES_CONTAINER" ]; then
    echo "❌ Error: Postgres container not running!"
    echo "Please start Docker containers first: docker-compose up -d"
    exit 1
fi

echo "📦 Using container: $POSTGRES_CONTAINER"
echo ""

# Execute the SQL file using Docker
docker exec -i $POSTGRES_CONTAINER psql -U postgres -d property_intel < delete_test_churches.sql

echo ""
echo "✅ Deletion complete!"
echo ""
echo "🔍 To verify in Adminer:"
echo "   1. Go to http://localhost:8080"
echo "   2. Click on 'churches' table"
echo "   3. Search for jack@rbc.org or john@gracecc.com"
echo "   4. Should return no results"
