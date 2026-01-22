/**
 * Admin Layout
 * Protected layout for admin portal with navigation sidebar
 * Requires admin role to access
 */

'use client';

import { useRequireAdmin } from '@/hooks/useAdminAuth';
import { useClerk, useUser } from '@clerk/nextjs';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { Button } from '@/components/ui/button';
import {
  LayoutDashboard,
  FileText,
  Users,
  LogOut,
  Menu,
  X,
} from 'lucide-react';
import { useState } from 'react';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { isAdmin, isLoading } = useRequireAdmin();
  const { user } = useUser();
  const { signOut } = useClerk();
  const router = useRouter();
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Show loading state while checking admin access
  if (isLoading) {
    return (
      <div className='min-h-screen flex items-center justify-center'>
        <div className='text-center'>
          <div className='animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4'></div>
          <p className='text-gray-600'>Verifying admin access...</p>
        </div>
      </div>
    );
  }

  // useRequireAdmin will handle redirect if not admin
  if (!isAdmin) {
    return null;
  }

  const navItems = [
    {
      href: '/admin/dashboard',
      label: 'Dashboard',
      icon: LayoutDashboard,
    },
    {
      href: '/admin/submissions',
      label: 'Submissions',
      icon: FileText,
    },
    {
      href: '/admin/users',
      label: 'Admin Users',
      icon: Users,
    },
  ];

  return (
    <div className='min-h-screen bg-gray-50 flex'>
      {/* Mobile top navigation bar with white background */}
      <div className='lg:hidden fixed top-0 left-0 right-0 h-16 bg-white border-b border-gray-200 z-50 flex items-center px-4'>
        {/* Mobile menu button */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className='p-2 rounded-lg hover:bg-gray-100'
        >
          {sidebarOpen ? (
            <X className='h-6 w-6 text-gray-600' />
          ) : (
            <Menu className='h-6 w-6 text-gray-600' />
          )}
        </button>

        {/* Logo in top nav for mobile */}
        <Link href='/admin/dashboard' className='ml-3 flex items-center gap-2'>
          <div className='w-10 h-10 flex-shrink-0'>
            <Image
              src='/logos-icon.png'
              alt='Logos Development'
              width={40}
              height={40}
              className='object-contain w-full h-full'
            />
          </div>
          <div className='font-normal text-base font-[family-name:var(--font-safe-light-accent)]'>
            Logos Admin
          </div>
        </Link>
      </div>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className='lg:hidden fixed inset-0 bg-black bg-opacity-50 z-40 mt-16'
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar - Fixed on desktop, slide-in on mobile */}
      <aside
        className={`
          w-64 bg-white border-r border-gray-200 fixed flex flex-col z-40
          transition-transform duration-300 ease-in-out
          top-16 bottom-0 lg:top-0 lg:h-full
          ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
          lg:translate-x-0
        `}
      >
        <div className='flex-1 overflow-y-auto'>
          <div className='p-6'>
            {/* Logo */}
            <Link href='/admin/dashboard'>
              <div className='flex items-center gap-1.5 mb-8 cursor-pointer hover:opacity-80'>
                <div className='w-14 h-14 flex-shrink-0'>
                  <Image
                    src='/logos-icon.png'
                    alt='Logos Development'
                    width={56}
                    height={56}
                    className='object-contain w-full h-full'
                  />
                </div>
                <div className='flex flex-col gap-0.5'>
                  <div className='font-normal text-lg font-[family-name:var(--font-safe-light-accent)] leading-tight'>
                    Logos Admin
                  </div>
                  <div className='text-xs text-gray-500 leading-tight'>
                    Property Management
                  </div>
                </div>
              </div>
            </Link>

            {/* Navigation */}
            <nav className='space-y-2'>
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive =
                  pathname === item.href ||
                  pathname.startsWith(item.href + '/');
                return (
                  <Link key={item.href} href={item.href}>
                    <div
                      onClick={() => setSidebarOpen(false)}
                      className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors cursor-pointer ${
                        isActive
                          ? 'bg-blue-50 text-blue-600 font-medium'
                          : 'text-gray-700 hover:bg-gray-50'
                      }`}
                    >
                      <Icon className='h-5 w-5' />
                      <span>{item.label}</span>
                    </div>
                  </Link>
                );
              })}
            </nav>
          </div>
        </div>

        {/* User info at bottom */}
        <div className='p-6 border-t border-gray-200'>
          <div className='flex items-center gap-3 mb-4'>
            <div className='w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center'>
              <span className='text-blue-600 font-medium'>
                {user?.firstName?.[0] ||
                  user?.emailAddresses[0].emailAddress[0].toUpperCase()}
              </span>
            </div>
            <div className='flex-1 min-w-0'>
              <div className='text-sm font-medium truncate'>
                {user?.firstName} {user?.lastName}
              </div>
              <div className='text-xs text-gray-500 truncate'>
                {user?.emailAddresses[0].emailAddress}
              </div>
            </div>
          </div>
          <Button
            variant='outline'
            size='sm'
            className='w-full'
            onClick={() =>
              signOut({
                redirectUrl: '/',
              })
            }
          >
            <LogOut className='h-4 w-4 mr-2' />
            Sign Out
          </Button>
        </div>
      </aside>

      {/* Main content - Responsive padding */}
      <main className='flex-1 lg:ml-64 px-4 sm:px-6 lg:px-12 py-6 sm:py-8 lg:py-12 pt-16 lg:pt-12 overflow-x-hidden'>
        {children}
      </main>
    </div>
  );
}
