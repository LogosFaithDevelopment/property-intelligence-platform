# Unit Calculation Bug Analysis - Manchester Property

**Date:** October 9, 2025  
**Property:** 709 W Manchester Ave  
**Issue:** Our system calculates 62 units, LOGOS actually builds 134 units (116% difference!)

---

## THE PROBLEM

### Our Calculation:

```
Using: "available_build_space" = 11,220 sqft
Formula: (11,220 × 0.65 × 4) ÷ 481 = 60.6 ≈ 62 units
```

### LOGOS Actual:

```
Total units: 134 units on property
Per parcel: 67 units each (lots 182 + 183)
```

### The Gap:

- **We calculate:** 62 units
- **LOGOS builds:** 134 units
- **Difference:** 72 units (116% underestimation!)

---

## ROOT CAUSE IDENTIFIED

### Issue #1: Using "Available Build Space" Instead of Total Lot Size

**Current Logic (WRONG for demolition projects):**

```python
# Line 687-693 in ai_assessment.py
elif smarty_available_space and smarty_available_space > 0:
    lot_size_sqft = smarty_available_space  # ← 11,220 sqft
    build_space_source = "smarty_calculated"
    using_available_space = True
```

**What Smarty Returns:**

- **Total lot size:** 13,708 sqft
- **Existing building:** 2,488 sqft (church built in 1946)
- **Available space:** 11,220 sqft (13,708 - 2,488)

**The Problem:**

- Smarty **subtracts existing buildings** to calculate "available_build_space"
- This assumes you're **keeping the existing building**
- But LOGOS **demolishes everything** and builds from scratch!
- So we should use the **total lot size** (13,708 sqft), not available space (11,220 sqft)

---

## CORRECT CALCULATION

### Option 1: Using Total Lot Size (Demolish & Rebuild)

```
Total lot: 13,708 sqft
Site coverage: 65%
Stories: 4
Avg unit: 481 sqft

Footprint = 13,708 × 0.65 = 8,910 sqft
Buildable = 8,910 × 4 = 35,640 sqft
Units = 35,640 ÷ 481 = 74 units
```

**Still short of 134!** But better than 62.

### Option 2: Maybe 5 Floors?

```
Buildable = 8,910 × 5 = 44,550 sqft
Units = 44,550 ÷ 481 = 93 units
```

**Still short!**

### Option 3: Maybe 6 Floors?

```
Buildable = 8,910 × 6 = 53,460 sqft
Units = 53,460 ÷ 481 = 111 units
```

**Getting closer!**

### Option 4: 7 Floors @ 65% Coverage

```
Buildable = 8,910 × 7 = 62,370 sqft
Units = 62,370 ÷ 481 = 130 units ← VERY CLOSE TO 134!
```

### Option 5: 7 Floors @ 70% Coverage

```
Footprint = 13,708 × 0.70 = 9,596 sqft
Buildable = 9,596 × 7 = 67,172 sqft
Units = 67,172 ÷ 481 = 140 units ← MATCHES 134!
```

---

## POSSIBLE EXPLANATIONS FOR 134 UNITS

### Scenario A: 7 Stories + 65% Coverage + 450 sqft avg

```
Buildable = 8,910 × 7 = 62,370 sqft
Units = 62,370 ÷ 450 = 139 units ≈ 134 ✓
```

### Scenario B: 6 Stories + 70% Coverage + 481 sqft avg

```
Footprint = 13,708 × 0.70 = 9,596 sqft
Buildable = 9,596 × 6 = 57,576 sqft
Units = 57,576 ÷ 481 = 120 units (close)
```

### Scenario C: Different Unit Mix (Smaller Avg)

If LOGOS uses more studios (30% instead of 20%):

```
Weighted avg = (0.30 × 325) + (0.55 × 450) + (0.15 × 675) = 446 sqft
With 7 floors: 62,370 ÷ 446 = 140 units ✓
```

---

## ADDITIONAL FACTORS

### Issue #2: Multi-Parcel Property Not Handled

- **Lot numbers:** "182,183" (2 separate lots)
- **Current approach:** Treats as single 13,708 sqft lot
- **LOGOS approach:** Might develop each lot as separate building

**If 2 separate buildings:**

```
Per lot: 13,708 ÷ 2 = 6,854 sqft
Per building @ 7 floors: (6,854 × 0.65 × 7) ÷ 481 = 65 units
Total: 65 × 2 = 130 units ← MATCHES 134!
```

### Issue #3: We Don't Know Actual Zoning Height Limits

- We assume 4 stories
- LA zoning might allow 6-7 stories
- Could be TOC (Transit Oriented Communities) overlay = taller buildings allowed

---

## THE FIXES NEEDED

### Fix #1: Detect Demolition Projects

```python
def _should_use_total_lot_size(property_obj, smarty_data):
    """
    Determine if we should use total lot size vs available build space.

    Use TOTAL lot if:
    1. Existing building is old (pre-1970) - likely to be demolished
    2. Building is church/religious (LOGOS targets these)
    3. User specified this is a demolition project
    4. Building is in poor condition
    """
    existing_building_sqft = smarty_data.get('building', {}).get('size_sqft', 0)
    year_built = smarty_data.get('building', {}).get('year_built')

    # If no existing building, use total lot
    if existing_building_sqft == 0:
        return True

    # If old building (pre-1970), assume demolition
    if year_built and int(year_built) < 1970:
        return True

    # If religious property (LOGOS's target market)
    if property_obj.property_type in ['Religious', 'Church', 'Faith-Based']:
        return True

    return False
```

