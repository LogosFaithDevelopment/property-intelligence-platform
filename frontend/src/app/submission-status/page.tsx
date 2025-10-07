'use client';

import { useSubmissionStatus } from '@/hooks/useSubmissions';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { CheckCircle, Clock, XCircle, AlertCircle } from 'lucide-react';

export default function SubmissionStatusPage() {
  const { data: status, isLoading, error } = useSubmissionStatus();

  if (isLoading) {
    return (
      <div className='flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50 px-4 py-12'>
        <div className='text-center'>
          <div className='mb-4 inline-block h-12 w-12 animate-spin rounded-full border-4 border-gray-300 border-t-blue-600'></div>
          <p className='text-gray-600'>Loading submission status...</p>
        </div>
      </div>
    );
  }

  if (error || !status) {
    return (
      <div className='flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50 px-4 py-12'>
        <div className='mx-auto max-w-md text-center'>
          <AlertCircle className='mx-auto mb-4 h-12 w-12 text-yellow-600' />
          <h1 className='mb-4 text-2xl font-bold text-gray-900'>
            No Submission Found
          </h1>
          <p className='mb-6 text-gray-600'>
            We couldn't find a property submission associated with your account.
          </p>
          <Button asChild>
            <Link href='/submit-property'>Submit Your Property</Link>
          </Button>
        </div>
      </div>
    );
  }

  const statusConfig = {
    received: {
      icon: Clock,
      color: 'blue',
      title: 'Submission Received',
      description:
        "We've received your property submission and it's in our queue for review.",
    },
    'under review': {
      icon: Clock,
      color: 'yellow',
      title: 'Under Review',
      description:
        'Our team is currently analyzing your property for development potential.',
    },
    approved: {
      icon: CheckCircle,
      color: 'green',
      title: 'Approved',
      description:
        "Great news! Your property has been approved. We'll contact you shortly to discuss next steps.",
    },
    rejected: {
      icon: XCircle,
      color: 'red',
      title: 'Not Approved',
      description:
        "Unfortunately, your property doesn't meet our current criteria. Thank you for your interest.",
    },
    contacted: {
      icon: CheckCircle,
      color: 'green',
      title: 'Contacted',
      description:
        "We've reached out to discuss your property. Please check your email for details.",
    },
  };

  // Tailwind-safe color class mapping
  const colorClass = {
    blue: {
      bg: 'bg-blue-100',
      icon: 'text-blue-600',
      badge: 'bg-blue-100 text-blue-800',
    },
    yellow: {
      bg: 'bg-yellow-100',
      icon: 'text-yellow-600',
      badge: 'bg-yellow-100 text-yellow-800',
    },
    green: {
      bg: 'bg-green-100',
      icon: 'text-green-600',
      badge: 'bg-green-100 text-green-800',
    },
    red: {
      bg: 'bg-red-100',
      icon: 'text-red-600',
      badge: 'bg-red-100 text-red-800',
    },
  };
  const currentStatus =
    statusConfig[status.status as keyof typeof statusConfig] ||
    statusConfig.received;
  const StatusIcon = currentStatus.icon;
  const color =
    colorClass[currentStatus.color as keyof typeof colorClass] ||
    colorClass.blue;

  return (
    <div className='flex min-h-screen items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-50 px-4 py-12'>
      <div className='mx-auto max-w-2xl'>
        {/* Status Icon */}
        <div className='mb-6 flex justify-center'>
          <div className={`rounded-full ${color.bg} p-6`}>
            <StatusIcon className={`h-16 w-16 ${color.icon}`} />
          </div>
        </div>

        {/* Status Title */}
        <h1 className='mb-4 text-center text-4xl font-bold text-gray-900'>
          {currentStatus.title}
        </h1>

        {/* Status Description */}
        <p className='mb-8 text-center text-lg text-gray-600'>
          {currentStatus.description}
        </p>

        {/* Property Details Card */}
        <div className='mb-8 rounded-lg border border-gray-200 bg-white p-6 shadow-sm'>
          <h2 className='mb-4 text-xl font-semibold text-gray-900'>
            Submission Details
          </h2>
          <dl className='space-y-3'>
            <div className='flex justify-between'>
              <dt className='text-gray-600'>Church Name:</dt>
              <dd className='font-medium text-gray-900'>
                {status.church_name}
              </dd>
            </div>
            <div className='flex justify-between'>
              <dt className='text-gray-600'>Property Address:</dt>
              <dd className='font-medium text-gray-900'>
                {status.property_address}
              </dd>
            </div>
            <div className='flex justify-between'>
              <dt className='text-gray-600'>Submitted:</dt>
              <dd className='font-medium text-gray-900'>
                {new Date(status.submitted_at).toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </dd>
            </div>
            <div className='flex justify-between'>
              <dt className='text-gray-600'>Status:</dt>
              <dd>
                <span
                  className={`inline-flex rounded-full px-3 py-1 text-sm font-semibold ${color.badge}`}
                >
                  {status.status}
                </span>
              </dd>
            </div>
          </dl>
        </div>

        {/* Action Buttons */}
        <div className='flex flex-col gap-3 sm:flex-row sm:justify-center'>
          <Button asChild variant='outline' size='lg'>
            <Link href='/'>Return to Home</Link>
          </Button>
        </div>

        {/* Contact Info */}
        <p className='mt-8 text-center text-sm text-gray-500'>
          Questions about your submission? Contact us at{' '}
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
