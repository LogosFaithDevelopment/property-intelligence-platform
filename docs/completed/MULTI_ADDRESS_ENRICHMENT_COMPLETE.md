# Multi-Address Enrichment - COMPLETE ✅

**Date:** October 9, 2025  
**Status:** Backend enrichment service now handles multiple addresses

---

## WHAT WAS UPDATED:

### 1. ✅ Schema - Accepts New Fields

**File:** `backend/app/schemas/submission.py`

Added to `PropertySubmissionData`:

```python
# Multi-Address Support
demolish_all_structures: Optional[bool] = Field(default=False, description="Plan to demolish all existing structures")
additional_addresses: Optional[list] = Field(default=None, description="Additional addresses for multi-parcel properties")
```

### 2. ✅ Enrichment Service - Multi-Address Support

**File:** `backend/app/services/property_enrichment.py`

#### A) New Method: `_combine_multi_address_data()`

Combines data from multiple addresses:

- Fetches Smarty data for PRIMARY address
- Fetches Smarty data for each ADDITIONAL address
- Sums all lot sizes: `total_lot_sqft = address1_lot + address2_lot + ...`
- Sums all building sizes (ONLY if NOT demolishing): `total_building_sqft = address1_building + address2_building + ...`
- Calculates available space: `available = total_lot - total_building`
- Collects all lot numbers: `"182,183, 184,185"` (from all addresses)
- Collects all parcel numbers

#### B) Updated Method: `_fetch_smarty_data()`

Now handles multiple addresses:

```python
# Fetch PRIMARY address
result = await smarty_provider.get_property_data(primary_address)

# Fetch ADDITIONAL addresses
for addr in property_obj.additional_addresses:
    additional_result = await smarty_provider.get_property_data(addr)
    all_addresses_data.append(additional_result)

# Combine all data
combined_data = self._combine_multi_address_data(all_addresses_data, demolish_flag)
```

#### C) Updated Method: `_update_property_with_enriched_data()`

Saves combined values to database:

```python
# Store combined lot/building sizes (for multi-address properties)
property_obj.combined_lot_size_sqft = combined_lot_size
property_obj.combined_building_size_sqft = combined_building_size
```

---

## HOW IT WORKS:

### Example: Manchester Property (2 addresses)

#### Step 1: User Submits Form

```json
{
  "property": {
    "street_address": "709 W Manchester Ave",
    "city": "Los Angeles",
    "state": "CA",
    "zip_code": "90044",
    "demolish_all_structures": false,
    "additional_addresses": [
      {
        "address": "706 W 85th St",
        "city": "Los Angeles",
        "state": "CA",
        "zip_code": "90044"
      }
    ]
  }
}
```

#### Step 2: Enrichment Service Runs

```python
# Fetch PRIMARY address (709 W Manchester)
address_1_data = fetch_smarty("709 W Manchester Ave, LA, CA 90044")
# Returns: lot=13,708 sqft, building=5,000 sqft, lots="182,183"

# Fetch ADDITIONAL address (706 W 85th St)
address_2_data = fetch_smarty("706 W 85th St, LA, CA 90044")
# Returns: lot=6,511 sqft, building=2,000 sqft, lots="184,185"
```

#### Step 3: Combine Data

```python
# Sum lot sizes
total_lot = 13,708 + 6,511 = 20,219 sqft

# Sum building sizes (if NOT demolishing)
if not demolish_all_structures:
    total_building = 5,000 + 2,000 = 7,000 sqft
else:
    total_building = 0 sqft

# Calculate available space
available = 20,219 - 7,000 = 13,219 sqft

# Collect lot numbers
all_lots = "182,183, 184,185"
```

#### Step 4: Save to Database

```python
property.lot_size_sqft = 13,708  # Primary address lot (for display)
property.combined_lot_size_sqft = 20,219  # TOTAL from all addresses
property.combined_building_size_sqft = 7,000  # TOTAL buildings
property.demolish_all_structures = false
property.additional_addresses = [{"address": "706 W 85th St", ...}]
```

#### Step 5: AI Assessment Uses Combined Values

```python
# AI assessment will use:
lot_size = property.combined_lot_size_sqft or property.lot_size_sqft
# = 20,219 sqft (instead of 13,708 sqft)

building_size = property.combined_building_size_sqft or 0
# = 7,000 sqft (or 0 if demolishing)

available_build_space = lot_size - building_size
# = 20,219 - 7,000 = 13,219 sqft

# Calculate units
units = calculate_units(available_build_space)
# = ~134 units ✅ (instead of 62 units ❌)
```

---

## DEMOLISH FLAG LOGIC:

### Scenario A: User checks "Demolish All Structures"

```python
demolish_all_structures = True

# Don't subtract buildings
available_space = total_lot_size - 0
# Manchester: 20,219 - 0 = 20,219 sqft available
```

