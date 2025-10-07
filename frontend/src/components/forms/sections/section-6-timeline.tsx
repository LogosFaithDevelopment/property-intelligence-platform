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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { churchSubmissionSchema } from '@/lib/validations/submission';
import type { z } from 'zod';

type FormData = z.infer<typeof churchSubmissionSchema>;

interface Section6TimelineProps {
  form: UseFormReturn<FormData>;
}

export function Section6Timeline({ form }: Section6TimelineProps) {
  return (
    <div className='space-y-6'>
      <div>
        <h2 className='text-2xl font-bold text-gray-900'>
          Timeline & Development Preferences
        </h2>
        <p className='mt-1 text-sm text-gray-500'>
          Help us understand your preferences for the development partnership
        </p>
      </div>

      <div className='grid grid-cols-1 gap-6 sm:grid-cols-2'>
        {/* Timeline Preference */}
        <FormField
          control={form.control}
          name='timeline_preference'
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                Preferred Timeline <span className='text-red-500'>*</span>
              </FormLabel>
              <Select
                onValueChange={field.onChange}
                value={field.value ?? undefined}
              >
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder='Select timeline' />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value='6-12 months'>6-12 months</SelectItem>
                  <SelectItem value='12-18 months'>12-18 months</SelectItem>
                  <SelectItem value='18-24 months'>18-24 months</SelectItem>
                  <SelectItem value='24+ months'>24+ months</SelectItem>
                  <SelectItem value='Flexible'>Flexible</SelectItem>
                </SelectContent>
              </Select>
              <FormDescription>
                When would you like to see development begin?
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Preferred Unit Count */}
        <FormField
          control={form.control}
          name='preferred_unit_count'
          render={({ field }) => (
            <FormItem>
              <FormLabel>Preferred Number of Units (Optional)</FormLabel>
              <FormControl>
                <Input
                  type='number'
                  placeholder='e.g., 50'
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
                Do you have a preferred number of affordable housing units?
                (Typically 20-140 units depending on lot size)
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>

      <div className='grid grid-cols-1 gap-6 sm:grid-cols-2'>
        {/* Affordability Target */}
        <FormField
          control={form.control}
          name='affordability_target'
          render={({ field }) => (
            <FormItem>
              <FormLabel>Affordability Target (Optional)</FormLabel>
              <Select
                onValueChange={field.onChange}
                value={field.value ?? undefined}
              >
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder='Select income level' />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value='30% AMI (Extremely Low Income)'>
                    30% AMI (Extremely Low Income)
                  </SelectItem>
                  <SelectItem value='50% AMI (Very Low Income)'>
                    50% AMI (Very Low Income)
                  </SelectItem>
                  <SelectItem value='60% AMI (Low Income)'>
                    60% AMI (Low Income)
                  </SelectItem>
                  <SelectItem value='80% AMI (Moderate Income)'>
                    80% AMI (Moderate Income)
                  </SelectItem>
                  <SelectItem value='Mix of income levels'>
                    Mix of income levels (Recommended)
                  </SelectItem>
                </SelectContent>
              </Select>
              <FormDescription>
                What income level would you like to serve? AMI = Area Median
                Income
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Revenue Sharing Preference */}
        <FormField
          control={form.control}
          name='revenue_sharing_preference'
          render={({ field }) => (
            <FormItem>
              <FormLabel>Revenue Sharing Preference (Optional)</FormLabel>
              <Select
                onValueChange={field.onChange}
                value={field.value ?? undefined}
              >
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder='Select preference' />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value='50/50 split'>
                    50/50 split (Standard)
                  </SelectItem>
                  <SelectItem value='Flexible - open to discussion'>
                    Flexible - open to discussion
                  </SelectItem>
                  <SelectItem value='Church receives fixed annual payment'>
                    Church receives fixed annual payment
                  </SelectItem>
                  <SelectItem value='Church receives % of net income'>
                    Church receives % of net income
                  </SelectItem>
                </SelectContent>
              </Select>
              <FormDescription>
                How would you prefer to structure the revenue sharing?
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>

      {/* Development Involvement Level */}
      <FormField
        control={form.control}
        name='development_involvement_level'
        render={({ field }) => (
          <FormItem>
            <FormLabel>Development Involvement Level (Optional)</FormLabel>
            <Select
              onValueChange={field.onChange}
              value={field.value ?? undefined}
            >
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder='Select involvement level' />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                <SelectItem value='Passive partner (Logos handles everything)'>
                  Passive partner (Logos handles everything)
                </SelectItem>
                <SelectItem value='Active partner (church involved in decisions)'>
                  Active partner (church involved in decisions)
                </SelectItem>
                <SelectItem value='Community oversight (church reviews progress)'>
                  Community oversight (church reviews progress)
                </SelectItem>
              </SelectContent>
            </Select>
            <FormDescription>
              How involved would you like your church to be in the development
              process?
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />
    </div>
  );
}
