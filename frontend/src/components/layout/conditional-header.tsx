/**
 * Conditional Header
 * Shows the public header on all pages EXCEPT admin routes
 * Admin routes have their own header in the admin layout
 */

'use client';

import { usePathname } from 'next/navigation';
import { Header } from './header';

export function ConditionalHeader() {
  const pathname = usePathname();

  // Hide header on admin routes - admin layout has its own header
  if (pathname?.startsWith('/admin')) {
    return null;
  }

  return <Header />;
}
