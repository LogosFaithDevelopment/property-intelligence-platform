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
import {
  InfoIcon,
  AlertTriangle,
  Loader2,
  CheckCircle2,
  Plus,
} from 'lucide-react';
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
  const [parcelInfo, setParcelInfo] = useState<{
    lot_numbers?: string;
    parcel_number?: string;
  } | null>(null);

  const propertyAddress = form.watch('property_address');
  const propertyCity = form.watch('property_city');
  const propertyState = form.watch('property_state');
  const propertyZip = form.watch('property_zip_code');

  // Handler to fetch property data from LA County API (including additional addresses)
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
      // Fetch PRIMARY address
      const response = await fetchPropertyDataByAddress({
        address: propertyAddress,
        city: propertyCity,
        state: propertyState,
        zipCode: propertyZip,
      });

      if (!response.success || !response.data) {
        throw new Error(response.error || 'Failed to fetch property data');
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
        `🏠 Primary address: ${totalLotSqft} sqft lot, ${totalBuildingSqft} sqft building`
      );

      // Fetch ADDITIONAL addresses if they exist
      const additionalAddrs = additionalAddresses || [];
      if (additionalAddrs.length > 0) {
        console.log(
          `📍 Fetching ${additionalAddrs.length} additional address(es)...`
        );

        for (let i = 0; i < additionalAddrs.length; i++) {
          const addr = additionalAddrs[i];

          if (!addr.address || !addr.city || !addr.state || !addr.zip_code) {
            console.warn(
              `⚠️ Skipping additional address #${i + 1} - incomplete`
            );
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
                }: ${additionalLotSqft} sqft lot, ${additionalBuildingSqft} sqft building`
              );
            } else {
              console.warn(`⚠️ Failed to fetch additional address #${i + 1}`);
            }
          } catch (err) {
            console.error(
              `❌ Error fetching additional address #${i + 1}:`,
              err
            );
          }
        }
      }

      console.log(
        `🎯 COMBINED TOTALS: ${totalLotSqft} sqft lot, ${totalBuildingSqft} sqft building`
      );

      const newAutoFilledFields = new Set<string>();

      // Only auto-fill if the field is currently empty (manual entries take precedence)
      if (!form.getValues('lot_size_sqft')) {
        console.log(
          '🔍 Auto-fetch setting lot_size_sqft:',
          totalLotSqft,
          'Type:',
          typeof totalLotSqft
        );
        console.log(
          '🔍 Auto-fetch setting lot_size_acres:',
          totalLotAcres,
          'Type:',
          typeof totalLotAcres
        );

        form.setValue('lot_size_sqft', totalLotSqft, { shouldValidate: true });
        form.setValue('lot_size_acres', totalLotAcres, {
          shouldValidate: true,
        });
        newAutoFilledFields.add('lot_size_sqft');

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

      // Zoning description from Smarty (priority) or LA County
      if (!form.getValues('zoning_description')) {
        const zoningInfo =
          response.data.zoning || // Smarty zoning (e.g., "R3-1")
          response.data.land_use || // Smarty land use (e.g., "Religious")
          response.data.use_type || // LA County use type
          response.data.classification; // LA County classification

        if (zoningInfo) {
          form.setValue('zoning_description', zoningInfo);
          newAutoFilledFields.add('zoning_description');
        }
      }

      setAutoFilledFields(newAutoFilledFields);

      // Store combined parcel/lot info for display
      setParcelInfo(allParcelInfo);

      const addressCount = 1 + additionalAddrs.length;
      toast({
        title: 'Property Data Fetched',
        description: `Auto-filled ${newAutoFilledFields.size} field(s) from ${addressCount} address(es).`,
        duration: 5000,
      });
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
                      current.filter((_, i) => i !== index)
                    );
                  }}
                  className='text-red-600 hover:text-red-700'
                >
                  Remove
                </Button>
              </div>

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
              form.setValue('additional_addresses', [
                ...current,
                { address: '', city: '', state: '', zip_code: '' },
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
                                      (value: string) => value !== item.value
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
    </div>
  );
}
