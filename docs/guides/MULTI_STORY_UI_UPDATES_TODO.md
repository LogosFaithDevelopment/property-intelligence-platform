# Multi-Story Scenarios & UI Updates - TODO

**Date:** October 10, 2025  
**Status:** In Progress - Needs Implementation

---

## COMPLETED SO FAR:

✅ Database migration (demolish + additional addresses)
✅ Frontend form (collect multiple addresses)
✅ Backend enrichment (fetch all addresses, combine lot sizes)
✅ TypeScript types (additional_addresses in ChurchSubmissionFormData)
✅ API payload transformation (includes demolish + additional_addresses)
✅ Submission successful with combined data (20,219 sqft total)

---

## REMAINING WORK:

### 1. Backend: AI Assessment - Generate 3/4/5 Story Scenarios

**File:** `backend/app/services/ai_assessment.py`

**Current State:**

- Hardcoded `stories = 4`
- Only generates single 4-story scenario
- Returns one set of units/IRR/NOI

**Needed:**
Create method `_calculate_multi_story_scenarios()` that returns:

```python
{
  "3_story": {
    "units": 82,
    "buildable_sqft": 39,427,
    "irr_percent": 21.2,
    "noi": $1,463,900,
    "development_cost": $23,123,240,
    "equity_required": $6,936,972
  },
  "4_story": {
    "units": 109,  # Current calculation
    "buildable_sqft": 52,569,
    "irr_percent": 23.5,  # RECOMMENDED
    "noi": $1,951,866,
    "development_cost": $30,831,086,
    "equity_required": $9,249,326
  },
  "5_story": {
    "units": 136,
    "buildable_sqft": 65,712,
    "irr_percent": 24.8,
    "noi": $2,439,833,
    "development_cost": $38,538,932,
    "equity_required": $11,561,680
  },
  "recommended": "4_story",  # Highest IRR or closest to 100 units
  "recommended_reason": "Optimal balance of IRR (23.5%) and unit count (109 units)"
}
```

**Implementation Steps:**

1. Modify `_calculate_unit_capacity()` to accept `stories` parameter
2. Create loop: `for stories in [3, 4, 5]`
3. For each scenario, calculate units, then call `_calculate_irr_analysis()`
4. Compare IRRs, pick recommended scenario
5. Store all 3 scenarios in `financial_projections` JSON field

---

### 2. Frontend: Assessment Page - Display Multi-Story Table

**File:** `frontend/src/app/admin/submissions/[id]/assessment/page.tsx`

**Add Section:** Development Scenarios Comparison

```tsx
<div className="bg-white rounded-lg shadow p-6">
  <h3 className="text-xl font-semibold mb-4">Development Scenarios</h3>

  <table className="w-full">
    <thead>
      <tr className="border-b">
        <th className="text-left py-2">Scenario</th>
        <th className="text-right py-2">Units</th>
        <th className="text-right py-2">IRR</th>
        <th className="text-right py-2">NOI (Year 1)</th>
        <th className="text-right py-2">Development Cost</th>
        <th className="text-right py-2">Equity Required</th>
      </tr>
    </thead>
    <tbody>
      <tr className={3_story.recommended ? 'bg-green-50' : ''}>
        <td>3-Story</td>
        <td className="text-right">82 units</td>
        <td className="text-right">21.2%</td>
        <td className="text-right">$1.46M</td>
        <td className="text-right">$23.1M</td>
        <td className="text-right">$6.9M</td>
      </tr>
      <tr className={4_story.recommended ? 'bg-green-50' : ''}>
        <td>4-Story ⭐</td>
        <td className="text-right font-bold">109 units</td>
        <td className="text-right font-bold">23.5%</td>
        <td className="text-right font-bold">$1.95M</td>
        <td className="text-right font-bold">$30.8M</td>
        <td className="text-right font-bold">$9.2M</td>
      </tr>
      <tr className={5_story.recommended ? 'bg-green-50' : ''}>
        <td>5-Story</td>
        <td className="text-right">136 units</td>
        <td className="text-right">24.8%</td>
        <td className="text-right">$2.44M</td>
        <td className="text-right">$38.5M</td>
        <td className="text-right">$11.6M</td>
      </tr>
    </tbody>
  </table>

  <div className="mt-4 p-4 bg-blue-50 rounded">
    <strong>Recommended:</strong> 4-Story Development
    <br />
    <span className="text-sm text-gray-600">
      Optimal balance of IRR (23.5%) and unit count (109 units).
      Meets LOGOS target of 20% IRR with manageable equity requirement.
    </span>
  </div>
</div>
```

