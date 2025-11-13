#!/bin/bash
# Script to create all Copilot secrets properly

echo "Creating Copilot secrets for production environment..."
echo ""

# Read from .env file and create secrets
echo "Reading values from .env.production.local..."

# Extract values
ATTOM_API_KEY=$(grep "^ATTOM_API_KEY=" .env.production.local | cut -d'=' -f2)
OPENAI_API_KEY=$(grep "^OPENAI_API_KEY=" .env.production.local | cut -d'=' -f2)
SECRET_KEY=$(grep "^SECRET_KEY=" .env.production.local | cut -d'=' -f2)
CLERK_SECRET_KEY=$(grep "^CLERK_SECRET_KEY=" .env.production.local | cut -d'=' -f2)
SMARTY_AUTH_ID=$(grep "^SMARTY_AUTH_ID=" .env.production.local | cut -d'=' -f2)
SMARTY_AUTH_TOKEN=$(grep "^SMARTY_AUTH_TOKEN=" .env.production.local | cut -d'=' -f2)
HUD_API_KEY=$(grep "^HUD_API_KEY=" .env.production.local | cut -d'=' -f2)
GOOGLE_MAPS_API_KEY=$(grep "^GOOGLE_MAPS_API_KEY=" .env.production.local | cut -d'=' -f2)

# Create secrets using AWS SSM directly
echo "Creating secrets in SSM Parameter Store..."

aws ssm put-parameter --name "/copilot/property-intel/production/secrets/ATTOM_API_KEY" --value "$ATTOM_API_KEY" --type "SecureString" --overwrite
echo "✓ Created ATTOM_API_KEY"

aws ssm put-parameter --name "/copilot/property-intel/production/secrets/OPENAI_API_KEY" --value "$OPENAI_API_KEY" --type "SecureString" --overwrite
echo "✓ Created OPENAI_API_KEY"

aws ssm put-parameter --name "/copilot/property-intel/production/secrets/SECRET_KEY" --value "$SECRET_KEY" --type "SecureString" --overwrite
echo "✓ Created SECRET_KEY"

aws ssm put-parameter --name "/copilot/property-intel/production/secrets/CLERK_SECRET_KEY" --value "$CLERK_SECRET_KEY" --type "SecureString" --overwrite
echo "✓ Created CLERK_SECRET_KEY"

aws ssm put-parameter --name "/copilot/property-intel/production/secrets/SMARTY_AUTH_ID" --value "$SMARTY_AUTH_ID" --type "SecureString" --overwrite
echo "✓ Created SMARTY_AUTH_ID"

aws ssm put-parameter --name "/copilot/property-intel/production/secrets/SMARTY_AUTH_TOKEN" --value "$SMARTY_AUTH_TOKEN" --type "SecureString" --overwrite
echo "✓ Created SMARTY_AUTH_TOKEN"

aws ssm put-parameter --name "/copilot/property-intel/production/secrets/HUD_API_KEY" --value "$HUD_API_KEY" --type "SecureString" --overwrite
echo "✓ Created HUD_API_KEY"

aws ssm put-parameter --name "/copilot/property-intel/production/secrets/GOOGLE_MAPS_API_KEY" --value "$GOOGLE_MAPS_API_KEY" --type "SecureString" --overwrite
echo "✓ Created GOOGLE_MAPS_API_KEY"

echo ""
echo "All secrets created successfully!"
echo ""
echo "Verifying secrets..."
aws ssm describe-parameters --query "Parameters[?starts_with(Name, '/copilot/property-intel/production/secrets/')].Name" --output table

echo ""
echo "Now you can deploy with: copilot svc deploy --name backend --env production"
