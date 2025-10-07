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
        <h2 className='text-2xl font-bold'>Church Information</h2>
        <p className='text-muted-foreground mt-1'>
          Tell us about your church and congregation
        </p>
      </div>

      <div className='space-y-4'>
        {/* Church Name */}
        <FormField
          control={form.control}
          name='church_name'
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                Church Name <span className='text-red-500'>*</span>
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

        {/* Legal Name (optional) */}
        <FormField
          control={form.control}
          name='legal_name'
          render={({ field }) => (
            <FormItem>
              <FormLabel>Legal Name (if different)</FormLabel>
              <FormControl>
                <Input
                  placeholder='e.g., Grace Community Church, Inc.'
                  {...field}
                  value={field.value ?? ''}
                />
              </FormControl>
              <FormDescription>
                The official legal name of your organization
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* 🔥 NEW FIELD: Entity Type (required dropdown) */}
        <FormField
          control={form.control}
          name='entity_type'
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                Entity Type <span className='text-red-500'>*</span>
              </FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder='Select entity type' />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {ENTITY_TYPE_OPTIONS.map((option) => (
                    <SelectItem key={option} value={option}>
                      {option}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormDescription>
                Select the legal structure of your organization
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* 🔥 NEW FIELD: EIN Number (optional masked input) */}
        <FormField
          control={form.control}
          name='ein_number'
          render={({ field }) => (
            <FormItem>
              <FormLabel className='flex items-center gap-2'>
                EIN Number
                <div className='group relative'>
                  <InfoIcon className='h-4 w-4 text-muted-foreground' />
                  <div className='absolute left-0 bottom-full mb-2 hidden group-hover:block w-64 p-2 bg-popover text-popover-foreground text-sm rounded-md shadow-md border z-10'>
                    Employer Identification Number for tax purposes. Format:
                    XX-XXXXXXX (e.g., 12-3456789)
                  </div>
                </div>
              </FormLabel>
              <FormControl>
                <Input
                  placeholder='12-3456789'
                  maxLength={10}
                  {...field}
                  value={field.value ?? ''}
                  onChange={(e) => {
                    // Auto-format EIN as user types
                    let value = e.target.value.replace(/\D/g, '');
                    if (value.length > 2) {
                      value = value.slice(0, 2) + '-' + value.slice(2, 9);
                    }
                    field.onChange(value);
                  }}
                />
              </FormControl>
              <FormDescription>
                Format: XX-XXXXXXX (optional, but helpful for verification)
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* 🔥 NEW FIELD: Website (optional URL input) */}
        <FormField
          control={form.control}
          name='website'
          render={({ field }) => (
            <FormItem>
              <FormLabel>Church Website</FormLabel>
              <FormControl>
                <Input
                  type='url'
                  placeholder='https://yourchurch.org'
                  {...field}
                  value={field.value ?? ''}
                />
              </FormControl>
              <FormDescription>
                Your church&apos;s website (optional)
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Denomination */}
        <FormField
          control={form.control}
          name='denomination'
          render={({ field }) => (
            <FormItem>
              <FormLabel>Denomination</FormLabel>
              <FormControl>
                <Input
                  placeholder='e.g., Baptist, Methodist, Non-denominational'
                  {...field}
                  value={field.value ?? ''}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Founded Year */}
        <FormField
          control={form.control}
          name='founded_year'
          render={({ field }) => (
            <FormItem>
              <FormLabel>Founded Year</FormLabel>
              <FormControl>
                <Input
                  type='number'
                  placeholder='e.g., 1985'
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
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Congregation Size */}
        <FormField
          control={form.control}
          name='congregation_size'
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                Congregation Size <span className='text-red-500'>*</span>
              </FormLabel>
              <Select onValueChange={field.onChange} defaultValue={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder='Select congregation size' />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {CONGREGATION_SIZE_OPTIONS.map((option) => (
                    <SelectItem key={option} value={option}>
                      {option} members
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Annual Budget */}
        <FormField
          control={form.control}
          name='annual_budget'
          render={({ field }) => (
            <FormItem>
              <FormLabel>Annual Budget (optional)</FormLabel>
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
                Your church&apos;s approximate annual budget in dollars
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>

      {/* Contact Information */}
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
                    placeholder='pastor@church.org'
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

      {/* Church Address */}
      <div className='pt-6 border-t'>
        <h3 className='text-lg font-semibold mb-4'>Church Address</h3>
        <div className='space-y-4'>
          <FormField
            control={form.control}
            name='street_address'
            render={({ field }) => (
              <FormItem>
                <FormLabel>
                  Street Address <span className='text-red-500'>*</span>
                </FormLabel>
                <FormControl>
                  <Input
                    placeholder='123 Main Street'
                    {...field}
                    value={field.value ?? ''}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
            <FormField
              control={form.control}
              name='city'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    City <span className='text-red-500'>*</span>
                  </FormLabel>
                  <FormControl>
                    <Input
                      placeholder='Los Angeles'
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
              name='state'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    State <span className='text-red-500'>*</span>
                  </FormLabel>
                  <FormControl>
                    <Input
                      placeholder='CA'
                      maxLength={2}
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
              name='zip_code'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    ZIP Code <span className='text-red-500'>*</span>
                  </FormLabel>
                  <FormControl>
                    <Input
                      placeholder='90001'
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
      </div>
    </div>
  );
}