---

### 3. Frontend: Assessment Page - Rich Recommendation Section

**Current:** Generic template text with "Schedule site visit" placeholder

**Needed:** Data-driven insights

```tsx
<div className='bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6'>
  <div className='flex items-start gap-4'>
    <div className='flex-shrink-0'>
      <CheckCircle className='h-12 w-12 text-green-600' />
    </div>
    <div>
      <h3 className='text-2xl font-bold text-green-800 mb-2'>
        STRONGLY RECOMMENDED FOR DEVELOPMENT
      </h3>
      <p className='text-lg mb-4'>
        This property scores{' '}
        <strong>
          {overall_score}/100 (Grade {grade})
        </strong>
        , placing it in the <strong>top {percentile}%</strong> of LOGOS
        opportunities.
      </p>

      <div className='grid grid-cols-3 gap-4 mb-4'>
        <div className='bg-white p-3 rounded'>
          <div className='text-sm text-gray-600'>IRR (10-year)</div>
          <div className='text-xl font-bold text-green-600'>{irr}%</div>
          <div className='text-xs text-gray-500'>Target: 20%</div>
        </div>
        <div className='bg-white p-3 rounded'>
          <div className='text-sm text-gray-600'>Units (4-story)</div>
          <div className='text-xl font-bold'>{units}</div>
          <div className='text-xs text-gray-500'>Range: 40-140</div>
        </div>
        <div className='bg-white p-3 rounded'>
          <div className='text-sm text-gray-600'>Equity Required</div>
          <div className='text-xl font-bold'>${equity_required}M</div>
          <div className='text-xs text-gray-500'>30% of ${dev_cost}M</div>
        </div>
      </div>

      <div className='mb-4'>
        <h4 className='font-semibold mb-2'>Key Strengths:</h4>
        <ul className='list-disc list-inside space-y-1 text-sm'>
          <li>
            Combined lot size: {lot_size} sqft across {address_count} parcels
          </li>
          <li>Strong market demand: {census_data_point}</li>
          <li>Excellent financial returns: {irr}% IRR exceeds 20% target</li>
          <li>Congregation approval: {approval_status}</li>
          <li>Manageable risk: {risk_score}/100 risk score</li>
        </ul>
      </div>

      <div className='mb-4'>
        <h4 className='font-semibold mb-2'>Risk Factors:</h4>
        <ul className='list-disc list-inside space-y-1 text-sm text-amber-700'>
          <li>
            {flood_zone}: Requires ${flood_mitigation_cost} mitigation
          </li>
          <li>{other_risk_factors_from_assessment}</li>
        </ul>
      </div>

      <div>
        <h4 className='font-semibold mb-2'>Recommended Next Steps:</h4>
        <ol className='list-decimal list-inside space-y-1 text-sm'>
          <li>
            <strong>Site Visit:</strong> Schedule walkthrough with LOGOS team to
            verify buildable space
          </li>
          <li>
            <strong>Environmental Assessment:</strong> Phase I ESA and flood
            zone verification
          </li>
          <li>
            <strong>Architectural Planning:</strong> Engage architect for
            4-story design (109 units)
          </li>
          <li>
            <strong>Community Engagement:</strong> Hold congregation meeting to
            review financials
          </li>
          <li>
            <strong>Due Diligence:</strong> Title search, zoning confirmation,
            utility capacity check
          </li>
        </ol>
      </div>
    </div>
  </div>
</div>
```

---

### 4. Frontend: Submission Detail Page - Property Data

**File:** `frontend/src/app/admin/submissions/[id]/page.tsx`

**Add to Property Section:**

