import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self';",
              "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://*.clerk.dev https://*.accounts.dev;",
              "worker-src 'self' blob:;",
              'connect-src *;',
              'img-src * blob: data:;',
              "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;",
              "font-src 'self' https://fonts.gstatic.com;",
              'frame-src https://*.clerk.dev https://*.accounts.dev;',
            ].join(' '),
          },
        ],
      },
    ];
  },
};

export default nextConfig;
