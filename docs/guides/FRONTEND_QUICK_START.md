# 🚀 Frontend Quick Start Guide

**Get your frontend up and running in 30 minutes!**

---

## 📋 Prerequisites

- **Node.js 18+** installed
- **Git** installed
- **VS Code** (recommended)
- Clerk account (free tier)
- Mapbox account (free tier)

---

## ⚡ Quick Setup (5 commands)

```bash
# 1. Create Next.js project
npx create-next-app@latest property-intelligence-frontend \
  --typescript \
  --tailwind \
  --app \
  --eslint

# 2. Navigate to project
cd property-intelligence-frontend

# 3. Install core dependencies
npm install @clerk/nextjs @tanstack/react-query axios recharts mapbox-gl date-fns lucide-react

# 4. Setup shadcn/ui
npx shadcn-ui@latest init

# 5. Start development
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) 🎉

---

## 🔑 Get Your API Keys

### **1. Clerk (Authentication)**

1. Go to [clerk.com](https://clerk.com)
2. Create free account
3. Create new application
4. Copy these keys:
   - **Publishable Key**: `pk_test_...`
   - **Secret Key**: `sk_test_...`

### **2. Mapbox (Maps)**

1. Go to [mapbox.com](https://mapbox.com)
2. Create free account
3. Copy **Access Token**: `pk.eyJ1...`

---

## 📝 Environment Setup

Create `.env.local` file:

```env
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Clerk Auth
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_YOUR_KEY_HERE
CLERK_SECRET_KEY=sk_test_YOUR_KEY_HERE

# Mapbox
NEXT_PUBLIC_MAPBOX_TOKEN=pk.eyJ1YOUR_TOKEN_HERE
```

> ⚠️ **Never commit this file!** Already in `.gitignore`

---

## 🎨 Install shadcn/ui Components

```bash
# Core UI components
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add input
npx shadcn-ui@latest add form
npx shadcn-ui@latest add table
npx shadcn-ui@latest add dialog
npx shadcn-ui@latest add badge
npx shadcn-ui@latest add select
npx shadcn-ui@latest add dropdown-menu
npx shadcn-ui@latest add tabs
npx shadcn-ui@latest add alert
npx shadcn-ui@latest add toast
```

---

## 🏗️ Project Structure

```
property-intelligence-frontend/
├── app/                      # Next.js App Router
│   ├── (auth)/              # Protected pages
│   │   ├── layout.tsx       # Auth layout
│   │   ├── dashboard/       # Dashboard pages
│   │   ├── churches/        # Church pages
│   │   ├── properties/      # Property pages
│   │   └── assessments/     # Assessment pages
│   ├── (public)/            # Public pages
│   │   ├── page.tsx         # Landing page
│   │   └── about/
│   ├── api/                 # API routes
│   ├── layout.tsx           # Root layout
│   └── globals.css          # Global styles
│
├── components/              # React components
│   ├── ui/                  # shadcn/ui components
│   ├── layout/              # Layout components
│   ├── churches/            # Church components
│   ├── properties/          # Property components
│   └── assessments/         # Assessment components
│
├── lib/                     # Utility functions
│   ├── api-client.ts        # Axios setup
│   ├── utils.ts             # Helper functions
│   └── constants.ts         # Constants
│
├── hooks/                   # Custom React hooks
│   ├── useProperties.ts     # Property queries
│   ├── useChurches.ts       # Church queries
│   └── useAssessments.ts    # Assessment queries
│
├── types/                   # TypeScript types
│   ├── property.ts
│   ├── church.ts
│   └── assessment.ts
│
└── public/                  # Static assets
    ├── images/
    └── icons/
```

---

## 🔐 Setup Authentication

### **1. Wrap app with Clerk**

```tsx
// app/layout.tsx
import { ClerkProvider } from '@clerk/nextjs';

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ClerkProvider>
      <html lang='en'>
        <body>{children}</body>
      </html>
    </ClerkProvider>
  );
}
```

### **2. Create middleware**

```tsx
// middleware.ts
import { authMiddleware } from '@clerk/nextjs';

export default authMiddleware({
  publicRoutes: ['/', '/about'],
});

export const config = {
  matcher: ['/((?!.+\\.[\\w]+$|_next).*)', '/', '/(api|trpc)(.*)'],
};
```

### **3. Add sign-in button**

```tsx
// app/page.tsx
import { SignInButton, SignUpButton } from '@clerk/nextjs';

export default function Home() {
  return (
    <div>
      <h1>Welcome</h1>
      <SignInButton mode='modal'>
        <button>Sign In</button>
      </SignInButton>
      <SignUpButton mode='modal'>
        <button>Sign Up</button>
      </SignUpButton>
    </div>
  );
}
```

---

## 🔌 Setup API Client

```typescript
// lib/api-client.ts
import axios from 'axios';
import { useAuth } from '@clerk/nextjs';

