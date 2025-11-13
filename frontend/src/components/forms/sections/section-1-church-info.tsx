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
import { ENTITY_TYPE_OPTIONS, CONGREGATION_SIZE_OPTIONS } from '@/types/church';
import { InfoIcon } from 'lucide-react';

interface Section1ChurchInfoProps {
  form: UseFormReturn<ChurchSubmissionFormValues>;
}

/**
 * Section 1: Church Information
 * Includes 3 NEW FIELDS:
 * - entity_type (required dropdown)
 * - ein_number (optional masked input)
 * - website (optional URL input)
 */
export function Section1ChurchInfo({ form }: Section1ChurchInfoProps) {
  return (
    <div className='space-y-6'>
      <div>
        <h2 className='text-2xl font-bold'>Contact Information</h2>
        <p className='text-muted-foreground mt-1'>Tell us about your entity</p>
      </div>

      <div className='space-y-4'>
        {/* Entity Name */}
        <FormField
          control={form.control}
          name='church_name'
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                Entity Name <span className='text-red-500'>*</span>
              </FormLabel>
              <FormControl>
                <Input
                  placeholder='e.g., Grace Community Church'
                  {...field}
                  value={field.value ?? ''}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Entity Type (required dropdown) */}
        <FormField
          control={form.control}
          name='entity_type'
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                Entity Type <span className='text-red-500'>*</span>
              </FormLabel>
              <FormControl>
                <Select
                  onValueChange={field.onChange}
                  value={field.value ?? undefined}
                >
                  <SelectTrigger>
                    <SelectValue placeholder='Select entity type' />
                  </SelectTrigger>
                  <SelectContent>
                    {ENTITY_TYPE_OPTIONS.map((type) => (
                      <SelectItem key={type} value={type}>
                        {type}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Website (optional URL input) */}
        <FormField
          control={form.control}
          name='website'
          render={({ field }) => (
            <FormItem>
              <FormLabel>Website</FormLabel>
              <FormControl>
                <Input
                  type='text'
                  placeholder='e.g., www.yourwebsite.org or yourwebsite.org'
                  {...field}
                  value={field.value ?? ''}
                />
              </FormControl>
              <FormDescription>Your website (optional)</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>

      {/* Primary Contact */}
      <div className='pt-6 border-t'>
        <h3 className='text-lg font-semibold mb-4'>Primary Contact</h3>
        <div className='space-y-4'>
          <FormField
            control={form.control}
            name='primary_contact_name'
            render={({ field }) => (
              <FormItem>
                <FormLabel>
                  Contact Name <span className='text-red-500'>*</span>
                </FormLabel>
                <FormControl>
                  <Input
                    placeholder='e.g., John Smith'
                    {...field}
                    value={field.value ?? ''}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name='primary_contact_email'
            render={({ field }) => (
              <FormItem>
                <FormLabel>
                  Email <span className='text-red-500'>*</span>
                </FormLabel>
                <FormControl>
                  <Input
                    type='email'
                    placeholder='contact@example.org'
                    {...field}
                    value={field.value ?? ''}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name='primary_contact_phone'
            render={({ field }) => (
              <FormItem>
                <FormLabel>
                  Phone <span className='text-red-500'>*</span>
                </FormLabel>
                <FormControl>
                  <Input
                    type='tel'
                    placeholder='(555) 123-4567'
                    {...field}
                    value={field.value ?? ''}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>
      </div>

      {/* Ownership & Financial */}
      <div className='pt-6 border-t'>
        <h3 className='text-lg font-semibold mb-4'>Ownership & Financial</h3>
        <div className='space-y-4'>
          {/* Current as-is Land Value - Owner Reported */}
          <FormField
            control={form.control}
            name='assessed_value'
            render={({ field }) => (
              <FormItem>
                <FormLabel>Owner Reported Current Value</FormLabel>
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
                  Your estimate of the property's current market value
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          {/* Existing Debt Amount */}
          <FormField
            control={form.control}
            name='existing_debt_amount'
            render={({ field }) => (
              <FormItem>
                <FormLabel>Existing Debt Amount</FormLabel>
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
                  Total amount of mortgages, liens, or other debts on the
                  property
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>
      </div>
    </div>
  );
}
