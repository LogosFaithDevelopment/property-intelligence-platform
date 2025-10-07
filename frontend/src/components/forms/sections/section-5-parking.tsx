'use client';

import { UseFormReturn } from 'react-hook-form';
import {
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { churchSubmissionSchema } from '@/lib/validations/submission';
import type { z } from 'zod';

type FormData = z.infer<typeof churchSubmissionSchema>;

interface Section5ParkingProps {
  form: UseFormReturn<FormData>;
}

export function Section5Parking({ form }: Section5ParkingProps) {
  return (
    <div className='space-y-6'>
      <div>
        <h2 className='text-2xl font-bold text-gray-900'>
          Parking & Development Requirements
        </h2>
        <p className='mt-1 text-sm text-gray-500'>
          Help us understand your church's parking needs after development
        </p>
      </div>

      <div className='grid grid-cols-1 gap-6 sm:grid-cols-2'>
        {/* Current Parking Spaces */}
        <FormField
          control={form.control}
          name='current_parking_spaces'
          render={({ field }) => (
            <FormItem>
              <FormLabel>Current Parking Spaces (Optional)</FormLabel>
              <FormControl>
                <Input
                  type='number'
                  placeholder='e.g., 150'
                  {...field}
                  value={
                    field.value === undefined ||
                    field.value === null ||
                    isNaN(field.value)
                      ? ''
                      : String(field.value)
                  }
                  onChange={(e) => {
                    const value = e.target.value;
                    field.onChange(value === '' ? undefined : Number(value));
                  }}
                />
              </FormControl>
              <FormDescription>
                How many parking spaces do you currently have?
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Parking Spaces Needed After Development */}
        <FormField
          control={form.control}
          name='parking_spaces_needed_after'
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                Parking Spaces Needed After Development{' '}
                <span className='text-red-500'>*</span>
              </FormLabel>
              <FormControl>
                <Input
                  type='number'
                  placeholder='e.g., 100'
                  {...field}
                  value={
                    field.value === undefined ||
                    field.value === null ||
                    isNaN(field.value)
                      ? ''
                      : String(field.value)
                  }
                  onChange={(e) => {
                    const value = e.target.value;
                    field.onChange(value === '' ? undefined : Number(value));
                  }}
                />
              </FormControl>
              <FormDescription>
                How many parking spaces will your congregation need after the
                affordable housing development? We'll design the project to
                preserve spaces for your church services.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>

      {/* Special Requirements */}
      <FormField
        control={form.control}
        name='special_requirements'
        render={({ field }) => (
          <FormItem>
            <FormLabel>
              Special Requirements or Considerations (Optional)
            </FormLabel>
            <FormControl>
              <Textarea
                placeholder='Examples:&#10;- Need community room for church programs&#10;- Some units for seniors in congregation&#10;- Preserve existing memorial garden&#10;- Maintain access to church entrance'
                className='min-h-[120px] resize-none'
                {...field}
                value={field.value ?? ''}
              />
            </FormControl>
            <FormDescription>
              Do you have any special requirements, design preferences, or
              considerations we should know about?
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />
    </div>
  );
}
