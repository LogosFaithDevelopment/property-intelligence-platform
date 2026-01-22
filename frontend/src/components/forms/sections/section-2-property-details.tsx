'use client';

import { useState, useEffect } from 'react';
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
  InfoIcon,
  AlertTriangle,
  Loader2,
  CheckCircle2,
  Plus,
} from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { toast } from 'sonner';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { fetchPropertyDataByAddress } from '@/lib/api/property-data';

import { Checkbox } from '@/components/ui/checkbox';

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
  const [isFetching, setIsFetching] = useState(false);
  const [showFormatDialog, setShowFormatDialog] = useState(false);
  const [autoFilledFields, setAutoFilledFields] = useState<Set<string>>(
    new Set(),
  );
  const [fetchAttempted, setFetchAttempted] = useState(false);
  const [parcelInfo, setParcelInfo] = useState<{
    lot_numbers?: string;
    parcel_number?: string;
  } | null>(null);
  const [isMounted, setIsMounted] = useState(false);
  const [additionalAddressErrors, setAdditionalAddressErrors] = useState<
    Map<number, string>
  >(new Map());

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const propertyAddress = form.watch('property_address');
  const propertyCity = form.watch('property_city');
  const propertyState = form.watch('property_state');
  const propertyZip = form.watch('property_zip_code');

  // Handler to fetch property data from LA County API (including additional addresses)
  const handleFetchPropertyData = async () => {
    if (!propertyAddress || !propertyCity || !propertyState || !propertyZip) {
      toast.error(
        'Please fill in all address fields before fetching property data.',
      );
      return;
    }

    setIsFetching(true);
    setFetchAttempted(true);

    try {
      // Fetch PRIMARY address
      const response = await fetchPropertyDataByAddress({
        address: propertyAddress,
        city: propertyCity,
        state: propertyState,
        zipCode: propertyZip,
      });

      if (!response.success || !response.data) {
        const errorMsg = response.error || 'unknown';
        const primaryAddressStr = `${propertyAddress}, ${propertyCity}`;

        if (errorMsg === 'not_found') {
          toast.error(
            `Primary address not found: ${primaryAddressStr}. Property data not available - please verify address or enter manually.`,
          );
        } else if (errorMsg === 'not_la_county') {
          toast.error(
            `${propertyCity} may not be in LA County. Property data auto-fill only works for LA County addresses. Please enter details manually.`,
          );
        } else if (errorMsg === 'no_data_source') {
          toast.error(
            `Property data not available for ${propertyState}. Please enter details manually.`,
          );
        } else {
          toast.error(
            `Could not fetch property data for: ${primaryAddressStr}. Please enter details manually.`,
          );
        }

        setIsFetching(false);
        return;
      }

      // Store primary lot size
      let totalLotSqft = Number(response.data.lot_size_sqft) || 0;
      let totalLotAcres =
        Number(response.data.lot_size_acres) || totalLotSqft / 43560;
      let totalBuildingSqft = Number(response.data.building_size_sqft) || 0;

      // Store primary parcel info
      const allParcelInfo = {
        lot_numbers: response.data.lot_numbers || '',
        parcel_number: response.data.parcel_number || '',
      };

      console.log(
        `🏠 Primary address: ${totalLotSqft} sqft lot, ${totalBuildingSqft} sqft building`,
      );

      // Fetch ADDITIONAL addresses if they exist
      const additionalAddrs = additionalAddresses || [];
      const newErrors = new Map<number, string>();
      let successfulFetches = 1; // Start with 1 for primary address

      if (additionalAddrs.length > 0) {
        console.log(
          `📍 Fetching ${additionalAddrs.length} additional address(es)...`,
        );

        for (let i = 0; i < additionalAddrs.length; i++) {
          const addr = additionalAddrs[i];

          if (!addr.address || !addr.city || !addr.state || !addr.zip_code) {
            console.warn(
              `⚠️ Skipping additional address #${i + 1} - incomplete`,
            );
            newErrors.set(i, 'Incomplete address - please fill in all fields');
            continue;
            continue;
          }

          try {
            const additionalResponse = await fetchPropertyDataByAddress({
              address: addr.address,
              city: addr.city,
              state: addr.state,
              zipCode: addr.zip_code,
            });

            if (additionalResponse.success && additionalResponse.data) {
              const additionalLotSqft =
                Number(additionalResponse.data.lot_size_sqft) || 0;
              const additionalBuildingSqft =
                Number(additionalResponse.data.building_size_sqft) || 0;

              totalLotSqft += additionalLotSqft;
              totalLotAcres = totalLotSqft / 43560;
              totalBuildingSqft += additionalBuildingSqft;

              // Append parcel info
              if (additionalResponse.data.lot_numbers) {
                allParcelInfo.lot_numbers += allParcelInfo.lot_numbers
                  ? `, ${additionalResponse.data.lot_numbers}`
                  : additionalResponse.data.lot_numbers;
              }
              if (additionalResponse.data.parcel_number) {
                allParcelInfo.parcel_number += allParcelInfo.parcel_number
                  ? `, ${additionalResponse.data.parcel_number}`
                  : additionalResponse.data.parcel_number;
              }

              console.log(
                `✅ Additional address #${
                  i + 1
                }: ${additionalLotSqft} sqft lot, ${additionalBuildingSqft} sqft building`,
              );
              successfulFetches++;
            } else {
              const errorMsg = additionalResponse.error || 'not_found';
              const addressStr = `${addr.address}, ${addr.city}`;

              console.warn(`⚠️ Failed to fetch additional address #${i + 1}`);

              if (errorMsg === 'not_found') {
                newErrors.set(
                  i,
                  'Address not found - data not available. Please verify address or enter lot size manually.',
                );
              } else if (errorMsg === 'not_la_county') {
                newErrors.set(
                  i,
                  `${addr.city} may not be in LA County - property data unavailable.`,
                );
              } else {
                newErrors.set(i, 'Could not fetch data for this address.');
              }
            }
          } catch (err) {
            console.error(
              `❌ Error fetching additional address #${i + 1}:`,
              err,
            );
          }
        }
      }

      console.log(
        `🎯 COMBINED TOTALS: ${totalLotSqft} sqft lot, ${totalBuildingSqft} sqft building`,
      );

      const newAutoFilledFields = new Set<string>();

      // Always set the values when fetching (overwrite any existing values)
      form.setValue('lot_size_sqft', totalLotSqft, { shouldValidate: true });
      form.setValue('lot_size_acres', totalLotAcres, {
        shouldValidate: true,
      });
      newAutoFilledFields.add('lot_size_sqft');

      // Zoning description from Smarty (priority) or LA County - always update if available
      const zoningInfo =
        response.data.zoning || // Smarty zoning (e.g., "R3-1")
        response.data.land_use || // Smarty land use (e.g., "Religious")
        response.data.use_type || // LA County use type
        response.data.classification; // LA County classification

      if (zoningInfo) {
        form.setValue('zoning_description', zoningInfo);
        newAutoFilledFields.add('zoning_description');
      }

      setAutoFilledFields(newAutoFilledFields);

      // Store combined parcel/lot info for display
      setParcelInfo(allParcelInfo);

      // Set errors for failed additional addresses
      setAdditionalAddressErrors(newErrors);

      const totalAddresses = 1 + additionalAddrs.length;
      const failedCount = newErrors.size;

      if (failedCount === 0) {
        toast.success(
          `Property Data Fetched - Auto-filled ${newAutoFilledFields.size} field(s) from ${successfulFetches} address(es).`,
        );
      } else if (successfulFetches === 1) {
        toast.success(
          `Primary address fetched successfully. ${failedCount} additional address(es) failed - see messages below.`,
        );
      } else {
        toast.success(
          `Fetched data from ${successfulFetches} of ${totalAddresses} addresses. See messages below for failed addresses.`,
        );
      }
    } catch (error) {
      console.error('Error fetching property data:', error);
      toast.error(
        'An error occurred while fetching property data. Please try again or enter details manually.',
      );
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

  // Track additional addresses
  const additionalAddresses = form.watch('additional_addresses') || [];

  return (
    <div className='space-y-6'>
      <div>
        <h2 className='text-xl md:text-2xl font-bold'>Property Details</h2>
        <p className='text-sm md:text-base text-muted-foreground mt-1'>
          Information about the property you&apos;re proposing for development
        </p>
      </div>

      <div className='space-y-4'>
        {/* Demolish All Structures Checkbox - BEFORE address section */}
        <FormField
          control={form.control}
          name='demolish_all_structures'
          render={({ field }) => (
            <FormItem className='flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4 bg-muted/30'>
              <FormControl>
                <input
                  type='checkbox'
                  checked={field.value}
                  onChange={field.onChange}
                  className='h-4 w-4 rounded border-gray-300 mt-1'
                />
              </FormControl>
              <div className='space-y-1 leading-none'>
                <FormLabel className='text-sm md:text-base font-semibold'>
                  Are you okay if some or all existing buildings are demolished
                  to build housing?
                </FormLabel>
              </div>
            </FormItem>
          )}
        />

        {/* Property Address */}
        <FormField
          control={form.control}
          name='property_address'
          render={({ field }) => (
            <FormItem>
              <div className='flex items-center gap-2'>
                <FormLabel>
                  Property Address <span className='text-red-500'>*</span>
                </FormLabel>
                <button
                  type='button'
                  className='text-blue-600 hover:text-blue-700 text-xs flex items-center gap-1'
                  onClick={() => setShowFormatDialog(true)}
                >
                  <InfoIcon className='h-3.5 w-3.5' />
                  <span>Format examples</span>
                </button>
              </div>
              <FormControl>
                <Input
                  placeholder='e.g., 10304-10312 S. Central Avenue or 123 Church Lane'
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

        {/* Additional Addresses Section */}
        <div className='space-y-4'>
          {additionalAddresses.map((_, index) => (
            <div
              key={index}
              className='p-4 border rounded-lg bg-muted/20 space-y-3'
            >
              <div className='flex justify-between items-center mb-2'>
                <h4 className='font-semibold text-sm'>
                  Additional Address {index + 1}
                </h4>
                <Button
                  type='button'
                  variant='ghost'
                  size='sm'
                  onClick={() => {
                    const current =
                      form.getValues('additional_addresses') || [];
                    form.setValue(
                      'additional_addresses',
                      current.filter((_, i) => i !== index),
                    );
                    // Clear error for this address
                    setAdditionalAddressErrors((prev) => {
                      const updated = new Map(prev);
                      updated.delete(index);
                      return updated;
                    });
                  }}
                  className='text-red-600 hover:text-red-700'
                >
                  Remove
                </Button>
              </div>

              {/* Error message for this address */}
              {additionalAddressErrors.has(index) && (
                <Alert variant='destructive' className='mb-3'>
                  <AlertTriangle className='h-4 w-4' />
                  <AlertDescription>
                    {additionalAddressErrors.get(index)}
                  </AlertDescription>
                </Alert>
              )}

              <div className='grid grid-cols-1 gap-3'>
                <Input
                  placeholder='Street address'
                  value={additionalAddresses[index]?.address || ''}
                  onChange={(e) => {
                    const current =
                      form.getValues('additional_addresses') || [];
                    current[index] = {
                      ...current[index],
                      address: e.target.value,
                    };
                    form.setValue('additional_addresses', current);
                  }}
                />
                <div className='grid grid-cols-3 gap-2'>
                  <Input
                    placeholder='City'
                    value={additionalAddresses[index]?.city || ''}
                    onChange={(e) => {
                      const current =
                        form.getValues('additional_addresses') || [];
                      current[index] = {
                        ...current[index],
                        city: e.target.value,
                      };
                      form.setValue('additional_addresses', current);
                    }}
                  />
                  <Input
                    placeholder='State'
                    maxLength={2}
                    value={additionalAddresses[index]?.state || ''}
                    onChange={(e) => {
                      const current =
                        form.getValues('additional_addresses') || [];
                      current[index] = {
                        ...current[index],
                        state: e.target.value.toUpperCase(),
                      };
                      form.setValue('additional_addresses', current);
                    }}
                  />
                  <Input
                    placeholder='ZIP'
                    value={additionalAddresses[index]?.zip_code || ''}
                    onChange={(e) => {
                      const current =
                        form.getValues('additional_addresses') || [];
                      current[index] = {
                        ...current[index],
                        zip_code: e.target.value,
                      };
                      form.setValue('additional_addresses', current);
                    }}
                  />
                </div>
              </div>
            </div>
          ))}

          {/* Add Additional Address Button */}
          <Button
            type='button'
            variant='outline'
            onClick={() => {
              const current = form.getValues('additional_addresses') || [];
              // Auto-populate city, state, zip from primary address
              const primaryCity = form.getValues('property_city') || '';
              const primaryState = form.getValues('property_state') || '';
              const primaryZip = form.getValues('property_zip_code') || '';

              form.setValue('additional_addresses', [
                ...current,
                {
                  address: '',
                  city: primaryCity,
                  state: primaryState,
                  zip_code: primaryZip,
                },
              ]);
            }}
            className='w-full'
          >
            <Plus className='mr-2 h-4 w-4' />
            Add Additional Address
          </Button>
        </div>

        {/* Auto-Fetch Property Data Button */}
        <div className='flex items-center gap-4 p-4 border rounded-lg bg-muted/50'>
          <div className='flex-1'>
            <h3 className='text-sm font-semibold mb-1'>
              Auto-Fill Property Details
            </h3>
            <p className='text-xs text-muted-foreground'>
              We can automatically fetch lot size, parcel number, zoning, and
              other property data from public records (works nationwide).
            </p>
          </div>
          <div className='flex gap-2 shrink-0'>
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
                'Auto-Fill Data'
              )}
            </Button>
            {isMounted && autoFilledFields.size > 0 && (
              <Button
                type='button'
                onClick={() => {
                  // Clear all auto-filled fields
                  if (autoFilledFields.has('lot_size_sqft')) {
                    form.setValue('lot_size_sqft', null as any, {
                      shouldValidate: false,
                    });
                    form.setValue('lot_size_acres', null as any, {
                      shouldValidate: false,
                    });
                    // Force re-render by resetting the form state
                    form.resetField('lot_size_sqft', {
                      defaultValue: undefined,
                    });
                    form.resetField('lot_size_acres', {
                      defaultValue: undefined,
                    });
                  }
                  if (autoFilledFields.has('zoning_description')) {
                    form.setValue('zoning_description', '', {
                      shouldValidate: false,
                    });
                    form.resetField('zoning_description', { defaultValue: '' });
                  }
                  setAutoFilledFields(new Set());
                  setParcelInfo(null);
                  setFetchAttempted(false);
                  setAdditionalAddressErrors(new Map());
                  toast.success('Cleared all auto-filled data');
                }}
                variant='ghost'
                size='sm'
              >
                Clear All
              </Button>
            )}
          </div>
        </div>

        {/* Parcel/Lot Information Display - Simple */}
        {parcelInfo && (parcelInfo.lot_numbers || parcelInfo.parcel_number) && (
          <div className='text-sm text-muted-foreground space-y-1'>
            {parcelInfo.lot_numbers && (
              <div>
                <span className='font-medium'>Lot Numbers:</span>{' '}
                {parcelInfo.lot_numbers}
              </div>
            )}
            {parcelInfo.parcel_number && (
              <div>
                <span className='font-medium'>Parcel:</span>{' '}
                {parcelInfo.parcel_number}
              </div>
            )}
          </div>
        )}

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
        </div>

        {/* Special Considerations (optional textarea) */}
        <FormField
          control={form.control}
          name='build_area_notes'
          render={({ field }) => (
            <FormItem>
              <FormLabel>Special Considerations</FormLabel>
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

      {/* FORM ENHANCEMENT: Debt & Restrictions */}
      <div className='pt-6 border-t'>
        <h3 className='text-lg font-semibold mb-4'>
          Property Debt & Restrictions
        </h3>

        {/* Has Property Debt */}
        <div className='space-y-4'>
          <FormField
            control={form.control}
            name='has_property_debt'
            render={({ field }) => (
              <FormItem className='flex flex-row items-start space-x-3 space-y-0'>
                <FormControl>
                  <input
                    type='checkbox'
                    checked={field.value || false}
                    onChange={(e) => field.onChange(e.target.checked)}
                    className='h-4 w-4 rounded border-gray-300 mt-1'
                  />
                </FormControl>
                <div className='space-y-1 leading-none'>
                  <FormLabel>Property has outstanding debt or liens</FormLabel>
                  <FormDescription>
                    Check if there are mortgages, liens, or other debts on the
                    property
                  </FormDescription>
                </div>
              </FormItem>
            )}
          />

          {/* Conditional: Property Debt Amount */}
          {form.watch('has_property_debt') && (
            <>
              <FormField
                control={form.control}
                name='property_debt_amount'
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>
                      Debt Amount <span className='text-red-500'>*</span>
                    </FormLabel>
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
                      Total debt amount in dollars
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name='property_debt_terms'
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Debt Terms</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder='e.g., 15-year mortgage at 4.5% interest, $3,200/month payment...'
                        className='min-h-[80px]'
                        {...field}
                        value={field.value ?? ''}
                      />
                    </FormControl>
                    <FormDescription>
                      Describe the terms, interest rate, and payment schedule
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </>
          )}
        </div>

        {/* Has Transfer Restrictions */}
        <div className='space-y-4 mt-4'>
          <FormField
            control={form.control}
            name='has_transfer_restrictions'
            render={({ field }) => (
              <FormItem className='flex flex-row items-start space-x-3 space-y-0'>
                <FormControl>
                  <input
                    type='checkbox'
                    checked={field.value || false}
                    onChange={(e) => field.onChange(e.target.checked)}
                    className='h-4 w-4 rounded border-gray-300 mt-1'
                  />
                </FormControl>
                <div className='space-y-1 leading-none'>
                  <FormLabel>Property has transfer restrictions</FormLabel>
                  <FormDescription>
                    Check if there are deed restrictions, covenants, or
                    denominational requirements
                  </FormDescription>
                </div>
              </FormItem>
            )}
          />

          {/* Conditional: Transfer Restrictions Description */}
          {form.watch('has_transfer_restrictions') && (
            <FormField
              control={form.control}
              name='transfer_restrictions_description'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Restrictions Description{' '}
                    <span className='text-red-500'>*</span>
                  </FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder='Describe the transfer restrictions, covenants, or approval requirements...'
                      className='min-h-[80px]'
                      {...field}
                      value={field.value ?? ''}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          )}
        </div>

        {/* Has Long-Term Leases */}
        <div className='space-y-4 mt-4'>
          <FormField
            control={form.control}
            name='has_long_term_leases'
            render={({ field }) => (
              <FormItem className='flex flex-row items-start space-x-3 space-y-0'>
                <FormControl>
                  <input
                    type='checkbox'
                    checked={field.value || false}
                    onChange={(e) => field.onChange(e.target.checked)}
                    className='h-4 w-4 rounded border-gray-300 mt-1'
                  />
                </FormControl>
                <div className='space-y-1 leading-none'>
                  <FormLabel>
                    Property has long-term leases or commitments
                  </FormLabel>
                  <FormDescription>
                    Check if there are existing leases or commitments that
                    extend beyond 1 year
                  </FormDescription>
                </div>
              </FormItem>
            )}
          />

          {/* Conditional: Long-Term Leases Description */}
          {form.watch('has_long_term_leases') && (
            <FormField
              control={form.control}
              name='long_term_leases_description'
              render={({ field }) => (
                <FormItem>
                  <FormLabel>
                    Leases Description <span className='text-red-500'>*</span>
                  </FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder='Describe the leases, tenants, terms, and expiration dates...'
                      className='min-h-[80px]'
                      {...field}
                      value={field.value ?? ''}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          )}
        </div>
      </div>

      {/* FORM ENHANCEMENT: Project Vision */}
      <div className='pt-6 border-t'>
        <h3 className='text-lg font-semibold mb-4'>Project Vision</h3>

        {/* Project Components Wanted */}
        <FormField
          control={form.control}
          name='project_components_wanted'
          render={({ field }) => {
            const PROJECT_COMPONENTS = [
              {
                value: 'affordable_housing',
                label: 'Affordable Housing Units',
              },
              { value: 'senior_housing', label: 'Senior Housing' },
              { value: 'family_housing', label: 'Family Housing' },
              { value: 'new_sanctuary', label: 'New/Renovated Sanctuary' },
              { value: 'fellowship_hall', label: 'Fellowship Hall' },
              { value: 'offices', label: 'Church Offices' },
              { value: 'classrooms', label: 'Classrooms/Meeting Rooms' },
              { value: 'parking', label: 'Parking Structure' },
              { value: 'community_space', label: 'Community Space' },
            ];
            return (
              <FormItem>
                <FormLabel>
                  What would you like to include in the development?
                </FormLabel>
                <FormDescription>
                  Select all components you'd like to see in the project
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
                      {PROJECT_COMPONENTS.map((item) => {
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
                      const item = PROJECT_COMPONENTS.find(
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

        {/* Sunday Parking Needed */}
        <FormField
          control={form.control}
          name='sunday_parking_needed'
          render={({ field }) => (
            <FormItem className='mt-4'>
              <FormLabel>Parking Spaces Needed on Sundays</FormLabel>
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
                    const val = e.target.value;
                    field.onChange(val === '' ? undefined : Number(val));
                  }}
                />
              </FormControl>
              <FormDescription>
                How many parking spaces do you need for Sunday services?
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>

      {/* Property Improvement Needs */}
      <div>
        <h3 className='text-lg font-semibold mb-4'>
          Property Improvement Needs
        </h3>

        <FormField
          control={form.control}
          name='property_improvement_needs'
          render={() => (
            <FormItem>
              <FormLabel>Do you have any property improvement needs?</FormLabel>
              <FormDescription>
                Select all that apply. These won't affect your assessment score.
              </FormDescription>
              <div className='space-y-2 mt-3'>
                {[
                  { value: 'hvac', label: 'HVAC/AC System' },
                  { value: 'roof', label: 'Roof' },
                  { value: 'landscaping', label: 'Landscaping' },
                  { value: 'painting', label: 'Painting' },
                  { value: 'interior', label: 'Interior Improvements' },
                  { value: 'other', label: 'Other' },
                ].map((item) => (
                  <FormField
                    key={item.value}
                    control={form.control}
                    name='property_improvement_needs'
                    render={({ field }) => {
                      const currentValue = field.value || [];
                      return (
                        <FormItem
                          key={item.value}
                          className='flex flex-row items-start space-x-3 space-y-0'
                        >
                          <FormControl>
                            <input
                              type='checkbox'
                              checked={currentValue.includes(item.value)}
                              onChange={(checked) => {
                                const newValue = checked.target.checked
                                  ? [...currentValue, item.value]
                                  : currentValue.filter(
                                      (value: string) => value !== item.value,
                                    );
                                field.onChange(newValue);
                              }}
                              className='h-4 w-4 rounded border-gray-300'
                            />
                          </FormControl>
                          <FormLabel className='font-normal cursor-pointer'>
                            {item.label}
                          </FormLabel>
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
      </div>

      {/* Capital/Financing Need */}
      <FormField
        control={form.control}
        name='capital_financing_need'
        render={({ field }) => (
          <FormItem>
            <FormLabel>Do you have a capital or financing need?</FormLabel>
            <FormControl>
              <Input
                placeholder='e.g., Need funds for roof repairs'
                maxLength={100}
                {...field}
                value={field.value || ''}
              />
            </FormControl>
            <FormDescription>
              Optional. Describe any capital or financing needs (max 100
              characters). This won't affect your assessment score.
            </FormDescription>
            <FormMessage />
          </FormItem>
        )}
      />

      {/* Format Examples Dialog */}
      <Dialog open={showFormatDialog} onOpenChange={setShowFormatDialog}>
        <DialogContent className='sm:max-w-[500px]'>
          <DialogHeader>
            <DialogTitle className='text-xl'>
              Address Format Examples
            </DialogTitle>
            <DialogDescription className='text-base'>
              Multiple parcels can be entered in the address field using these
              formats:
            </DialogDescription>
          </DialogHeader>

          <div className='space-y-4 py-4'>
            <div className='space-y-3'>
              <div className='p-3 bg-muted rounded-md'>
                <p className='text-base font-mono'>
                  10304-10312 S. Central Avenue
                </p>
              </div>
              <div className='p-3 bg-muted rounded-md'>
                <p className='text-base font-mono'>
                  10304, 10306, 10308 S. Central Avenue
                </p>
              </div>
              <div className='p-3 bg-muted rounded-md'>
                <p className='text-base font-mono'>
                  10304/10306/10308 S. Central Avenue
                </p>
              </div>
              <div className='p-3 bg-muted rounded-md'>
                <p className='text-base font-mono'>
                  Parcels 10304-10312 S. Central Avenue
                </p>
              </div>
            </div>

            <div className='border-t pt-4'>
              <p className='text-base text-muted-foreground'>
                💡 <strong>Tip:</strong> For separate parcels with different
                street addresses, click the{' '}
                <strong>"Add Additional Address"</strong> button below the
                primary address.
              </p>
            </div>
          </div>

          <Button onClick={() => setShowFormatDialog(false)} className='w-full'>
            Got it
          </Button>
        </DialogContent>
      </Dialog>
    </div>
  );
}
