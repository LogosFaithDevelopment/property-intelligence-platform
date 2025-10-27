/**
 * Admin Authentication Hook
 * Checks if current Clerk user has admin access and fetches their role
 */

import { useUser, useAuth } from '@clerk/nextjs';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export type AdminRole = 'superadmin' | 'admin' | 'viewer';

interface AdminUser {
  isAdmin: boolean;
  role: AdminRole | null;
  email: string | null;
  isLoading: boolean;
}

// Cache to prevent multiple API calls for the same user
const adminCache = new Map<string, { data: AdminUser; timestamp: number }>();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

// In-flight requests to prevent duplicate API calls
const inFlightRequests = new Map<string, Promise<AdminUser>>();

async function fetchAdminStatus(
  userId: string,
  token: string,
  email: string
): Promise<AdminUser> {
  // If there's already a request in flight for this user, wait for it
  if (inFlightRequests.has(userId)) {
    console.log('⏳ Waiting for in-flight admin check...');
    return inFlightRequests.get(userId)!;
  }

  // Create a new request
  const requestPromise = (async () => {
    try {
      console.log('🔍 Checking admin access for:', email);

      // Call backend directly instead of through Next.js API route
      const backendUrl =
        process.env.NEXT_PUBLIC_API_URL ||
        (typeof window !== 'undefined'
          ? 'http://localhost:8000'
          : 'https://proper-Publi-82PMmiq7gkYF-1157142909.us-east-1.elb.amazonaws.com');

      // Only use HTTPS in production (when API URL is already HTTPS or on production domain)
      // For local development (localhost), keep HTTP
      const apiUrl = backendUrl.includes('localhost')
        ? backendUrl
        : backendUrl.replace('http://', 'https://');

      const response = await fetch(`${apiUrl}/api/v1/admin/auth/check`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      let resultData: AdminUser;

      if (response.ok) {
        const data = await response.json();
        resultData = {
          isAdmin: true,
          role: data.role,
          email: data.email,
          isLoading: false,
        };
        console.log('✅ Admin access confirmed:', data.role);
      } else {
        resultData = {
          isAdmin: false,
          role: null,
          email,
          isLoading: false,
        };
        console.log('❌ No admin access');
      }

      // Cache the result
      adminCache.set(userId, { data: resultData, timestamp: Date.now() });
      return resultData;
    } catch (error) {
      console.error('Error checking admin access:', error);
      return {
        isAdmin: false,
        role: null,
        email: null,
        isLoading: false,
      };
    } finally {
      // Remove from in-flight requests when done
      inFlightRequests.delete(userId);
    }
  })();

  inFlightRequests.set(userId, requestPromise);
  return requestPromise;
}

export function useAdminAuth(): AdminUser {
  const { user, isLoaded } = useUser();
  const { getToken } = useAuth();
  const [adminData, setAdminData] = useState<AdminUser>({
    isAdmin: false,
    role: null,
    email: null,
    isLoading: true,
  });

  useEffect(() => {
    let cancelled = false;

    async function checkAdminAccess() {
      if (!isLoaded) return;

      // Not signed in
      if (!user) {
        if (!cancelled) {
          setAdminData({
            isAdmin: false,
            role: null,
            email: null,
            isLoading: false,
          });
        }
        return;
      }

      const userId = user.id;
      const email = user.primaryEmailAddress?.emailAddress || null;

      // Check cache first
      const cached = adminCache.get(userId);
      if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
        console.log('✅ Using cached admin status');
        if (!cancelled) {
          setAdminData(cached.data);
        }
        return;
      }

      // Get Clerk session token
      const token = await getToken();
      if (!token) {
        if (!cancelled) {
          setAdminData({
            isAdmin: false,
            role: null,
            email,
            isLoading: false,
          });
        }
        return;
      }

      // Fetch admin status (will use in-flight request if available)
      const resultData = await fetchAdminStatus(userId, token, email || '');
      if (!cancelled) {
        setAdminData(resultData);
      }
    }

    checkAdminAccess();

    return () => {
      cancelled = true;
    };
  }, [user, isLoaded, getToken]);

  return adminData;
}

/**
 * Hook to redirect based on admin status
 * Use this on protected admin pages
 */
export function useRequireAdmin() {
  const { isAdmin, isLoading } = useAdminAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAdmin) {
      console.log(
        '❌ Non-admin trying to access admin page, redirecting to /submit-property'
      );
      router.push('/submit-property'); // Redirect non-admins to form
    }
  }, [isAdmin, isLoading, router]);

  return { isAdmin, isLoading };
}

/**
 * Clear admin cache
 * Call this when user roles change or for testing
 * Clears both in-memory and cookie caches
 */
export async function clearAdminCache() {
  console.log('🧹 Clearing admin cache...');

  // Clear in-memory cache
  adminCache.clear();
  inFlightRequests.clear();

  // Clear cookie cache
  try {
    await fetch('/api/admin/clear-cache', { method: 'POST' });
    console.log('✅ Admin cache cleared');
  } catch (error) {
    console.error('❌ Failed to clear admin cache:', error);
  }
}
