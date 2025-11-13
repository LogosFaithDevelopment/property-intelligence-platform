'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useRouter } from 'next/navigation';
import { useUser } from '@clerk/nextjs';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import {
  CheckCircle,
  TrendingUp,
  Home,
  DollarSign,
  Building2,
} from 'lucide-react';

export default function HomePage() {
  const { isSignedIn, isLoaded } = useUser();
  const router = useRouter();

  return (
    <>
      {/* Role-based redirect now happens in middleware.ts - no flash! */}

      <div className='fixed inset-0 overflow-hidden bg-gradient-to-b from-blue-50 to-white'>
        {/* Hero Section */}
        <div className='container mx-auto px-4 h-full flex flex-col justify-center -mt-[70px] md:pt-0 md:-mt-16'>
          <nav className='flex justify-between items-center mb-4 md:mb-12 mt-[100px] md:mt-0'>
            <div className='flex-1 flex justify-center'>
              <Image
                src='/home-logos.png'
                alt='Logos Faith Development'
                width={200}
                height={65}
                className='object-contain'
              />
            </div>
            <div className='flex gap-4 absolute right-4 md:right-8 top-28 md:top-20'>
              {isLoaded && (
                <>
                  {isSignedIn ? (
                    <Button onClick={() => router.push('/submit-property')}>
                      Submit Property
                    </Button>
                  ) : (
                    <Link href='/sign-up'>
                      <Button>Sign Up</Button>
                    </Link>
                  )}
                </>
              )}
            </div>
          </nav>

          <div className='max-w-4xl mx-auto text-center'>
            <h1 className='text-3xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-blue-600 to-blue-800 bg-clip-text text-transparent max-w-[280px] md:max-w-none mx-auto'>
              Transforming Underutilized Land Into Housing
            </h1>
            <p className='text-xl text-gray-600 mb-8'>
              We provide 100% private funding.
            </p>
            <div className='flex gap-4 justify-center flex-wrap'>
              {isLoaded && (
                <>
                  {isSignedIn ? (
                    <Button
                      size='lg'
                      className='text-lg px-8'
                      onClick={() => router.push('/submit-property')}
                    >
                      Submit Your Property
                    </Button>
                  ) : (
                    <Link href='/sign-in'>
                      <Button size='lg' className='text-lg px-8'>
                        Submit Your Property for Review
                      </Button>
                    </Link>
                  )}
                </>
              )}
              <Link href='/partner-with-us'>
                <Button size='lg' variant='outline' className='text-lg px-8'>
                  Learn More
                </Button>
              </Link>
            </div>
          </div>
        </div>

        {/* Benefits Section */}
        {/* <div className='container mx-auto px-4 py-16'>
          <h2 className='text-3xl font-bold text-center mb-12'>
            Why Partner With Logos Faith Development?
          </h2>
          <div className='grid md:grid-cols-3 gap-8'>
            <Card>
              <CardContent className='pt-6'>
                <DollarSign className='h-12 w-12 text-blue-600 mb-4' />
                <h3 className='text-xl font-bold mb-2'>100% Private Funding</h3>
                <p className='text-gray-600'>
                  We cover all development costs through private investors. Zero
                  financial risk or upfront capital required from your church.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className='pt-6'>
                <Building2 className='h-12 w-12 text-blue-600 mb-4' />
                <h3 className='text-xl font-bold mb-2'>Modular Construction</h3>
                <p className='text-gray-600'>
                  Faster, cost-effective, and sustainable building methods that
                  maximize efficiency and minimize disruption to your church
                  operations.
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardContent className='pt-6'>
                <Home className='h-12 w-12 text-blue-600 mb-4' />
                <h3 className='text-xl font-bold mb-2'>Double-Bottom-Line</h3>
                <p className='text-gray-600'>
                  Shared ownership creates long-term revenue for your church
                  while addressing critical housing needs in your community.
                </p>
              </CardContent>
            </Card>
          </div>
        </div> */}

        {/* How It Works */}
        {/* <div className='bg-blue-50 py-16'>
          <div className='container mx-auto px-4'>
            <h2 className='text-3xl font-bold text-center mb-12'>
              Our Partnership Process
            </h2>
            <div className='max-w-3xl mx-auto space-y-6'>
              {[
                {
                  step: 1,
                  title: 'Submit Your Property',
                  description:
                    'Share your church property details through our streamlined submission platform.',
                },
                {
                  step: 2,
                  title: 'Feasibility Analysis',
                  description:
                    'Our team evaluates zoning, development potential, and financial viability.',
                },
                {
                  step: 3,
                  title: 'Partnership Agreement',
                  description:
                    'We collaborate on development plans and establish shared ownership structure.',
                },
                {
                  step: 4,
                  title: 'Build & Create Impact',
                  description:
                    'We manage modular construction and project delivery. Your church receives ongoing revenue while serving the community.',
                },
              ].map((item) => (
                <div key={item.step} className='flex gap-4 items-start'>
                  <div className='flex-shrink-0 w-12 h-12 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xl'>
                    {item.step}
                  </div>
                  <div>
                    <h3 className='text-xl font-bold mb-1'>{item.title}</h3>
                    <p className='text-gray-600'>{item.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div> */}

        {/* CTA Section */}
        {/* <div className='container mx-auto px-4 py-16'>
          <div className='max-w-2xl mx-auto text-center'>
            <h2 className='text-3xl font-bold mb-4'>
              Ready to Make an Impact?
            </h2>
            <p className='text-xl text-gray-600 mb-8'>
              Partner with us to transform underutilized church land into
              affordable housing. Submit your property to begin the
              conversation.
            </p>
            <Link href='/submit-property'>
              <Button size='lg' className='text-lg px-12'>
                Submit Property Now
              </Button>
            </Link>
          </div>
        </div> */}

        {/* Footer */}
        {/* <footer className='bg-gray-900 text-white py-8'>
          <div className='container mx-auto px-4 text-center'>
            <p>&copy; 2025 Property Intel Inc. All rights reserved.</p>
          </div>
        </footer> */}
      </div>
    </>
  );
}
