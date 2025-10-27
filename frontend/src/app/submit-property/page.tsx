import { MultiStepSubmissionForm } from '@/components/forms/multi-step-submission-form';

export default function SubmitPropertyPage() {
  return (
    <div className='min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50'>
      <div className='mx-auto max-w-5xl px-4 py-12'>
        {/* Header */}
        <div className='mb-8 text-center'>
          <h1 className='text-4xl font-bold text-gray-900'>
            Submit Your Church Property
          </h1>
          <p className='mt-3 text-lg text-gray-600'>
            Complete this form to partner with Logos on affordable housing
            development.
            <br />
            We&apos;ll review your submission and contact you within 5 business days.
          </p>
        </div>

        {/* Form */}
        <MultiStepSubmissionForm />
      </div>
    </div>
  );
}
