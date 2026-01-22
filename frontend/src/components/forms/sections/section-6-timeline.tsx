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
import { Checkbox } from '@/components/ui/checkbox';
import { Badge } from '@/components/ui/badge';
import { churchSubmissionSchema } from '@/lib/validations/submission';
import {
  PARTNERSHIP_STRUCTURE_OPTIONS,
  DECISION_AUTHORITY_OPTIONS,
  TIMELINE_PREFERENCE_NEW_OPTIONS,
} from '@/types/church';
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

      {/* FORM ENHANCEMENT: Partnership Structure */}
      <div className='pt-6 border-t'>
        <h3 className='text-lg font-semibold mb-4'>Partnership Structure</h3>

        {/* Partnership Structure Preferences */}
        <FormField
          control={form.control}
          name='partnership_structure_preferences'
          render={() => (
            <FormItem>
              <FormLabel>Preferred Partnership Structure(s)</FormLabel>
              <FormDescription>
                Select all structures you'd be open to considering
              </FormDescription>
              <div className='space-y-2 mt-3'>
                {[
                  {
                    value: 'ground_lease' as const,
                    label: 'Ground Lease',
                    description:
                      'Church retains land ownership, leases to developer',
                  },
                  {
                    value: 'limited_partnership' as const,
                    label: 'Limited Partnership',
                    description: 'Church becomes equity partner in development',
                  },
                  {
                    value: 'fee_development' as const,
                    label: 'Fee Development',
                    description: 'Church sells land, receives development fee',
                  },
                  {
                    value: 'unsure' as const,
                    label: 'Unsure / Open to Discussion',
                    description: 'Open to exploring different options',
                  },
                ].map((item) => (
                  <FormField
                    key={item.value}
                    control={form.control}
                    name='partnership_structure_preferences'
                    render={({ field }) => {
                      const currentValue = field.value || [];
                      return (
                        <FormItem
                          key={item.value}
                          className='flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4'
                        >
                          <FormControl>
                            <Checkbox
                              checked={currentValue.includes(item.value)}
                              onCheckedChange={(checked: boolean) => {
                                const newValue = checked
                                  ? [...currentValue, item.value]
                                  : currentValue.filter(
                                      (value: string) => value !== item.value,
                                    );
                                field.onChange(newValue);
                              }}
                            />
                          </FormControl>
                          <div className='space-y-1 leading-none'>
                            <FormLabel className='font-medium cursor-pointer'>
                              \n {item.label}
                            </FormLabel>
                            <FormDescription className='text-sm'>
                              {item.description}
                            </FormDescription>
                          </div>
                        </FormItem>
                      );
                    }}
                  />
                ))}
              </div>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Decision Making Structure */}
        <FormField
          control={form.control}
          name='decision_making_structure'
          render={({ field }) => {
            const DECISION_MAKERS = [
              { value: 'pastor' as const, label: 'Pastor' },
              { value: 'board' as const, label: 'Board of Directors/Trustees' },
              { value: 'congregation' as const, label: 'Congregation Vote' },
              {
                value: 'denomination' as const,
                label: 'Denominational Approval',
              },
            ];
            return (
              <FormItem className='mt-6'>
                <FormLabel>Who Makes Final Decisions?</FormLabel>
                <FormDescription>
                  Select all parties involved in decision-making
                </FormDescription>
                <FormControl>
                  <Select
                    value={field.value?.[0] || ''}
                    onValueChange={(value) => {
                      const currentValue = field.value || [];
                      if (value && !currentValue.includes(value as any)) {
                        field.onChange([...currentValue, value]);
                      }
                    }}
                  >
                    <SelectTrigger className='h-10'>
                      <SelectValue placeholder='Make a selection'>
                        {field.value && field.value.length > 0
                          ? `${field.value.length} selected`
                          : 'Make a selection'}
                      </SelectValue>
                    </SelectTrigger>
                    <SelectContent>
                      {DECISION_MAKERS.map((item) => {
                        const isSelected = field.value?.includes(item.value);
                        return (
                          <SelectItem
                            key={item.value}
                            value={item.value}
                            className={isSelected ? 'bg-accent' : ''}
                            onSelect={(e) => {
                              e.preventDefault();
                              const currentValue = field.value || [];
                              if (isSelected) {
                                field.onChange(
                                  currentValue.filter((v) => v !== item.value),
                                );
                              } else {
                                field.onChange([...currentValue, item.value]);
                              }
                            }}
                          >
                            {item.label}
                          </SelectItem>
                        );
                      })}
                    </SelectContent>
                  </Select>
                </FormControl>
                {field.value && field.value.length > 0 && (
                  <div className='flex flex-wrap gap-1 mt-2'>
                    {field.value.map((value: string) => {
                      const item = DECISION_MAKERS.find(
                        (opt) => opt.value === value,
                      );
                      return (
                        <Badge
                          key={value}
                          variant='secondary'
                          className='text-xs'
                        >
                          {item?.label}
                          <button
                            type='button'
                            onClick={() => {
                              field.onChange(
                                field.value.filter((v: string) => v !== value),
                              );
                            }}
                            className='ml-1 hover:text-destructive'
                          >
                            ×
                          </button>
                        </Badge>
                      );
                    })}
                  </div>
                )}
                <FormMessage />
              </FormItem>
            );
          }}
        />

        {/* Timeline Preference (New - More Specific) */}
        <FormField
          control={form.control}
          name='timeline_preference_new'
          render={({ field }) => (
            <FormItem className='mt-6'>
              <FormLabel>Preferred Decision Timeline</FormLabel>
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
                  <SelectItem value='0_6_months'>0-6 months</SelectItem>
                  <SelectItem value='6_12_months'>6-12 months</SelectItem>
                  <SelectItem value='12_plus_months'>12+ months</SelectItem>
                </SelectContent>
              </Select>
              <FormDescription>
                How soon are you ready to make a decision on partnership?
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Reinvestment Preference */}
        <FormField
          control={form.control}
          name='reinvestment_preference'
          render={({ field }) => (
            <FormItem className='mt-6'>
              <FormLabel>Reinvestment Preference</FormLabel>
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
                  <SelectItem value='maximize_church_share'>
                    Maximize church financial return
                  </SelectItem>
                  <SelectItem value='maximize_affordable_housing'>
                    Maximize affordable housing impact
                  </SelectItem>
                  <SelectItem value='balance_both'>
                    Balance both priorities
                  </SelectItem>
                </SelectContent>
              </Select>
              <FormDescription>
                What's most important to your church in this partnership?
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>
    </div>
  );
}
