'use client';

import Link from 'next/link';
import Image from 'next/image';
import { UserButton, useUser } from '@clerk/nextjs';
import { Button } from '@/components/ui/button';

export function Header() {
  const { isSignedIn, isLoaded } = useUser();

  return (
    <header className='sticky top-0 z-50 border-b bg-white shadow-sm'>
      <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8'>
        <div className='flex h-16 items-center justify-between'>
          {/* Logo */}
          <Link href='/' className='flex items-center'>
            <Image
              src='/logos-icon.png'
              alt='Logos Development'
              width={60}
              height={60}
              className='object-contain'
            />
            <div className='flex flex-col -ml-1'>
              <div className='text-2xl font-bold bg-gradient-to-r from-yellow-500 to-yellow-700 bg-clip-text text-transparent font-[family-name:var(--font-safe-light-accent)]'>
                Logos
              </div>
              <span className='text-xs text-gray-500'>
                Property Intelligence
              </span>
            </div>
          </Link>

          {/* Navigation */}
          {/* <nav className='hidden md:flex items-center space-x-8'>
            <Link
              href='/submit-property'
              className='text-gray-700 hover:text-blue-600 transition-colors'
            >
              Submit Property
            </Link>
            <Link
              href='/submission-status'
              className='text-gray-700 hover:text-blue-600 transition-colors'
            >
              Check Status
            </Link>
            <Link
              href='/how-it-works'
              className='text-gray-700 hover:text-blue-600 transition-colors'
            >
              How It Works
            </Link>
          </nav> */}

          {/* User Menu */}
          <div className='flex items-center'>
            {isLoaded && (
              <>
                {isSignedIn ? (
                  <div className='flex items-center gap-4'>
                    <span className='text-sm text-gray-600 hidden sm:inline'>
                      Signed in
                    </span>
                    <UserButton
                      afterSignOutUrl='/'
                      appearance={{
                        elements: {
                          avatarBox: 'h-10 w-10',
                        },
                      }}
                    />
                  </div>
                ) : (
                  <Link href='/sign-in'>
                    <Button size='sm'>Sign In</Button>
                  </Link>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
