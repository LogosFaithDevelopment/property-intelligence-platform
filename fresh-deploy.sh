#!/bin/bash
set -e

echo "=== STEP 1: Complete Cleanup ==="

# Delete CloudFormation stack if it exists
echo "Deleting backend CloudFormation stack..."
aws cloudformation delete-stack --stack-name property-intel-production-backend 2>/dev/null || echo "No stack to delete"

# Wait for stack deletion
echo "Waiting for stack deletion to complete..."
aws cloudformation wait stack-delete-complete --stack-name property-intel-production-backend 2>/dev/null || echo "Stack already deleted"

# Delete all SSM parameters (copilot secrets)
echo "Deleting all SSM parameters..."
aws ssm get-parameters-by-path --path "/copilot/property-intel/production/secrets" --query "Parameters[].Name" --output text 2>/dev/null | xargs -n 1 -I {} aws ssm delete-parameter --name {} 2>/dev/null || echo "No SSM parameters found"

echo ""
echo "=== STEP 2: Cleanup Complete ==="
echo ""
echo "Now run these commands to create secrets with the correct names:"
echo ""
echo "copilot secret init --name ATTOM_API_KEY"
echo "copilot secret init --name OPENAI_API_KEY"
echo "copilot secret init --name SECRET_KEY"
echo "copilot secret init --name CLERK_SECRET_KEY"
echo "copilot secret init --name SMARTY_AUTH_ID"
echo "copilot secret init --name SMARTY_AUTH_TOKEN"
echo "copilot secret init --name HUD_API_KEY"
echo "copilot secret init --name GOOGLE_MAPS_API_KEY"
echo ""
echo "After creating all secrets, run:"
echo "copilot svc deploy --name backend --env production"
