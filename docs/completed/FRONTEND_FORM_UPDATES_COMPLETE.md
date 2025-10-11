# Frontend Form Updates - Step #2 COMPLETE ✅

**Date:** October 9, 2025  
**Status:** Frontend form changes complete

---

## CHANGES MADE:

### 1. ✅ Updated Validation Schema

**File:** `frontend/src/lib/validations/submission.ts`

**Added fields:**

```typescript
// Demolish Flag
demolish_all_structures: z.boolean().optional().default(false),

// Additional Addresses (array)
additional_addresses: z.array(
  z.object({
    address: z.string().min(5),
    city: z.string().min(2),
    state: z.string().length(2),
    zip_code: z.string().regex(/^\d{5}(-\d{4})?$/),
  })
).optional().default([]),
```

---

### 2. ✅ Updated Form Defaults

**File:** `frontend/src/components/forms/multi-step-submission-form.tsx`

**Added:**

```typescript
demolish_all_structures: false,
additional_addresses: [],
```

---

### 3. ✅ Updated Section 2 Form Component

**File:** `frontend/src/components/forms/sections/section-2-property-details.tsx`

**Added at the TOP (before address section):**

#### A) Demolish All Structures Checkbox

```tsx
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
        <FormLabel className='text-base font-semibold'>
          Do you plan on knocking down all existing structures on your property?
        </FormLabel>
        <FormDescription>
          If yes, we'll calculate available build space using the total lot
          size. If no, we'll subtract existing building areas from the lot size.
        </FormDescription>
      </div>
    </FormItem>
  )}
/>
```

#### B) Additional Addresses Section (after ZIP code)

```tsx
{/* Show existing additional addresses */}
{additionalAddresses.map((_, index) => (
  <div key={index} className='p-4 border rounded-lg bg-muted/20 space-y-3'>
    <div className='flex justify-between items-center mb-2'>
      <h4 className='font-semibold text-sm'>Additional Address {index + 1}</h4>
      <Button type='button' variant='ghost' size='sm' onClick={() => removeAddress(index)}>
        Remove
      </Button>
    </div>

    {/* Address fields (street, city, state, ZIP) */}
    <Input placeholder='Street address' {...} />
    <Input placeholder='City' {...} />
    <Input placeholder='State' maxLength={2} {...} />
    <Input placeholder='ZIP' {...} />
  </div>
))}

{/* Add button */}
<Button type='button' variant='outline' onClick={addAddress} className='w-full'>
  <Plus className='mr-2 h-4 w-4' />
  Add Additional Address
</Button>
```

#### C) Updated Available Build Space Placeholder

```tsx
<Input
  type='number'
  placeholder='Leave this blank if you do not know the exact build space available'
  {...field}
/>
```

---

## UI/UX FEATURES:

### ✅ Demolish Checkbox

- **Location:** Top of Property Details section (before address)
- **Styling:** Bordered card with muted background
- **Behavior:**
  - If checked → use total lot size
  - If unchecked → subtract building sizes from lot
- **Helper text:** Explains the impact on calculations

### ✅ Multiple Addresses

- **Location:** After primary address (after ZIP code)
- **Initial state:** No additional addresses shown
- **Add button:** "+ Add Additional Address" (full width, outline style)
- **Each address card:**
  - Light muted background
  - Remove button (top-right)
  - 4 input fields: street, city (1 col), state + ZIP (grid)
- **Data structure:** Array of address objects in form state

### ✅ Better Placeholder Text

- Old: "Leave blank if entire lot is available"
- New: **"Leave this blank if you do not know the exact build space available"**
- More user-friendly and clear

---

## FORM FLOW:

```
Step 2: Property Details
├─ [✓] Do you plan on knocking down all existing structures? (checkbox)
├─ Property Address (required)
├─ City, State, ZIP (required)
├─ [+] Add Additional Address (button)
│   └─ Additional Address 1
│       ├─ Street address
│       ├─ City
│       ├─ State
│       ├─ ZIP
│       └─ [Remove] button
├─ Auto-Fetch Property Data (button)
├─ Lot Size (sqft, acres)
├─ Available Build Space (optional - NEW placeholder text)
├─ Build Area Notes
├─ Current Usage
└─ Zoning
```

---

## DATA STRUCTURE:

### Form Values:

```typescript
{
  // Existing fields
  property_address: string
  property_city: string
  property_state: string
  property_zip_code: string

  // NEW FIELDS
  demolish_all_structures: boolean  // default: false
  additional_addresses: Array<{     // default: []
    address: string
    city: string
    state: string
    zip_code: string
  }>

  // Rest of fields...
  lot_size_sqft: number
  available_build_sqft: number
  ...
}
```

---

## WHAT'S NEXT (Step #3):

### Backend API Updates Needed:

1. **Update Property Model** - ✅ DONE (database migration complete)
2. **Update Submission Schema** - Accept demolish flag + additional addresses
3. **Update Smarty Integration** - Fetch data for multiple addresses
4. **Combine Lot Sizes Logic:**

   ```python
   # Fetch all addresses
   address_1_data = fetch_smarty(address_1)
   address_2_data = fetch_smarty(address_2)

   # Combine data
   total_lot_size = address_1_lot + address_2_lot
   total_building_size = address_1_building + address_2_building

   # Calculate available space
   if demolish_all:
       available = total_lot_size
   else:
       available = total_lot_size - total_building_size
   ```

5. **Update Assessment Calculation** - Use combined lot size
6. **Display Parcels** - Show all parcel numbers from all addresses

---

## TESTING CHECKLIST:

- [ ] Form renders without errors
- [ ] Demolish checkbox toggles correctly
- [ ] Can add multiple additional addresses
- [ ] Can remove additional addresses
- [ ] Address validation works
- [ ] Form submission includes new fields
- [ ] Placeholder text updated correctly

---

**Status:** Frontend complete ✅  
**Next:** Backend API updates (Step #3)
