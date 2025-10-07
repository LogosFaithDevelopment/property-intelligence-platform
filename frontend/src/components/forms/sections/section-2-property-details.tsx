'use client';

import { useState } from 'react';
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
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { UseFormReturn } from 'react-hook-form';
import { ChurchSubmissionFormValues } from '@/lib/validations/submission';
import { InfoIcon, AlertTriangle, Loader2, CheckCircle2 } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useToast } from '@/hooks/use-toast';
import { fetchPropertyDataByAddress } from '@/lib/api/property-data';

interface Section2PropertyDetailsProps {
  form: UseFormReturn<ChurchSubmissionFormValues>;
}

/**
 * Section 2: Property Details
 * Includes 2 NEW FIELDS:
 * - available_build_sqft (optional number)
 * - build_area_notes (optional textarea)
 *
 * Features auto-fetch from LA County API with manual override support
 */
export function Section2PropertyDetails({
  form,
}: Section2PropertyDetailsProps) {
  const { toast } = useToast();
  const [isFetching, setIsFetching] = useState(false);
  const [autoFilledFields, setAutoFilledFields] = useState<Set<string>>(
    new Set()
  );
  const [fetchAttempted, setFetchAttempted] = useState(false);

  const lotSize = form.watch('lot_size_sqft');
  const availableBuildSpace = form.watch('available_build_sqft');
  const propertyAddress = form.watch('property_address');
  const propertyCity = form.watch('property_city');
  const propertyState = form.watch('property_state');
  const propertyZip = form.watch('property_zip_code');

  // Check if available build space is less than total lot
  const hasConstraints =
    lotSize && availableBuildSpace && availableBuildSpace < lotSize;

  // Handler to fetch property data from LA County API
  const handleFetchPropertyData = async () => {
    if (!propertyAddress || !propertyCity || !propertyState || !propertyZip) {
      toast({
        title: 'Missing Address Information',
        description:
          'Please fill in all address fields before fetching property data.',
        variant: 'destructive',
      });
      return;
    }

    setIsFetching(true);
    setFetchAttempted(true);

    try {
      const response = await fetchPropertyDataByAddress({
        address: propertyAddress,
        city: propertyCity,
        state: propertyState,
        zipCode: propertyZip,
      });

      if (response.success && response.data) {
        const newAutoFilledFields = new Set<string>();

        // Only auto-fill if the field is currently empty (manual entries take precedence)
        if (!form.getValues('lot_size_sqft') && response.data.lot_size_sqft) {
          // Ensure we're setting numbers, not strings
          const lotSizeSqft = Number(response.data.lot_size_sqft);
          const lotSizeAcres =
            Number(response.data.lot_size_acres) || lotSizeSqft / 43560;

          console.log(
            '🔍 Auto-fetch setting lot_size_sqft:',
            lotSizeSqft,
            'Type:',
            typeof lotSizeSqft
          );
          console.log(
            '🔍 Auto-fetch setting lot_size_acres:',
            lotSizeAcres,
            'Type:',
            typeof lotSizeAcres
          );

          form.setValue('lot_size_sqft', lotSizeSqft, { shouldValidate: true });
          form.setValue('lot_size_acres', lotSizeAcres, {
            shouldValidate: true,
          });
          newAutoFilledFields.add('lot_size_sqft');

          // Verify what was actually set
          console.log(
            '✅ After setValue - lot_size_sqft:',
            form.getValues('lot_size_sqft'),
            'Type:',
            typeof form.getValues('lot_size_sqft')
          );
          console.log(
            '✅ After setValue - lot_size_acres:',
            form.getValues('lot_size_acres'),
            'Type:',
            typeof form.getValues('lot_size_acres')
          );
        }

        // Use use_type or classification for zoning description
        if (
          !form.getValues('zoning_description') &&
          (response.data.use_type || response.data.classification)
        ) {
          const zoningInfo =
            response.data.use_type || response.data.classification;
          form.setValue('zoning_description', zoningInfo);
          newAutoFilledFields.add('zoning_description');
        }

        setAutoFilledFields(newAutoFilledFields);

        toast({
          title: 'Property Data Fetched',
          description: `Auto-filled ${newAutoFilledFields.size} field(s) from LA County Assessor.`,
          duration: 5000,
        });
      } else {
        // Handle different error types
        const errorMessage =
          response.error === 'not_la_county'
            ? response.message ||
              'Property data auto-fill is only available for Los Angeles County addresses.'
            : response.error === 'not_found'
            ? 'Property not found in LA County records. Please enter details manually.'
            : 'Failed to fetch property data. Please enter details manually.';

        toast({
          title:
            response.error === 'not_la_county'
              ? 'Not LA County'
              : 'Property Not Found',
          description: errorMessage,
          variant:
            response.error === 'not_la_county' ? 'default' : 'destructive',
          duration: 7000,
        });
      }
    } catch (error) {
      console.error('Error fetching property data:', error);
      toast({
        title: 'Error',
        description:
          'An error occurred while fetching property data. Please try again or enter details manually.',
        variant: 'destructive',
      });
    } finally {
      setIsFetching(false);
    }
  };

  // Track when user manually edits an auto-filled field
  const handleFieldEdit = (fieldName: string) => {
    if (autoFilledFields.has(fieldName)) {
      setAutoFilledFields((prev) => {
        const updated = new Set(prev);
        updated.delete(fieldName);
        return updated;
      });
    }
  };

  // Warning if build space is small
  const showWarning = availableBuildSpace && availableBuildSpace < 10000;

  return (
    <div className='space-y-6'>
      <div>
        <h2 className='text-2xl font-bold'>Property Details</h2>
        <p className='text-muted-foreground mt-1'>
          Information about the property you&apos;re proposing for development
        </p>
      </div>

      <div className='space-y-4'>
        {/* Property Address */}
        <FormField
          control={form.control}
          name='property_address'
          render={({ field }) => (
            <FormItem>
              <FormLabel>
                Property Address <span className='text-red-500'>*</span>
              </FormLabel>
              <FormControl>
                <Input
                  placeholder='123 Church Lane, Los Angeles, CA 90001'
                  {...field}
                  value={field.value ?? ''}
                />
              </FormControl>
              <FormDescription>
                Full address of the property to be developed
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
          <FormField
            control={form.control}
            name='property_city'
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
            name='property_state'
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
            name='property_zip_code'
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

        {/* Auto-Fetch Property Data Button */}
        <div className='flex items-center gap-4 p-4 border rounded-lg bg-muted/50'>
          <div className='flex-1'>
            <h3 className='text-sm font-semibold mb-1'>
              Auto-Fill Property Details
            </h3>
            <p className='text-xs text-muted-foreground'>
              For LA County properties, we can automatically fetch lot size and
              zoning information from public records.
            </p>
          </div>
          <Button
            type='button'
            onClick={handleFetchPropertyData}
            disabled={
              isFetching ||
              !propertyAddress ||
              !propertyCity ||
              !propertyState ||
              !propertyZip
            }
            variant='outline'
            className='shrink-0'
          >
            {isFetching ? (
              <>
                <Loader2 className='mr-2 h-4 w-4 animate-spin' />
                Fetching...
              </>
            ) : fetchAttempted && autoFilledFields.size > 0 ? (
              <>
                <CheckCircle2 className='mr-2 h-4 w-4 text-green-600' />
                Fetched
              </>
            ) : (
              'Fetch Property Data'
            )}
          </Button>
        </div>

        {/* Lot Size */}
        <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
          <FormField
            control={form.control}
            name='lot_size_sqft'
            render={({ field }) => (
              <FormItem>
                <FormLabel className='flex items-center gap-2'>
                  Total Lot Size (sq ft)
                  {autoFilledFields.has('lot_size_sqft') && (
                    <Badge variant='secondary' className='text-xs'>
                      <CheckCircle2 className='mr-1 h-3 w-3' />
                      Auto-filled
                    </Badge>
                  )}
                </FormLabel>
                <FormControl>
                  <Input
                    type='number'
                    placeholder='e.g., 50000'
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
                      const numValue = val === '' ? undefined : Number(val);
                      field.onChange(numValue);
                      handleFieldEdit('lot_size_sqft');
                      // Auto-calculate acres
                      if (val !== '' && numValue !== undefined) {
                        form.setValue('lot_size_acres', numValue / 43560);
                      }
                    }}
                  />
                </FormControl>
                <FormDescription>
                  If known, enter total property size in square feet
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name='lot_size_acres'
            render={({ field }) => (
              <FormItem>
                <FormLabel>Lot Size (acres)</FormLabel>
                <FormControl>
                  <Input
                    type='number'
                    step='0.01'
                    placeholder='Calculated automatically'
                    {...field}
                    disabled
                    value={field.value?.toFixed(2) || ''}
                  />
                </FormControl>
                <FormDescription>Calculated from square feet</FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {/* 🔥 NEW FIELD: Available Build Space (optional) */}
        <FormField
          control={form.control}
          name='available_build_sqft'
          render={({ field }) => (
            <FormItem>
              <FormLabel className='flex items-center gap-2'>
                Available Build Space (sq ft)
                <div className='group relative'>
                  <InfoIcon className='h-4 w-4 text-muted-foreground' />
                  <div className='absolute left-0 bottom-full mb-2 hidden group-hover:block w-80 p-3 bg-popover text-popover-foreground text-sm rounded-md shadow-md border z-10'>
                    <p className='font-semibold mb-2'>
                      When to use this field:
                    </p>
                    <p className='mb-2'>
                      If only part of your property can be developed (e.g.,
                      existing building, parking, memorial garden), enter the
                      buildable area here.
                    </p>
                    <p className='text-xs text-muted-foreground'>
                      Example: Total lot 50,000 sqft, but 20,000 sqft has
                      existing church building, so available = 30,000 sqft
                    </p>
                  </div>
                </div>
              </FormLabel>
              <FormControl>
                <Input
                  type='number'
                  placeholder='Leave blank if entire lot is available'
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
                Only fill this if the buildable area is less than total lot size
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Show helpful info when available build space differs from lot size */}
        {hasConstraints && (
          <Alert>
            <InfoIcon className='h-4 w-4' />
            <AlertDescription>
              Using {availableBuildSpace?.toLocaleString()} sqft for buildable
              area instead of total lot size ({lotSize?.toLocaleString()} sqft).
              This will be used to calculate unit capacity.
            </AlertDescription>
          </Alert>
        )}

        {/* Warning if build space is small */}
        {showWarning && (
          <Alert variant='destructive'>
            <AlertTriangle className='h-4 w-4' />
            <AlertDescription>
              Warning: Build space less than 10,000 sqft may not meet the
              minimum requirement for 40+ units
            </AlertDescription>
          </Alert>
        )}

        {/* 🔥 NEW FIELD: Build Area Notes (optional textarea) */}
        <FormField
          control={form.control}
          name='build_area_notes'
          render={({ field }) => (
            <FormItem>
              <FormLabel>Build Area Notes</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Describe any constraints or special considerations (e.g., 'Southeast corner available', 'Preserve existing memorial garden', 'Parking lot can be redeveloped')"
                  rows={4}
                  maxLength={500}
                  {...field}
                  value={field.value ?? ''}
                />
              </FormControl>
              <FormDescription>
                {field.value?.length || 0}/500 characters - Explain any site
                constraints or areas to preserve
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Current Usage */}
        <FormField
          control={form.control}
          name='current_usage'
          render={({ field }) => (
            <FormItem>
              <FormLabel>Current Property Usage</FormLabel>
              <FormControl>
                <Input
                  placeholder='e.g., Vacant land, Parking lot, Old building'
                  {...field}
                  value={field.value ?? ''}
                />
              </FormControl>
              <FormDescription>
                What is the property currently being used for?
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Zoning */}
        <FormField
          control={form.control}
          name='zoning_description'
          render={({ field }) => (
            <FormItem>
              <FormLabel className='flex items-center gap-2'>
                Zoning (if known)
                {autoFilledFields.has('zoning_description') && (
                  <Badge variant='secondary' className='text-xs'>
                    <CheckCircle2 className='mr-1 h-3 w-3' />
                    Auto-filled
                  </Badge>
                )}
              </FormLabel>
              <FormControl>
                <Input
                  placeholder='e.g., R3, C2, or leave blank if unknown'
                  {...field}
                  value={field.value ?? ''}
                  onChange={(e) => {
                    field.onChange(e);
                    handleFieldEdit('zoning_description');
                  }}
                />
              </FormControl>
              <FormDescription>
                Property zoning designation (we&apos;ll verify this)
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Coordinates - Will be set by map picker later (no hidden inputs needed) */}
      </div>
    </div>
  );
}
