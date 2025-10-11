/**
 * Admin Check API Route
 * Proxies admin auth check to backend to avoid CORS issues
 */

import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    // Get authorization header from the request
    const authHeader = request.headers.get('authorization');

    if (!authHeader) {
      return NextResponse.json(
        { error: 'Missing authorization header' },
        { status: 401 }
      );
    }

    // Forward the request to the backend
    // Use Docker service name when running in Docker, localhost for local dev
    const backendUrl = process.env.BACKEND_URL || 'http://backend:8000';
    console.log(
      'Forwarding admin check to:',
      `${backendUrl}/api/v1/admin/auth/check`
    );

    const response = await fetch(`${backendUrl}/api/v1/admin/auth/check`, {
      headers: {
        Authorization: authHeader,
      },
    });

    // Forward the response from backend
    if (response.ok) {
      const data = await response.json();
      return NextResponse.json(data);
    } else {
      const error = await response
        .json()
        .catch(() => ({ detail: 'Unauthorized' }));
      return NextResponse.json(error, { status: response.status });
    }
  } catch (error) {
    console.error('Error checking admin access:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