const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to all requests
apiClient.interceptors.request.use(async (config) => {
  const { getToken } = useAuth();
  const token = await getToken();

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export default apiClient;
```

---

## 📊 Setup React Query

```tsx
// app/providers.tsx
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { useState } from 'react';

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            retry: 1,
          },
        },
      })
  );

  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  );
}
```

```tsx
// app/layout.tsx (update)
import { Providers } from './providers';

export default function RootLayout({ children }) {
  return (
    <ClerkProvider>
      <html lang='en'>
        <body>
          <Providers>{children}</Providers>
        </body>
      </html>
    </ClerkProvider>
  );
}
```

---

## 🎯 First Feature: Church List

### **1. Create Church Type**

```typescript
// types/church.ts
export interface Church {
  id: number;
  name: string;
  street_address: string;
  city: string;
  state: string;
  zip_code: string;
  primary_contact_name?: string;
  primary_email?: string;
  primary_phone?: string;
  congregation_size?: number;
  created_at: string;
  updated_at: string;
}
```

### **2. Create API Hook**

```typescript
// hooks/useChurches.ts
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/lib/api-client';
import { Church } from '@/types/church';

export const useChurches = () => {
  return useQuery<Church[]>({
    queryKey: ['churches'],
    queryFn: async () => {
      const { data } = await apiClient.get('/churches');
      return data;
    },
  });
};
```

### **3. Create Church List Page**

```tsx
// app/(auth)/churches/page.tsx
'use client';

import { useChurches } from '@/hooks/useChurches';
import { Card } from '@/components/ui/card';

export default function ChurchesPage() {
  const { data: churches, isLoading, error } = useChurches();

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading churches</div>;

  return (
    <div className='container mx-auto py-8'>
      <h1 className='text-3xl font-bold mb-6'>Churches</h1>

      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'>
        {churches?.map((church) => (
          <Card key={church.id} className='p-6'>
            <h2 className='text-xl font-semibold'>{church.name}</h2>
            <p className='text-gray-600 mt-2'>
              {church.city}, {church.state}
            </p>
            {church.congregation_size && (
              <p className='text-sm text-gray-500 mt-2'>
                {church.congregation_size.toLocaleString()} members
              </p>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
}
```

---

## 🎨 Tailwind Config

```typescript
// tailwind.config.ts
import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: ['class'],
  content: [
    './pages/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './app/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#2c5aa0',
          foreground: '#ffffff',
          50: '#e6f2ff',
          100: '#b3d9ff',
          500: '#2c5aa0',
          700: '#1e4176',
          900: '#0d1f3d',
        },
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
};

export default config;
```

---

## 🧪 Testing Your Setup

### **1. Test Backend Connection**

```typescript
// app/api/health/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/health`);
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json({ error: 'Backend unreachable' }, { status: 500 });
  }
}
```

Visit: [http://localhost:3000/api/health](http://localhost:3000/api/health)

### **2. Test Authentication**

```tsx
// app/(auth)/test/page.tsx
'use client';

import { useUser } from '@clerk/nextjs';

export default function TestPage() {
  const { user, isLoaded } = useUser();

  if (!isLoaded) return <div>Loading...</div>;

  return (
    <div className='p-8'>
      <h1>Authentication Test</h1>
      <pre className='bg-gray-100 p-4 rounded mt-4'>
        {JSON.stringify(user, null, 2)}
      </pre>
    </div>
  );
}
```

---

## 🐛 Common Issues & Fixes

### **Issue: CORS Errors**

**Solution:** Backend must allow your frontend origin:

```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### **Issue: Clerk Webhooks**

**Solution:** Add webhook URL in Clerk dashboard:

- URL: `https://your-domain.com/api/webhooks/clerk`
- Events: `user.created`, `user.updated`, `user.deleted`

### **Issue: Environment Variables Not Loading**

**Solution:**

1. Restart dev server after changing `.env.local`
2. Ensure file is in root directory
3. Check for typos in variable names

---

## 📚 Next Steps

Now that your frontend is running:

1. ✅ **Read** `FRONTEND_BUILD_PLAN.md` for full roadmap
2. 🎨 **Design** wireframes for key pages
3. 🏗️ **Build** Dashboard page (Phase 2)
4. 📊 **Add** Property management (Phase 3)
5. 🚀 **Deploy** to Vercel when ready

---

## 🔗 Useful Links

- **Your Backend**: [http://localhost:8000](http://localhost:8000)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Clerk Dashboard**: [https://dashboard.clerk.com](https://dashboard.clerk.com)

---

## 💡 Pro Tips

1. **Use TypeScript** - Catch errors early
2. **Install ESLint/Prettier** - Consistent code style
3. **Use React DevTools** - Debug components
4. **Use Tanstack Query DevTools** - Monitor API calls
5. **Commit often** - Small, focused commits

---

**Questions? Stuck? Need help?**

Check the full `FRONTEND_BUILD_PLAN.md` or ask your team! 🚀

**Happy coding!** 🎉
