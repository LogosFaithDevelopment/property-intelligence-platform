# Smarty Data Analysis - Manchester Property

## Goal: Find why LOGOS fits 134 units vs our 62 units

---

## RAW DATA FROM DATABASE

**Property:** 709 W Manchester Ave, Los Angeles, CA 90044

### LOT INFORMATION

```json
"lot": {
  "size_sqft": 13708,
  "size_acres": 0.3146924,
  "lot_numbers": "182,183",
  "parcel_number": "6032-015-042"
}
```

### BUILDING INFORMATION

```json
"building": {
  "size_sqft": 2488,
  "year_built": "1946",
  "stories": null,
  "construction_type": "wood",
  "floor_1_sqft": 0,
  "floor_2_sqft": 0
}
```

### AVAILABLE BUILD SPACE

```json
"available_build_space": {
  "sqft": 11220,
  "acres": 0.2576,
  "qualifies_for_logos": true,
  "minimum_required": 10000,
  "calculation": "13,708 sqft (lot) - 2,488 sqft (building) = 11,220 sqft"
}
```

### RAW PROPERTY DATA (Full Fields)

```json
"acres": "0.3146924",
"lot_sqft": "13708.00",
"lot_1": "182,183",
"parcel_raw_number": "6032-015-042",
"gross_sqft": "2488",
"building_sqft": "2488",
"stories_number": "1",
```

---

## CRITICAL FINDING: MULTI-PARCEL PROPERTY

### Evidence of 2 Separate Lots

1. **`lot_numbers`**: "182,183" ← TWO lot numbers
2. **`lot_sqft`**: 13,708 sqft ← COMBINED total for both lots
3. **Legal description**: "Lots 182 and 183"

---

## THE PROBLEM WITH OUR CALCULATION

### What We're Currently Doing:

```
Available space: 11,220 sqft (COMBINED for both lots)
Site coverage: 65%
Stories: 4
Avg unit size: 481 sqft

Units = (11,220 × 0.65 × 4) ÷ 481 = 62 units TOTAL
```

### What LOGOS Is Actually Doing:

**They're developing EACH lot as a SEPARATE 4-story building!**

```
LOT 182:
  Lot size: ~6,854 sqft (half of 13,708)
  Available: ~5,610 sqft (half of 11,220)
  Footprint: 5,610 × 0.65 = 3,647 sqft
  Buildable: 3,647 × 4 = 14,588 sqft
  Units: 14,588 ÷ 481 = 30 units

LOT 183:
  Lot size: ~6,854 sqft (half of 13,708)
  Available: ~5,610 sqft (half of 11,220)
  Footprint: 5,610 × 0.65 = 3,647 sqft
  Buildable: 3,647 × 4 = 14,588 sqft
  Units: 14,588 ÷ 481 = 30 units

TOTAL: 60 units (still short of 134!)
```

---

## WAIT - RECALCULATING WITH ACTUAL LOGOS NUMBERS

### LOGOS Actual: 134 units on 2 parcels = 67 units per parcel

Let me reverse-engineer their calculation:

```
67 units per parcel × 481 sqft avg = 32,227 sqft buildable per parcel
32,227 ÷ 4 stories = 8,057 sqft footprint per parcel
8,057 ÷ 6,854 sqft lot = 117.5% site coverage (!!)
```

**That's impossible - over 100% coverage!**

---

## ALTERNATIVE EXPLANATIONS

### Option 1: Different Average Unit Size

```
If LOGOS uses smaller units:
67 units per parcel
4 stories
Site coverage: 65%

Footprint: 6,854 × 0.65 = 4,455 sqft
Buildable: 4,455 × 4 = 17,820 sqft
Avg unit size: 17,820 ÷ 67 = 266 sqft per unit

THIS WOULD BE MICRO-UNITS! (too small for affordable housing)
```

### Option 2: Higher Site Coverage

```
If LOGOS uses 85% coverage (more aggressive):
Footprint: 6,854 × 0.85 = 5,826 sqft
Buildable: 5,826 × 4 = 23,304 sqft
Avg unit size: 23,304 ÷ 67 = 348 sqft per unit

STILL TOO SMALL for our unit mix!
```

### Option 3: More Stories

```
If LOGOS builds 5 stories per building:
Footprint: 6,854 × 0.65 = 4,455 sqft
Buildable: 4,455 × 5 = 22,275 sqft
Avg unit size: 22,275 ÷ 67 = 332 sqft per unit

STILL TOO SMALL!
```

