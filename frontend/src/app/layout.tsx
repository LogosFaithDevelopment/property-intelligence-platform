import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { ClerkProvider } from '@clerk/nextjs';
import { ReactQueryProvider } from '@/providers/react-query-provider';
import { Toaster } from 'sonner';
import { Header } from '@/components/layout/header';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
});

export const metadata: Metadata = {
  title: 'Property Intelligence Platform | Logos Development',
  description:
    'Partner with Logos to develop church property into affordable housing',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html lang='en'>
        <body className={`${inter.variable} font-sans antialiased`}>
          <Header />
          <ReactQueryProvider>
            {children}
            <Toaster position='top-right' />
          </ReactQueryProvider>
        </body>
      </html>
    </ClerkProvider>
  );
}