```tsx
{
  /* Combined Lot Size (if multi-address) */
}
{
  property.combined_lot_size_sqft && (
    <div className='border-l-4 border-blue-500 pl-4 bg-blue-50 p-3'>
      <div className='text-sm text-gray-600'>Combined Lot Size</div>
      <div className='text-lg font-semibold'>
        {property.combined_lot_size_sqft.toLocaleString()} sqft
      </div>
      <div className='text-xs text-gray-500'>
        Across {1 + (property.additional_addresses?.length || 0)} addresses
      </div>
    </div>
  );
}

{
  /* Additional Addresses */
}
{
  property.additional_addresses && property.additional_addresses.length > 0 && (
    <div>
      <div className='text-sm font-semibold text-gray-700 mb-2'>
        Additional Addresses:
      </div>
      {property.additional_addresses.map((addr, idx) => (
        <div key={idx} className='text-sm text-gray-600 ml-4'>
          • {addr.address}, {addr.city}, {addr.state} {addr.zip_code}
        </div>
      ))}
    </div>
  );
}

{
  /* Parcel Numbers */
}
{
  property.parcel_numbers && (
    <div>
      <div className='text-sm text-gray-600'>Parcel Numbers</div>
      <div className='text-sm font-mono'>{property.parcel_numbers}</div>
    </div>
  );
}

{
  /* Demolish Flag */
}
{
  property.demolish_all_structures && (
    <div className='bg-amber-50 p-2 rounded border border-amber-200'>
      <span className='text-sm text-amber-800'>
        ⚠️ Plans to demolish all existing structures
      </span>
    </div>
  );
}
```

---

### 5. Frontend: Submission Detail Page - Fix N/A Values

**Current:** Bottom metrics showing "N/A"

**Fix:** Extract from financial_projections JSON

```tsx
<div className='grid grid-cols-4 gap-4'>
  <div className='bg-white p-4 rounded shadow'>
    <div className='text-sm text-gray-600'>Units (4-story)</div>
    <div className='text-2xl font-bold'>
      {assessment?.financial_projections?.unit_capacity?.feasible_units ||
        'N/A'}
    </div>
  </div>

  <div className='bg-white p-4 rounded shadow'>
    <div className='text-sm text-gray-600'>10-Year IRR</div>
    <div className='text-2xl font-bold text-green-600'>
      {assessment?.financial_projections?.irr_percent
        ? `${assessment.financial_projections.irr_percent}%`
        : 'N/A'}
    </div>
  </div>

  <div className='bg-white p-4 rounded shadow'>
    <div className='text-sm text-gray-600'>Year 1 NOI</div>
    <div className='text-2xl font-bold'>
      {assessment?.financial_projections?.revenue_projections?.noi_formatted ||
        'N/A'}
    </div>
  </div>

  <div className='bg-white p-4 rounded shadow'>
    <div className='text-sm text-gray-600'>Development Cost</div>
    <div className='text-2xl font-bold'>
      {assessment?.financial_projections?.adjusted_development_cost_formatted ||
        'N/A'}
    </div>
  </div>
</div>
```

---

### 6. UI Fixes:

#### A) View Full AI Button

**File:** `frontend/src/app/admin/submissions/[id]/page.tsx`

```tsx
<Button
  onClick={() => router.push(`/admin/submissions/${id}/assessment`)}
  className="w-full py-4 text-lg bg-blue-600 hover:bg-blue-700"  {/* Changed */}
>
  View Full AI Assessment
</Button>
```

#### B) Land Use Text Wrapping

Find the land_use display and add:

```tsx
<div className='text-sm text-gray-600 break-words max-w-xs'>
  {property.land_use || 'N/A'}
</div>
```

Or truncate:

```tsx
<div className='text-sm text-gray-600'>
  {property.land_use?.length > 40
    ? property.land_use.substring(0, 40) + '...'
    : property.land_use || 'N/A'}
</div>
```

---

## PRIORITY ORDER:

1. **Backend: AI Assessment Multi-Story** (30-45 min) - Generates the data
2. **Frontend: Assessment Page Table** (20 min) - Displays scenarios
3. **Frontend: Rich Recommendation** (30 min) - Data-driven insights
4. **Frontend: Submission Page Metrics** (15 min) - Fix N/A values
5. **UI Fixes** (10 min) - Button styling, text wrapping

---

## TESTING CHECKLIST:

- [ ] Re-submit Manchester property (or run assessment manually)
- [ ] Verify 3 scenarios appear in financial_projections JSON
- [ ] Check assessment page shows 3-row table
- [ ] Verify recommended scenario is highlighted
- [ ] Confirm submission detail page shows combined lot size
- [ ] Check all N/A values replaced with actual data
- [ ] Test button styling looks good
- [ ] Verify land use text doesn't overflow

---

**Status:** Ready for implementation  
**Estimated Time:** 2-3 hours total
