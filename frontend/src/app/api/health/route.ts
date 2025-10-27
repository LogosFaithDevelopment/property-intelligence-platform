/**
 * Frontend Health Check API Route
 * For AWS ECS load balancer health checks
 */

import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  // Log health check for debugging (will show in CloudWatch)
  const timestamp = new Date().toISOString();
  console.log(
    `[${timestamp}] Health check request from:`,
    request.headers.get('user-agent')
  );

  // Simple health check - returns 200 if Next.js server is running
  return NextResponse.json(
    {
      status: 'healthy',
      service: 'property-intelligence-platform-frontend',
      timestamp,
    },
    { status: 200 }
  );
}
