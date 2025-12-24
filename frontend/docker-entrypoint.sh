#!/bin/sh
set -e

# This script injects runtime environment variables into the Next.js build
# Replacing the build-time placeholders with actual runtime values

echo "Injecting runtime environment variables..."

# Find all JS files in the standalone build
find /app/.next -type f -name "*.js" -exec sed -i \
  -e "s|RUNTIME_NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY|${NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}|g" \
  -e "s|RUNTIME_NEXT_PUBLIC_API_URL|${NEXT_PUBLIC_API_URL}|g" \
  -e "s|RUNTIME_NEXT_PUBLIC_ENVIRONMENT|${NEXT_PUBLIC_ENVIRONMENT}|g" \
  {} +

echo "Environment variables injected successfully"

# Start Next.js server
exec node server.js