### Option 4: TALLER BUILDINGS (Most Likely!)

```
If LOGOS builds 6 stories per building:
Footprint: 6,854 × 0.65 = 4,455 sqft
Buildable: 4,455 × 6 = 26,730 sqft
Avg unit size: 26,730 ÷ 67 = 399 sqft per unit

CLOSER! But still less than our 481 sqft
```

### Option 5: Different Unit Mix (Smaller Units)

```
If LOGOS uses MORE studios (30%) and fewer 2BDs (15%):
Studios: 30% × 325 sqft = 97.5
1BD: 55% × 450 sqft = 247.5
2BD: 15% × 675 sqft = 101.25
Weighted avg = 446 sqft per unit

With 6 stories:
Buildable: 4,455 × 6 = 26,730 sqft
Units: 26,730 ÷ 446 = 60 units per parcel
Total: 120 units (still short of 134!)
```

---

## THE MOST LIKELY ANSWER

### LOGOS is probably using:

1. **TWO separate 6-story buildings** (not 4-story)
2. **Higher site coverage** (~75-80%)
3. **Smaller average unit size** (~400 sqft)

### Let me test this:

```
LOT 182 (6 stories, 75% coverage, 400 sqft avg):
  Footprint: 6,854 × 0.75 = 5,141 sqft
  Buildable: 5,141 × 6 = 30,846 sqft
  Units: 30,846 ÷ 400 = 77 units

LOT 183 (6 stories, 75% coverage, 400 sqft avg):
  Footprint: 6,854 × 0.75 = 5,141 sqft
  Buildable: 5,141 × 6 = 30,846 sqft
  Units: 30,846 ÷ 400 = 77 units

TOTAL: 154 units (CLOSE to 134!)
```

---

## DATA WE'RE MISSING FROM SMARTY

Looking at all Smarty fields, we DO NOT have:

- ❌ Individual lot sizes (only combined: 13,708 sqft)
- ❌ Separate parcel information for lots 182 vs 183
- ❌ Maximum allowed height/stories (zoning data)
- ❌ Actual site coverage limits from zoning

We DO have:

- ✅ Combined lot size: 13,708 sqft
- ✅ Lot numbers: "182,183" (indicates 2 lots)
- ✅ Existing building: 2,488 sqft
- ✅ Zoning: "Lac2"

---

## CONCLUSION

**The Smarty API returns COMBINED lot data for multi-parcel properties.**

Our system needs to:

1. **Detect when lot_numbers contains multiple lots** (e.g., "182,183")
2. **Count the number of lots** (split by comma)
3. **Divide the lot_sqft by number of lots** to get size per lot
4. **Calculate units PER LOT**, then multiply by number of lots

### Current Calculation (WRONG for multi-parcel):

```python
units = (total_lot_sqft × coverage × stories) ÷ avg_unit_size
```

### Correct Calculation (for multi-parcel):

```python
num_lots = count(lot_numbers.split(','))
sqft_per_lot = total_lot_sqft / num_lots
units_per_lot = (sqft_per_lot × coverage × stories) ÷ avg_unit_size
total_units = units_per_lot × num_lots
```

### For Manchester:

```python
num_lots = 2
sqft_per_lot = 13,708 / 2 = 6,854 sqft
available_per_lot = 11,220 / 2 = 5,610 sqft
units_per_lot = (5,610 × 0.65 × 4) ÷ 481 = 30 units
total_units = 30 × 2 = 60 units

# Still short of 134! LOGOS must be using:
# - 6 stories instead of 4
# OR
# - Higher site coverage (75%+)
# OR
# - Smaller units (400 sqft avg)
```

---

## RECOMMENDED FIX

Update `_calculate_unit_capacity()` in `ai_assessment.py`:

```python
# Detect multi-parcel properties
lot_numbers = smarty_data.get('lot', {}).get('lot_numbers', '')
num_lots = len(lot_numbers.split(',')) if lot_numbers else 1

# Divide lot size by number of lots
total_lot_sqft = lot_size
lot_sqft_per_parcel = total_lot_sqft / num_lots

# Calculate units per lot
units_per_lot = (lot_sqft_per_parcel × coverage × stories) / avg_unit_size

# Total units = units per lot × number of lots
total_units = units_per_lot × num_lots
```

This will give us:

- **60-62 units** for Manchester (with 4 stories, 65% coverage)
- Still need to understand LOGOS's actual assumptions (likely 6 stories or higher coverage)
