'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useRouter } from 'next/navigation';
import { Form } from '@/components/ui/form';
import { Button } from '@/components/ui/button';
import { ArrowLeft, ArrowRight, Check, Save } from 'lucide-react';
import { churchSubmissionSchema } from '@/lib/validations/submission';
import { useSubmitProperty } from '@/hooks/useSubmissions';
import { toast } from 'sonner';
import { Section1ChurchInfo } from './sections/section-1-church-info';
import { Section2PropertyDetails } from './sections/section-2-property-details';
import type { z } from 'zod';

type FormData = z.infer<typeof churchSubmissionSchema>;

// Define which fields belong to each step for validation
const STEP_FIELDS = {
  1: [
    'church_name',
    'entity_type',
    'website',
    'primary_contact_name',
    'primary_contact_email',
    'primary_contact_phone',
    'assessed_value',
    'existing_debt_amount',
  ] as const,
  2: [
    'property_address',
    'property_city',
    'property_state',
    'property_zip_code',
    'lot_size_sqft',
    'build_area_notes',
    'zoning_description',
  ] as const,
};

const STEPS = [
  { id: 1, name: 'Contact Information', component: Section1ChurchInfo },
  { id: 2, name: 'Property Details', component: Section2PropertyDetails },
];

// Utility to clean form data for enums and numbers (matches backend expectations)
function cleanFormDataForSubmission<T extends Record<string, any>>(data: T): T {
  const cleaned: Record<string, any> = {};
  for (const key in data) {
    const value = data[key];

    // Special handling for latitude/longitude - convert empty string to null
    if (key === 'latitude' || key === 'longitude') {
      if (value === '' || value === undefined) {
        cleaned[key] = null;
      } else {
        cleaned[key] = value;
      }
    } else if (typeof value === 'string' && value.trim() === '') {
      cleaned[key] = undefined;
    } else if (typeof value === 'number' && isNaN(value)) {
      cleaned[key] = undefined;
    } else if (value && typeof value === 'object' && !Array.isArray(value)) {
      cleaned[key] = cleanFormDataForSubmission(value);
    } else {
      cleaned[key] = value;
    }
  }
  return cleaned as T;
}

const DRAFT_STORAGE_KEY = 'church-submission-draft';
const DRAFT_STEP_KEY = 'church-submission-step';