### Scenario B: User DOES NOT check "Demolish All Structures"

```python
demolish_all_structures = False

# Subtract existing buildings
available_space = total_lot_size - total_building_size
# Manchester: 20,219 - 7,000 = 13,219 sqft available
```

---

## DATABASE COLUMNS USED:

From migration `2025_10_09_1615_add_demolish_and_multi_address.py`:

```sql
-- New columns in properties table
demolish_all_structures BOOLEAN DEFAULT false
additional_addresses JSONB  -- Array of address objects
combined_lot_size_sqft INTEGER  -- Total lot from all addresses
combined_building_size_sqft INTEGER  -- Total buildings (if not demolishing)
```

---

## LOG OUTPUT EXAMPLE:

```
INFO: Fetching Smarty property data for PRIMARY address: 709 W Manchester Ave, Los Angeles, CA 90044
INFO: ✅ Successfully fetched data for primary address
INFO: Found 1 additional address(es) to fetch
INFO: Fetching Smarty data for additional address #1: 706 W 85th St
INFO: ✅ Successfully fetched data for additional address #1
INFO: Combining data from 2 address(es)
INFO: Address #1: Lot=13,708 sqft, Building=5,000 sqft, Lots=182,183, Parcel=6032-015-042
INFO: Address #2: Lot=6,511 sqft, Building=2,000 sqft, Lots=184,185, Parcel=6032-015-043
INFO: ✅ COMBINED TOTALS: Lot=20,219 sqft (0.46 acres), Building=7,000 sqft, Available=13,219 sqft - QUALIFIES for LOGOS
INFO: Updated lot_size from Smarty: 20,219 sqft (0.46 acres)
INFO: Updated building_sqft from Smarty: 7,000 sqft
INFO: Stored combined_lot_size_sqft: 20,219 sqft
INFO: Stored combined_building_size_sqft: 7,000 sqft
INFO: Updated property 123 with enriched data
```

---

## TESTING INSTRUCTIONS:

### 1. Delete Existing Manchester Submissions

```sql
DELETE FROM assessments WHERE property_id IN (
  SELECT id FROM properties WHERE street_address LIKE '%Manchester%'
);
DELETE FROM properties WHERE street_address LIKE '%Manchester%';
DELETE FROM churches WHERE name LIKE '%Manchester%';
```

### 2. Submit New Manchester Property via Form

**Primary Address:**

- Street: 709 W Manchester Ave
- City: Los Angeles
- State: CA
- ZIP: 90044

**Check the box:** ☐ Do you plan on knocking down all existing structures? (leave unchecked for testing)

**Click:** "+ Add Additional Address"

**Additional Address #1:**

- Street: 706 W 85th St
- City: Los Angeles
- State: CA
- ZIP: 90044

**Submit form**

### 3. Check Database After Enrichment

```sql
SELECT
  id,
  street_address,
  lot_size_sqft,
  combined_lot_size_sqft,
  combined_building_size_sqft,
  demolish_all_structures,
  additional_addresses
FROM properties
WHERE street_address LIKE '%Manchester%';
```

**Expected Results:**

- `lot_size_sqft` = 13,708 (primary address)
- `combined_lot_size_sqft` = 20,219 (both addresses)
- `combined_building_size_sqft` = 7,000 (both buildings, since not demolishing)
- `demolish_all_structures` = false
- `additional_addresses` = JSON array with 706 W 85th St

### 4. Check AI Assessment

```sql
SELECT
  units,
  available_build_space_sqft,
  irr_10yr,
  noi_stabilized
FROM assessments a
JOIN properties p ON a.property_id = p.id
WHERE p.street_address LIKE '%Manchester%';
```

**Expected Results:**

- `available_build_space_sqft` = 13,219 (or 20,219 if demolishing)
- `units` ≈ 134 (close to actual LOGOS development)
- IRR/NOI calculated based on 134 units

---

## WHAT'S NEXT:

### ✅ COMPLETED:

1. Database migration (4 new columns)
2. Frontend form (demolish checkbox + add addresses)
3. Backend schema (accepts new fields)
4. Enrichment service (fetches all addresses, combines data)
5. Parcel display (shows lot numbers after fetch)

### ⏳ TODO:

1. **Update AI Assessment Service** - Use combined values instead of single address
2. **Multi-Story Scenarios** - Calculate 3, 4, 5 story options (remove hardcoded 4)
3. **Display All Scenarios** - Show 3 rows in assessment UI (3/4/5 stories)
4. **CIO Value Changes** - Per user note about additional updates

---

**Status:** Enrichment complete ✅  
**Ready for:** Testing with Manchester property (2 addresses)  
**Next:** Update AI assessment to use combined values
