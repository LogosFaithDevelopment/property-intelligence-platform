import type { Metadata, Viewport } from 'next';
import { Inter, Playfair_Display } from 'next/font/google';
import './globals.css';
import { ClerkProvider } from '@clerk/nextjs';
import { ReactQueryProvider } from '@/providers/react-query-provider';
import { Toaster } from 'sonner';
import { ConditionalHeader } from '@/components/layout/conditional-header';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
});

const safeLightAccent = Playfair_Display({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-safe-light-accent',
});

export const metadata: Metadata = {
  title: 'Property Intelligence Platform | Logos Development',
  description:
    'Partner with Logos to develop church property into affordable housing',
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  userScalable: true,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html lang='en'>
        <body
          className={`${inter.variable} ${safeLightAccent.variable} font-sans antialiased`}
        >
          <ConditionalHeader />
          <ReactQueryProvider>
            {children}
            <Toaster position='top-right' />
          </ReactQueryProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
