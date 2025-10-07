import Link from 'next/link';
import { CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';

export default function SubmissionSuccessPage() {
  return (
    <div className='flex min-h-screen items-center justify-center bg-gradient-to-br from-green-50 to-blue-50 px-4 py-12'>
      <div className='mx-auto max-w-2xl text-center'>
        {/* Success Icon */}
        <div className='mb-6 flex justify-center'>
          <div className='rounded-full bg-green-100 p-6'>
            <CheckCircle className='h-16 w-16 text-green-600' />
          </div>
        </div>

        {/* Title */}
        <h1 className='mb-4 text-4xl font-bold text-gray-900'>
          Thank You for Your Submission!
        </h1>

        {/* Description */}
        <p className='mb-6 text-lg text-gray-600'>
          We've received your church property submission and our team will
          review it carefully. You'll receive a confirmation email shortly.
        </p>

        {/* What Happens Next */}
        <div className='mb-8 rounded-lg border border-gray-200 bg-white p-6 text-left shadow-sm'>
          <h2 className='mb-4 text-xl font-semibold text-gray-900'>
            What Happens Next?
          </h2>
          <ol className='space-y-3 text-gray-600'>
            <li className='flex items-start'>
              <span className='mr-3 flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-semibold text-blue-700'>
                1
              </span>
              <span>
                <strong>Confirmation Email:</strong> You'll receive an email
                confirming your submission within a few minutes.
              </span>
            </li>
            <li className='flex items-start'>
              <span className='mr-3 flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-semibold text-blue-700'>
                2
              </span>
              <span>
                <strong>Property Analysis:</strong> Our team will analyze your
                property's suitability for affordable housing development.
              </span>
            </li>
            <li className='flex items-start'>
              <span className='mr-3 flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-semibold text-blue-700'>
                3
              </span>
              <span>
                <strong>Review & Response:</strong> We'll contact you within 5
                business days with next steps or any questions.
              </span>
            </li>
            <li className='flex items-start'>
              <span className='mr-3 flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-blue-100 text-sm font-semibold text-blue-700'>
                4
              </span>
              <span>
                <strong>Partnership Discussion:</strong> If your property
                qualifies, we'll schedule a call to discuss the partnership
                details.
              </span>
            </li>
          </ol>
        </div>

        {/* Action Buttons */}
        <div className='flex flex-col gap-3 sm:flex-row sm:justify-center'>
          <Button asChild size='lg'>
            <Link href='/submission-status'>Check Submission Status</Link>
          </Button>
          <Button asChild variant='outline' size='lg'>
            <Link href='/'>Return to Home</Link>
          </Button>
        </div>

        {/* Contact Info */}
        <p className='mt-8 text-sm text-gray-500'>
          Have questions? Contact us at{' '}
          <a
            href='mailto:partnerships@logos.org'
            className='font-medium text-blue-600 hover:underline'
          >
            partnerships@logos.org
          </a>
        </p>
      </div>
    </div>
  );
}
