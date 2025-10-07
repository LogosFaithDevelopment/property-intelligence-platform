'use client';

import {
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { UseFormReturn } from 'react-hook-form';
import { ChurchSubmissionFormValues } from '@/lib/validations/submission';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertTriangle, CheckCircle } from 'lucide-react';

interface Section3OwnershipProps {
  form: UseFormReturn<ChurchSubmissionFormValues>;
}

/**
 * Section 3: Ownership & Financial
 * CRITICAL SECTION - Determines if property qualifies
 */
export function Section3Ownership({ form }: Section3OwnershipProps) {
  const ownsFreeClear = form.watch('owns_property_free_clear');
  const willingToGroundLease = form.watch('willing_to_ground_lease');
  const hasMortgage = form.watch('has_mortgage');

  // Deal breaker if property is not owned free & clear
  const isDealBreaker = ownsFreeClear === false;
  const showMortgageFields = hasMortgage === true;

  return (
    <div className='space-y-6'>
      <div>
        <h2 className='text-2xl font-bold'>Ownership & Financial</h2>
        <p className='text-muted-foreground mt-1'>
          Property ownership details and financial information
        </p>
      </div>

      {/* CRITICAL QUESTION: Property Owned Free & Clear */}
      <FormField
        control={form.control}
        name='owns_property_free_clear'
        render={({ field }) => (
          <FormItem>
            <FormLabel className='text-lg font-semibold'>
              Does your church own this property free and clear (no mortgage)?
              <span className='text-red-500'> *</span>
            </FormLabel>
            <Select
              onValueChange={(value) => field.onChange(value === 'true')}
              value={
                field.value === undefined ? undefined : String(field.value)
              }
            >
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder='Select an option' />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                <SelectItem value='true'>Yes - Owned free and clear</SelectItem>
                <SelectItem value='false'>
                  No - Has mortgage or liens
                </SelectItem>
              </SelectContent>
            </Select>
            <FormDescription>
              This is a critical requirement for partnership eligibility
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />

      {/* Deal Breaker Alert */}
      {isDealBreaker && (
        <Alert variant='destructive'>
          <AlertTriangle className='h-4 w-4' />
          <AlertDescription className='font-semibold'>
            <strong>Important:</strong> Properties must be owned free and clear
            (no mortgage) to qualify for our partnership program. We recommend
            paying off any existing mortgage before applying.
          </AlertDescription>
        </Alert>
      )}

      {/* Success Indicator */}
      {ownsFreeClear === true && (
        <Alert className='border-green-500 bg-green-50'>
          <CheckCircle className='h-4 w-4 text-green-600' />
          <AlertDescription className='text-green-800'>
            ✅ Great! Your property meets the ownership requirement.
          </AlertDescription>
        </Alert>
      )}

      {/* Has Mortgage? (For information purposes) */}
      <FormField
        control={form.control}
        name='has_mortgage'
        render={({ field }) => (
          <FormItem>
            <FormLabel>Does the property currently have a mortgage?</FormLabel>
            <Select
              onValueChange={(value) => field.onChange(value === 'true')}
              value={
                field.value === undefined ? undefined : String(field.value)
              }
            >
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder='Select an option' />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                <SelectItem value='true'>Yes</SelectItem>
                <SelectItem value='false'>No</SelectItem>
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        )}
      />

      {/* Mortgage Balance (if applicable) */}
      {showMortgageFields && (
        <FormField
          control={form.control}
          name='mortgage_balance'
          render={({ field }) => (
            <FormItem>
              <FormLabel>Current Mortgage Balance</FormLabel>
              <FormControl>
                <Input
                  type='number'
                  placeholder='e.g., 500000'
                  {...field}
                  value={
                    field.value === undefined ||
                    field.value === null ||
                    isNaN(field.value)
                      ? ''
                      : String(field.value)
                  }
                  onChange={(e) => {
                    const val = e.target.value;
                    field.onChange(val === '' ? undefined : Number(val));
                  }}
                />
              </FormControl>
              <FormDescription>
                Approximate balance owed on the mortgage
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
      )}

      {/* Willing to Ground Lease */}
      <FormField
        control={form.control}
        name='willing_to_ground_lease'
        render={({ field }) => (
          <FormItem>
            <FormLabel className='text-lg font-semibold'>
              Is your church willing to ground lease the land to Logos for
              development? <span className='text-red-500'>*</span>
            </FormLabel>
            <Select
              onValueChange={(value) => field.onChange(value === 'true')}
              value={
                field.value === undefined ? undefined : String(field.value)
              }
            >
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder='Select an option' />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                <SelectItem value='true'>
                  Yes - Willing to ground lease
                </SelectItem>
                <SelectItem value='false'>
                  No - Not willing to ground lease
                </SelectItem>
              </SelectContent>
            </Select>
            <FormDescription>
              A ground lease allows Logos to develop the property while you
              retain land ownership and receive ongoing revenue
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />

      {/* Ground Lease Explanation */}
      {willingToGroundLease === true && (
        <Alert className='border-blue-500 bg-blue-50'>
          <CheckCircle className='h-4 w-4 text-blue-600' />
          <AlertDescription className='text-blue-800'>
            <strong>Ground Lease Benefits:</strong>
            <ul className='list-disc ml-5 mt-2 space-y-1'>
              <li>Church retains land ownership</li>
              <li>Logos funds 100% of development costs</li>
              <li>50/50 revenue sharing from rental income</li>
              <li>Church receives ongoing passive income</li>
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {/* Property Assessed Value (Optional) */}
      <FormField
        control={form.control}
        name='assessed_value'
        render={({ field }) => (
          <FormItem>
            <FormLabel>Property Assessed Value (Optional)</FormLabel>
            <FormControl>
              <Input
                type='number'
                placeholder='e.g., 2500000'
                {...field}
                value={
                  field.value === undefined ||
                  field.value === null ||
                  isNaN(field.value)
                    ? ''
                    : String(field.value)
                }
                onChange={(e) => {
                  const val = e.target.value;
                  field.onChange(val === '' ? undefined : Number(val));
                }}
              />
            </FormControl>
            <FormDescription>
              Most recent tax-assessed value (if known). We&apos;ll verify this
              during our evaluation.
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />
    </div>
  );
}