export function MultiStepSubmissionForm() {
  const [currentStep, setCurrentStep] = useState(1);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const router = useRouter();
  const { mutate: submitProperty, isPending } = useSubmitProperty();

  const form = useForm<FormData>({
    resolver: zodResolver(churchSubmissionSchema) as any,
    mode: 'onBlur',
    defaultValues: {
      // Church defaults
      church_name: '',
      legal_name: '',
      denomination: '',
      founded_year: undefined,
      entity_type: undefined,
      ein_number: '',
      website: '',
      street_address: '',
      city: '',
      state: '',
      zip_code: '',
      congregation_size: undefined,
      annual_budget: undefined,
      primary_contact_name: '',
      primary_contact_email: '',
      primary_contact_phone: '',
      // Property defaults
      property_address: '',
      property_city: '',
      property_state: '',
      property_zip_code: '',
      demolish_all_structures: false,
      additional_addresses: [],
      latitude: null,
      longitude: null,
      lot_size_sqft: undefined,
      lot_size_acres: undefined,
      current_usage: '',
      zoning_description: '',
      available_build_sqft: undefined,
      build_area_notes: '',
      // Ownership defaults
      owns_property_free_clear: undefined,
      willing_to_ground_lease: undefined,
      has_mortgage: false,
      mortgage_balance: undefined,
      assessed_value: undefined,
      // Phase 2: Deal Breaker defaults
      existing_debt_amount: undefined,
      expects_sanctuary_replacement: undefined,
      sanctuary_replacement_cost_estimate: undefined,
      // Approval defaults
      congregation_voted: undefined,
      vote_percentage: undefined,
      leadership_support: undefined,
      denomination_approval_needed: undefined,
      // Phase 3: Partnership Quality defaults
      decision_making_authority: undefined,
      decision_timeline: undefined,
      accepts_60_40_ownership: undefined,
      willing_to_pay_deposit: undefined,
      // Parking defaults
      current_parking_spaces: undefined,
      parking_spaces_needed_after: undefined,
      special_requirements: '',
      // Timeline defaults
      timeline_preference: undefined,
      preferred_unit_count: undefined,
      affordability_target: undefined,
      revenue_sharing_preference: undefined,
      development_involvement_level: undefined,
    },
  });

  const CurrentStepComponent =
    STEPS.find((step) => step.id === currentStep)?.component ||
    Section1ChurchInfo;

  // Load saved draft on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const savedDraft = localStorage.getItem(DRAFT_STORAGE_KEY);
      const savedStep = localStorage.getItem(DRAFT_STEP_KEY);

      if (savedDraft) {
        try {
          const parsedDraft = JSON.parse(savedDraft);
          // Reset form with saved data
          form.reset(parsedDraft);
          toast.info('Draft loaded! Continue where you left off.');
          console.log('✅ Loaded draft from localStorage:', parsedDraft);
        } catch (error) {
          console.error('❌ Failed to load draft:', error);
          localStorage.removeItem(DRAFT_STORAGE_KEY);
        }
      }

      if (savedStep) {
        const step = parseInt(savedStep, 10);
        if (step >= 1 && step <= STEPS.length) {
          setCurrentStep(step);
        }
      }
    }
  }, []); // Only run on mount

  // Save draft whenever form data changes
  useEffect(() => {
    const subscription = form.watch((data) => {
      if (typeof window !== 'undefined') {
        // Save to localStorage
        localStorage.setItem(DRAFT_STORAGE_KEY, JSON.stringify(data));
        localStorage.setItem(DRAFT_STEP_KEY, currentStep.toString());
        setLastSaved(new Date());
        console.log('💾 Draft auto-saved');
      }
    });

    return () => subscription.unsubscribe();
  }, [form, currentStep]);

  // Function to clear draft
  const clearDraft = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(DRAFT_STORAGE_KEY);
      localStorage.removeItem(DRAFT_STEP_KEY);
      console.log('🗑️ Draft cleared');
    }
  };

  const handleNext = async () => {
    console.log(
      `⏭️ handleNext called - Current step: ${currentStep} of ${STEPS.length}`
    );

    // Get the fields for the current step
    const fieldsToValidate =
      STEP_FIELDS[currentStep as keyof typeof STEP_FIELDS];

    // Debug: Log current form values before validation
    const currentValues = form.getValues();
    console.log('🔍 Current form values before validation:', currentValues);
    console.log('🔍 Fields to validate:', fieldsToValidate);
    console.log(
      '🔍 lot_size_sqft value:',
      currentValues.lot_size_sqft,
      'Type:',
      typeof currentValues.lot_size_sqft
    );
    console.log(
      '🔍 lot_size_acres value:',
      currentValues.lot_size_acres,
      'Type:',
      typeof currentValues.lot_size_acres
    );

    // Validate only the current step's fields
    const isValid = await form.trigger(fieldsToValidate);

    if (isValid) {
      if (currentStep < STEPS.length) {
        console.log(
          `✅ Validation passed - Advancing from step ${currentStep} to ${
            currentStep + 1
          }`
        );
        setIsTransitioning(true);
        setCurrentStep((prev) => prev + 1);
        window.scrollTo({ top: 0, behavior: 'smooth' });
        // Clear transition flag after a brief delay
        setTimeout(() => setIsTransitioning(false), 300);
      } else {
        console.log(`⚠️ Already on last step (${currentStep}), not advancing`);
      }
    } else {
      // Get the errors for better feedback
      const errors = form.formState.errors;
      const errorFields = Object.keys(errors);
      const firstError = errorFields[0];

      // Debug: Log all errors
      console.error('❌ Validation errors:', errors);
      console.error('❌ Error fields:', errorFields);

      if (firstError && errors[firstError as keyof typeof errors]) {
        const errorMessage = errors[firstError as keyof typeof errors]?.message;
        toast.error(
          (errorMessage as string) || 'Please check the form and fix any errors'
        );
      } else {
        toast.error('Please complete all required fields before continuing');
      }

      // Focus the first field with an error
      if (firstError) {
        const element = document.getElementsByName(firstError)[0];
        if (element) {
          element.focus();
          element.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep((prev) => prev - 1);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const onSubmit = async (data: FormData) => {
    console.log('🚀 Form submission started');
    console.log('📝 Form data:', data);

    // Force-fix latitude/longitude if they're empty strings (React Hook Form bug)
    const fixedData = { ...data };
    // TypeScript doesn't know that React Hook Form might store these as strings at runtime
    if (
      (fixedData.latitude as any) === '' ||
      fixedData.latitude === undefined
    ) {
      fixedData.latitude = null;
    }
    if (
      (fixedData.longitude as any) === '' ||
      fixedData.longitude === undefined
    ) {
      fixedData.longitude = null;
    }

    // Normalize website URL - add https:// if missing
    if (fixedData.website && typeof fixedData.website === 'string') {
      const website = fixedData.website.trim();
      if (
        website &&
        !website.startsWith('http://') &&
        !website.startsWith('https://')
      ) {
        fixedData.website = `https://${website}`;
      }
    }

    console.log('🔧 Fixed data:', fixedData);

    // Clean data before submit to avoid "" for enums/optionals
    const cleaned = cleanFormDataForSubmission(
      fixedData
    ) as import('@/types/church').ChurchSubmissionFormData;

    console.log('✅ Cleaned data for submission:', cleaned);

    submitProperty(cleaned, {
      onSuccess: (response) => {
        console.log('✅ Submission successful! Response:', response);
        toast.success('Property submitted successfully!');
        // Clear the draft after successful submission
        clearDraft();
        // Add a small delay to ensure toast is visible before navigation
        setTimeout(() => {
          router.push('/submission-success');
        }, 500);
      },
      onError: (error: any) => {
        console.error('❌ Submission error:', error);
        console.error('❌ Error response:', error.response);
        console.error('❌ Error details:', error.response?.data);

        const errorMessage =
          error.response?.data?.detail ||
          error.response?.data?.message ||
          error.message ||
          'Failed to submit property. Please try again.';

        toast.error(errorMessage);
      },
    });
  };

  return (
    <div className='mx-auto max-w-4xl px-4 py-8'>
      {/* Draft Status Indicator */}
      {lastSaved && (
        <div className='mb-4 flex items-center justify-end gap-2 text-sm text-gray-500'>
          <Save className='h-4 w-4 text-green-600' />
          <span>Draft saved at {lastSaved.toLocaleTimeString()}</span>
        </div>
      )}

      {/* Stepper */}
      <div className='mb-8'>
        <div className='flex items-start justify-between gap-2'>
          {STEPS.map((step, index) => (
            <div key={step.id} className='flex flex-1 items-start min-w-0'>
              <div className='flex flex-col items-center w-full px-1'>
                {/* Circle */}
                <div
                  className={`flex h-10 w-10 items-center justify-center rounded-full border-2 transition-colors flex-shrink-0 ${
                    currentStep > step.id
                      ? 'border-green-500 bg-green-500 text-white'
                      : currentStep === step.id
                      ? 'border-blue-500 bg-blue-500 text-white'
                      : 'border-gray-300 bg-white text-gray-500'
                  }`}
                >
                  {currentStep > step.id ? (
                    <Check className='h-5 w-5' />
                  ) : (
                    <span className='text-sm font-semibold'>{step.id}</span>
                  )}
                </div>
                {/* Label */}
                <span
                  className={`mt-2 text-xs font-medium text-center w-full leading-tight ${
                    currentStep >= step.id ? 'text-gray-900' : 'text-gray-500'
                  }`}
                  style={{ wordBreak: 'break-word' }}
                >
                  {step.name}
                </span>
              </div>
              {/* Connector Line */}
              {index < STEPS.length - 1 && (
                <div
                  className={`mx-2 h-0.5 flex-1 transition-colors self-start ${
                    currentStep > step.id ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                  style={{ marginTop: '20px' }}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Progress Bar */}
      <div className='mb-6'>
        <div className='flex items-center justify-between text-sm text-gray-600'>
          <span>
            Step {currentStep} of {STEPS.length}
          </span>
          <span>
            {Math.round(((currentStep - 1) / STEPS.length) * 100)}% Complete
          </span>
        </div>
        <div className='mt-2 h-2 w-full overflow-hidden rounded-full bg-gray-200'>
          <div
            className='h-full bg-blue-500 transition-all duration-300'
            style={{ width: `${((currentStep - 1) / STEPS.length) * 100}%` }}
          />
        </div>
      </div>

      {/* Form */}
      <Form {...form}>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            console.log(
              `📝 Form onSubmit triggered - Current step: ${currentStep} of ${STEPS.length}, isTransitioning: ${isTransitioning}`
            );

            // PREVENT submission if we're transitioning between steps
            if (isTransitioning) {
              console.log('🚫 Ignoring submit during transition');
              return;
            }

            // Only allow submission if on the last step
            if (currentStep === STEPS.length) {
              console.log('✅ On last step - submitting form');
              const data = form.getValues();
              onSubmit(data);
            } else {
              console.log(
                `⏭️ Not on last step (step ${currentStep}) - calling handleNext instead`
              );
              // If not on last step, treat it like clicking Next button
              handleNext();
            }
          }}
          className='space-y-8'
        >
          <div className='rounded-lg border bg-white p-6 shadow-sm'>
            <CurrentStepComponent form={form as any} />
          </div>

          {/* Navigation Buttons */}
          <div className='flex items-center justify-between'>
            <Button
              type='button'
              variant='outline'
              onClick={handlePrevious}
              disabled={currentStep === 1}
            >
              <ArrowLeft className='mr-2 h-4 w-4' />
              Previous
            </Button>

            <div className='text-sm text-gray-500'>
              Step {currentStep} of {STEPS.length}
            </div>

            {currentStep < STEPS.length ? (
              <Button type='button' onClick={handleNext}>
                Next
                <ArrowRight className='ml-2 h-4 w-4' />
              </Button>
            ) : (
              <Button type='submit' disabled={isPending}>
                {isPending ? 'Submitting...' : 'Submit Property'}
              </Button>
            )}
          </div>
        </form>
      </Form>
    </div>
  );
}
