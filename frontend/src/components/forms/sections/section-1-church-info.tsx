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
import {
  ENTITY_TYPE_OPTIONS,
  CONGREGATION_SIZE_OPTIONS,
  DENOMINATIONAL_AFFILIATION_OPTIONS,
  BUILDING_CONDITION_OPTIONS,
} from '@/types/church';
import { InfoIcon } from 'lucide-react';
import { Checkbox } from '@/components/ui/checkbox';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';

interface Section1ChurchInfoProps {
  form: UseFormReturn<ChurchSubmissionFormValues>;
}

const SITE_CONDITION_OPTIONS = [
  { value: 'environmental', label: 'Environmental concerns' },
  { value: 'structural', label: 'Structural issues' },
  { value: 'access', label: 'Access or egress problems' },
  { value: 'utility', label: 'Utility infrastructure issues' },
  { value: 'legal', label: 'Legal or title issues' },
];

const EXPLORATION_REASON_OPTIONS = [
  { value: 'declining_membership', label: 'Declining membership' },
  { value: 'financial_challenges', label: 'Financial challenges' },
  { value: 'aging_facility', label: 'Aging facility' },
  { value: 'create_housing', label: 'Desire to create affordable housing' },
  { value: 'utilize_land', label: 'Underutilized land' },
  { value: 'community_impact', label: 'Increase community impact' },
  { value: 'other', label: 'Other' },
];

/**
 * Section 1: Church Information
 * Includes 3 NEW FIELDS:
 * - entity_type (required dropdown)
 * - ein_number (optional masked input)
 * - website (optional URL input)
 * FORM ENHANCEMENT: 6 NEW FIELDS:
 * - denominational_affiliation
 * - member_count
 * - building_condition
 * - site_condition_issues
 * - exploration_reasons
 * - ministries_using_property
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

        {/* Denominational Affiliation */}
        <FormField
          control={form.control}
          name='denominational_affiliation'
          render={({ field }) => (
            <FormItem>
              <FormLabel>Denominational Affiliation</FormLabel>
              <Select
                onValueChange={field.onChange}
                value={field.value ?? undefined}
              >
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder='Select affiliation' />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {DENOMINATIONAL_AFFILIATION_OPTIONS.map((affiliation) => (
                    <SelectItem key={affiliation} value={affiliation}>
                      {affiliation
                        .split('_')
                        .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                        .join(' ')}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormDescription>
                Your church's denomination (optional)
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Member Count */}
        <FormField
          control={form.control}
          name='member_count'
          render={({ field }) => (
            <FormItem>
              <FormLabel>Number of Church Members</FormLabel>
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
                    const val = e.target.value;
                    field.onChange(val === '' ? undefined : Number(val));
                  }}
                />
              </FormControl>
              <FormDescription>
                Approximate number of active members (optional)
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Building Condition */}
        <FormField
          control={form.control}
          name='building_condition'
          render={({ field }) => (
            <FormItem>
              <FormLabel>Current Building Condition</FormLabel>
              <Select
                onValueChange={field.onChange}
                value={field.value ?? undefined}
              >
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder='Select condition' />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {BUILDING_CONDITION_OPTIONS.map((condition) => (
                    <SelectItem key={condition} value={condition}>
                      {condition
                        .split('_')
                        .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                        .join(' ')}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormDescription>
                Overall condition of your building (optional)
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Site Condition Issues */}
        <FormField
          control={form.control}
          name='site_condition_issues'
          render={({ field }) => (
            <FormItem>
              <FormLabel>Site Condition Issues (if any)</FormLabel>
              <FormDescription>
                Select all issues that apply to your property
              </FormDescription>
              <FormControl>
                <Select
                  value={field.value?.[0] || ''}
                  onValueChange={(value) => {
                    const currentValue = field.value || [];
                    if (value && !currentValue.includes(value)) {
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
                    {SITE_CONDITION_OPTIONS.map((item) => {
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
                                currentValue.filter(
                                  (v: string) => v !== item.value,
                                ),
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
                    const item = SITE_CONDITION_OPTIONS.find(
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
          )}
        />

        {/* Exploration Reasons */}
        <FormField
          control={form.control}
          name='exploration_reasons'
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                What inspired you to explore this opportunity?
              </FormLabel>
              <FormDescription>Select all reasons that apply</FormDescription>
              <FormControl>
                <Select
                  value={field.value?.[0] || ''}
                  onValueChange={(value) => {
                    const currentValue = field.value || [];
                    if (value && !currentValue.includes(value)) {
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
                    {EXPLORATION_REASON_OPTIONS.map((item) => {
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
                                currentValue.filter(
                                  (v: string) => v !== item.value,
                                ),
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
                    const item = EXPLORATION_REASON_OPTIONS.find(
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
          )}
        />

        <FormField
          control={form.control}
          name='ministries_using_property'
          render={({ field }) => (
            <FormItem>
              <FormLabel>Current Ministries Using the Property</FormLabel>
              <FormControl>
                <Textarea
                  placeholder='e.g., Sunday worship, youth programs, community food bank, after-school tutoring...'
                  className='min-h-[100px]'
                  {...field}
                  value={field.value ?? ''}
                />
              </FormControl>
              <FormDescription>
                Describe the ministries and activities currently using your
                property (optional)
              </FormDescription>
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
        </div>
      </div>
    </div>
  );
}