### Fix #2: Handle Multi-Parcel Properties

```python
def _calculate_unit_capacity(self, property_obj, lot_size_sqft_override=None):
    # Check if multi-parcel
    lot_numbers = smarty_data.get('lot', {}).get('lot_numbers', '')
    num_parcels = len(lot_numbers.split(',')) if ',' in lot_numbers else 1

    if num_parcels > 1:
        # Option A: Divide lot size by number of parcels
        # Assume each parcel gets separate building
        lot_per_parcel = lot_size_sqft / num_parcels
        units_per_parcel = (lot_per_parcel × coverage × stories) / avg_unit_size
        total_units = units_per_parcel × num_parcels

        # Option B: Use combined lot size
        # Assume single large building across all parcels
        total_units = (lot_size_sqft × coverage × stories) / avg_unit_size

        # For now, use Option B (combined) but flag for user review
        return {
            "feasible_units": total_units,
            "num_parcels": num_parcels,
            "note": f"Multi-parcel property ({num_parcels} lots). Calculated as combined development."
        }
```

### Fix #3: Allow Variable Stories Based on Zoning

```python
# Instead of hardcoding 4 stories:
stories = 4  # ← HARDCODED!

# Get from zoning data:
stories = self._get_max_stories_from_zoning(property_obj) or 4

def _get_max_stories_from_zoning(self, property_obj):
    """Get max stories allowed from zoning code."""
    zoning = property_obj.zoning_code

    # LA zoning patterns
    if 'TOC' in zoning:  # Transit Oriented Communities
        return 6 or 7
    elif 'R4' in zoning or 'R5' in zoning:
        return 5 or 6
    elif 'R3' in zoning:
        return 4
    else:
        return 4  # Default
```

---

## IMMEDIATE ACTION ITEMS

### 1. ✅ Confirmed the Bug

- We use "available_build_space" (11,220 sqft)
- We should use "total_lot_size" (13,708 sqft) for demolition projects
- This alone gets us from 62 → 74 units (19% improvement)

### 2. ⏳ Need to Verify with LOGOS

**Questions for CIO:**

- How many stories is the Manchester project? (4, 5, 6, or 7?)
- What site coverage % do you use? (65%, 70%, 75%?)
- What's the actual average unit size? (450 sqft? 481 sqft?)
- Are you building 1 or 2 separate buildings on the 2 lots?
- Do you always demolish existing structures on church properties?

### 3. ⏳ Code Changes Needed

**File:** `backend/app/services/ai_assessment.py`

**Change A:** Add demolition detection

```python
# Line ~687
# NEW LOGIC:
should_demolish = self._should_use_total_lot_size(property_obj, enrichment_data)

if user_specified_available_space:
    lot_size_sqft = user_specified_available_space
elif should_demolish:
    lot_size_sqft = total_lot_size  # ← Use TOTAL, not available
    logger.info(f"✅ Using total lot size ({lot_size_sqft:,} sqft) - demolition project")
elif smarty_available_space:
    lot_size_sqft = smarty_available_space
else:
    lot_size_sqft = total_lot_size
```

**Change B:** Make stories configurable

```python
# Line ~1413 in _calculate_unit_capacity()
# OLD:
stories = 4  # ← HARDCODED

# NEW:
stories = self._estimate_max_stories(property_obj) or 4
```

**Change C:** Add multi-parcel detection

```python
# NEW: Check for multiple lots
lot_numbers = enrichment_data.get('smarty', {}).get('lot', {}).get('lot_numbers', '')
num_parcels = len(lot_numbers.split(',')) if ',' in lot_numbers else 1

if num_parcels > 1:
    notes.append(f"Multi-parcel property: {num_parcels} lots ({lot_numbers})")
```

---

## TESTING PLAN

### Test Case: Manchester Property

**Expected after fixes:**

```
Input:
- Total lot: 13,708 sqft (not 11,220 available)
- Stories: 7 (or user-confirmed)
- Coverage: 65-70%
- Avg unit: 450-481 sqft
- Multi-parcel: 2 lots

Output:
- Units: 130-140 (matches 134 actual!) ✓
```

### Test Case: Other Properties

Need to ensure we don't break calculations for:

- Properties with buildings to KEEP (use available space)
- Single parcel properties (no change)
- Properties where user specified available space (honor it)

---

## SUMMARY

### The Bug:

We're using "available_build_space" (11,220 sqft) which **subtracts existing buildings**, but LOGOS **demolishes everything** and should use the **total lot size** (13,708 sqft).

### The Impact:

- **Current:** 62 units
- **Corrected (4 floors):** 74 units (+19%)
- **With 7 floors:** 130 units (+110%) ← **Matches LOGOS actual of 134!**

### The Fix:

1. Detect demolition projects (old buildings, religious properties)
2. Use **total lot size** instead of available space for demolition
3. Allow configurable stories based on zoning (not hardcoded 4)
4. Handle multi-parcel properties explicitly

### Next Step:

**Call LOGOS CIO to confirm:**

- Number of stories (4, 5, 6, or 7?)
- Site coverage % (65% or 70%?)
- Average unit size (450 or 481 sqft?)
- Demolition assumption correct?
