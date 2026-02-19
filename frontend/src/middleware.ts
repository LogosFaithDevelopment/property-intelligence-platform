import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';

// Public routes that don't require authentication
const isPublicRoute = createRouteMatcher([
  '/',
  '/sign-in(.*)',
  '/sign-up(.*)',
  '/partner-with-us',
  '/how-it-works',
  '/success-stories',
  '/faq',
  '/submit-property', // Allow public property submissions
  '/submission-success',
  '/submission-status',
  '/api/health', // Health check endpoint for ELB - must be fast and not require auth
]);

/**
 * Check if user is an admin by calling the backend
 * This runs server-side BEFORE the page loads
 */
async function checkAdminStatus(token: string): Promise<boolean> {
  try {
    const backendUrl = process.env.BACKEND_URL || 'http://backend:8000';
    const response = await fetch(`${backendUrl}/api/v1/admin/auth/check`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      // Add timeout to prevent hanging
      signal: AbortSignal.timeout(3000),
    });

    return response.ok;
  } catch (error) {
    console.error('❌ Admin check failed in middleware:', error);
    return false;
  }
}

export default clerkMiddleware(async (auth, request) => {
  const pathname = request.nextUrl.pathname;

  // Fast-path for health checks - skip all auth and logic
  if (pathname === '/api/health') {
    return NextResponse.next();
  }

  const { userId, getToken } = await auth();

  // Clear admin cache when user signs out
  if (!userId && request.cookies.has('admin_role')) {
    const response = NextResponse.next();
    response.cookies.delete('admin_role');
    response.cookies.delete('admin_cache_time');
    return response;
  }

  // Protect non-public routes
  if (!isPublicRoute(request)) {
    await auth.protect();
  }

  // Role-based redirect for signed-in users on homepage
  if (pathname === '/' && userId) {
    // Check if we have a cached admin status
    const cachedRole = request.cookies.get('admin_role');
    const cacheTimestamp = request.cookies.get('admin_cache_time');
    const now = Date.now();
    const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

    let isAdmin = false;
    let shouldUpdateCache = true;

    // Use cached value if it's recent
    if (
      cachedRole &&
      cacheTimestamp &&
      now - parseInt(cacheTimestamp.value) < CACHE_DURATION
    ) {
      isAdmin = cachedRole.value === 'true';
      shouldUpdateCache = false;
      console.log('✅ Using cached admin status:', isAdmin);
    } else {
      // Check admin status from backend
      const token = await getToken();
      if (token) {
        isAdmin = await checkAdminStatus(token);
        console.log('🔍 Checked admin status from backend:', isAdmin);
      }
    }

    // Redirect based on role
    const redirectUrl = isAdmin ? '/admin/dashboard' : '/submit-property';
    const response = NextResponse.redirect(
      new URL(redirectUrl, request.nextUrl.origin),
    );

    // Update cache if needed
    if (shouldUpdateCache) {
      response.cookies.set('admin_role', String(isAdmin), {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 60 * 5, // 5 minutes
      });
      response.cookies.set('admin_cache_time', String(now), {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 60 * 5, // 5 minutes
      });
    }

    return response;
  }

  return NextResponse.next();
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
};
