/**
 * Role-Based Redirect
 * Automatically redirects users after Clerk authentication based on their role
 * - Admins → /admin/dashboard
 * - Regular users → /submit-property
 *
 * This component only redirects when mounted on the landing page
 * Shows a loading overlay while checking admin status to prevent flash of content
 */

'use client';

import { useUser } from '@clerk/nextjs';
import { useRouter, usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import { useAdminAuth } from '@/hooks/useAdminAuth';
import { Loader2 } from 'lucide-react';

export default function RoleBasedRedirect() {
  const { isLoaded: clerkLoaded, user } = useUser();
  const { isAdmin, isLoading: adminLoading } = useAdminAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [hasRedirected, setHasRedirected] = useState(false);

  // Show loading overlay if user is signed in and we're checking their role
  const showLoading =
    clerkLoaded && user && adminLoading && pathname === '/' && !hasRedirected;

  useEffect(() => {
    // Only redirect if we're on the landing page and haven't redirected yet
    if (pathname !== '/' || hasRedirected) return;

    // Wait for both Clerk and admin check to load
    if (!clerkLoaded || adminLoading) return;

    // Not signed in - stay on landing page
    if (!user) return;

    // User is signed in and admin check is complete - redirect once
    console.log('🔀 Role-based redirect:', {
      isAdmin,
      user: user.primaryEmailAddress?.emailAddress,
    });

    setHasRedirected(true);

    if (isAdmin) {
      console.log('✅ Redirecting admin to /admin/dashboard');
      router.push('/admin/dashboard');
    } else {
      console.log('✅ Redirecting regular user to /submit-property');
      router.push('/submit-property');
    }
  }, [
    clerkLoaded,
    user,
    isAdmin,
    adminLoading,
    router,
    pathname,
    hasRedirected,
  ]);

  // Show loading overlay while checking admin status
  if (showLoading) {
    return (
      <div className='fixed inset-0 bg-white z-50 flex items-center justify-center'>
        <div className='text-center'>
          <Loader2 className='h-12 w-12 animate-spin text-blue-600 mx-auto mb-4' />
          <p className='text-gray-600'>Loading...</p>
        </div>
      </div>
    );
  }

  return null;
}
