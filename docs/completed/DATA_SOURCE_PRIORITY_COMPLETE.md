# AI Assessment Data Source Priority - Complete Summary

**Date**: October 8, 2025  
**Status**: ✅ BACKEND COMPLETE | ⏳ FRONTEND PENDING  
**Priority**: HIGH - Core assessment logic change

---

## 🎯 Executive Summary

**Changed the AI assessment system to prioritize user-specified available build space over Smarty calculated data**, while maintaining both values side-by-side for comparison and quality assurance.

**Rationale**: Users have local knowledge about their properties (demolitions, restrictions, easements, surveys) that automated calculations cannot capture.

**Impact**: More accurate assessments that trust user expertise while maintaining automated cross-checks.

---

## 📊 Before vs After

### Data Source Priority

| Priority | Before (Smarty First)       | After (User First)         |
| -------- | --------------------------- | -------------------------- |
| 1st      | Smarty calculated (trusted) | User-specified (trusted)   |
| 2nd      | User-specified (verify)     | Smarty calculated (verify) |
| 3rd      | Total lot size (verify)     | Total lot size (verify)    |

### Verification Requirements

| Source            | Before                   | After                            |
| ----------------- | ------------------------ | -------------------------------- |
| User-specified    | ⚠️ Requires verification | ✅ Trusted                       |
| Smarty calculated | ✅ Trusted               | ⚠️ User confirmation recommended |
| Total lot size    | ⚠️ Requires verification | ⚠️ Requires verification         |

---

## 🔧 Technical Implementation

### File Modified

- `backend/app/services/ai_assessment.py` (lines ~645-685)

### Code Changes

#### Priority Logic (lines 663-687)

```python
# Check user-specified FIRST
if assessment.available_build_sqft and assessment.available_build_sqft > 0:
    lot_size_sqft = assessment.available_build_sqft
    build_space_source = "user_specified"
    requires_verification = False  # Trust user input

    # Compare with Smarty if available
    if smarty_available_space:
        difference = lot_size_sqft - smarty_available_space
        pct_diff = (difference / smarty_available_space) * 100

        # Flag large discrepancies (>20%)
        if abs(pct_diff) > 20:
            logger.warning("Large discrepancy detected")
            verification_note = "Consider verification call..."
```

#### Smart Comparison (lines 673-684)

```python
# Log comparison with Smarty data
logger.info(f"✅ Using user-specified: {lot_size_sqft:,} sq ft")
logger.info(f"   Smarty calculated: {smarty_available_space:,} sq ft")
logger.info(f"   Difference: {difference:+,} sq ft / {pct_diff:+.1f}%")

# Flag significant discrepancies
if abs(pct_diff) > 20:
    logger.warning("⚠️ Large discrepancy detected - may warrant verification call")
```

#### Fallback Behavior (lines 687-700)

```python
# Only use Smarty if user didn't provide value
elif smarty_available_space and smarty_available_space > 0:
    lot_size_sqft = smarty_available_space
    build_space_source = "smarty_calculated"
    requires_verification = True  # Request user confirmation

    verification_note = "User did not specify - recommend confirmation"
```

---

## 📋 Data Flow

### Scenario 1: User Provides Value (Most Common)

```
Input Flow:
┌─────────────────────┐
│ User Form           │
│ Available Space:    │
│ 10,000 sqft        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ AI Assessment       │
│ Priority Check      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Use: 10,000 sqft   │
│ Source: user_specified │
│ Verify: No         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Compare with Smarty │
│ 11,220 sqft         │
│ Diff: -10.9%        │
└─────────────────────┘
```

**Outcome**: Use 10,000 sqft, no verification needed, show comparison

---

### Scenario 2: Large Discrepancy (>20%)

```
Input Flow:
┌─────────────────────┐
│ User: 15,000 sqft  │
│ Smarty: 10,000 sqft│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Calculate Diff      │
│ +5,000 sqft (+50%) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ ⚠️ FLAG ALERT       │
│ Large discrepancy   │
│ May need call       │
└─────────────────────┘
```

**Outcome**: Use 15,000 sqft, but flag for review

---

### Scenario 3: No User Input

```
Input Flow:
┌─────────────────────┐
│ User: (empty)      │
│ Smarty: 11,220 sqft│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Fallback to Smarty │
│ 11,220 sqft         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ ⚠️ REQUEST          │
│ User confirmation   │
│ recommended         │
└─────────────────────┘
```

**Outcome**: Use 11,220 sqft, request user to confirm

---

## 🎨 Frontend Requirements

### 1. Assessment Results Display

```tsx
<div className='available-space-comparison'>
  <h3>Available Build Space</h3>

  {/* Primary Value */}
  <div className='primary-value'>
    <CheckCircle className='text-green-500' />
    <span className='font-bold'>User Specified:</span>
    <span>10,000 sqft</span>
    <Badge>Used for calculations</Badge>
  </div>

  {/* Comparison Value */}
  <div className='comparison-value'>
    <Info className='text-blue-500' />
    <span>Smarty Calculated:</span>
    <span>11,220 sqft</span>
    <Badge variant='outline'>For comparison</Badge>
  </div>

  {/* Difference */}
  <div className='difference'>
    <span>Difference:</span>
    <span className='text-muted-foreground'>-1,220 sqft (-10.9%)</span>
  </div>
</div>
```

### 2. Large Discrepancy Alert

```tsx
{
  pct_diff > 20 && (
    <Alert variant='warning'>
      <AlertTriangle className='h-4 w-4' />
      <AlertTitle>Large Discrepancy Detected</AlertTitle>
      <AlertDescription>
        User specified {userValue} sqft vs Smarty calculated {smartyValue} sqft
        ({Math.abs(pct_diff).toFixed(1)}% difference).
        <Button variant='outline' size='sm' className='mt-2'>
          Schedule Verification Call
        </Button>
      </AlertDescription>
    </Alert>
  );
}
```

### 3. No User Input Warning

```tsx
{
  source === 'smarty_calculated' && (
    <Alert variant='info'>
      <Info className='h-4 w-4' />
      <AlertTitle>Using Calculated Value</AlertTitle>
      <AlertDescription>
        User did not specify available space. Using Smarty calculation of{' '}
        {smartyValue} sqft.
        <Button variant='link' size='sm'>
          Request User Confirmation
        </Button>
      </AlertDescription>
    </Alert>
  );
}
```

---

## 🧪 Testing Results

### Test Property: Assessment #50

**Property**: 709 Manchester Ave, Los Angeles, CA 90044  
**Church**: St Rest Baptist Church

#### Input Data

```
User Specified:     10,000 sqft
Smarty Calculated:  11,220 sqft
Total Lot Size:     13,708 sqft
```

#### Before (Smarty Priority)

```
Used:         11,220 sqft
Source:       smarty_calculated
Units:        45
Verification: Not needed
```

#### After (User Priority)

```
Used:         10,000 sqft
Source:       user_specified
Units:        41
Verification: Not needed
Difference:   -1,220 sqft (-10.9%)
```

#### Analysis

- ✅ User value takes priority
- ✅ Comparison logged
- ✅ No verification flag (within 20% threshold)
- ✅ Slightly more conservative unit count (41 vs 45)
- ✅ Still meets 40-unit minimum

---

## 💡 Key Insights

### 1. Why User Priority Makes Sense

**Users Know:**

- Recent demolitions or additions
- Parking requirements specific to jurisdiction
- Setback restrictions from recent surveys
- Easements and encumbrances from title reports
- Protected areas (trees, historical features)
- Access constraints
- Utility locations

**Smarty Cannot Know:**

- Recent changes (demolitions last 6 months)
- Local zoning variations
- Site-specific restrictions
- Covenant limitations
- Irregular lot shapes
- Shared access agreements

### 2. When to Flag for Verification

**Large Discrepancy (>20% difference)**

- Possible data entry error
- Possible Smarty calculation error
- Possible lot combination issue
- Possible recent changes

**User Didn't Provide Value**

- Request confirmation of Smarty value
- Ask if they have more accurate data
- Suggest professional survey if needed

### 3. Benefits of Dual Display

**For Users:**

- See that their input is valued
- Get automated sanity check
- Understand calculation basis
- Identify potential issues early

**For Admin:**

- Quality assurance mechanism
- Catch data entry errors
- Document decision trail
- Improve future calculations

---

## 📈 Impact Analysis

### Assessment Accuracy

- ✅ **Improved**: Uses best available data (user knowledge)
- ✅ **Validated**: Automated cross-check catches errors
- ✅ **Transparent**: Both values visible for review

### User Experience

- ✅ **Trusted**: User input is primary source
- ✅ **Validated**: Get confirmation from automated data
- ✅ **Informed**: See comparison to understand discrepancies

### Admin Workflow

- ✅ **Efficient**: Only flag significant discrepancies
- ✅ **Clear**: Easy to identify verification needs
- ✅ **Documented**: Audit trail of data sources

### Data Quality

- ✅ **Learning**: Track discrepancies over time
- ✅ **Improving**: Refine Smarty calculations
- ✅ **Reporting**: Analytics on data accuracy

---

## 🚀 Implementation Roadmap

### ✅ Phase 1: Backend (COMPLETE)

- [x] Update priority logic in AI assessment
- [x] Add smart comparison logging
- [x] Implement discrepancy detection (>20%)
- [x] Store both values for comparison
- [x] Update verification flags
- [x] Test with Assessment #50

### ⏳ Phase 2: Frontend (PENDING)

- [ ] Update assessment results display
- [ ] Add comparison visualization
- [ ] Implement discrepancy alerts
- [ ] Add "Request Confirmation" workflow
- [ ] Show data source badges

### 📋 Phase 3: Admin Dashboard (PENDING)

- [ ] Add "Discrepancy > 20%" filter
- [ ] Show comparison in detail view
- [ ] Add manual override capability
- [ ] Track verification outcomes
- [ ] Generate data quality reports

### 📧 Phase 4: Workflow (PENDING)

- [ ] Create "Request Confirmation" email template
- [ ] Develop verification call script
- [ ] Implement "Mark as Verified" action
- [ ] Add verification history tracking
- [ ] Schedule follow-up reminders

### 📊 Phase 5: Analytics (FUTURE)

- [ ] Track user vs Smarty accuracy
- [ ] Identify discrepancy patterns
- [ ] Improve Smarty calculation logic
- [ ] Generate monthly data quality reports
- [ ] ML model for outlier detection

---

## 🔍 Edge Cases

### Edge Case 1: User Value = 0

```python
if assessment.available_build_sqft and assessment.available_build_sqft > 0:
    # This condition handles 0 as "not provided"
```

**Outcome**: Falls back to Smarty data

### Edge Case 2: Negative Smarty Value

```python
if smarty_available_space and smarty_available_space > 0:
    # Filters out negative/invalid values
```

**Outcome**: Falls back to total lot size

### Edge Case 3: Both Values Missing

```python
else:
    # Use total lot size as last resort
    lot_size_sqft = total_lot_size
    requires_verification = True
```

**Outcome**: Request user confirmation

### Edge Case 4: Smarty Exactly Matches User

```python
if smarty_available_space:
    difference = lot_size_sqft - smarty_available_space
    # 0% difference - perfect match!
```

**Outcome**: High confidence, no flag

---

## 📊 Expected Outcomes

### Immediate Benefits

- ✅ More accurate assessments (trust user knowledge)
- ✅ Better user experience (input is valued)
- ✅ Quality assurance (automated cross-check)

### Medium-Term Benefits

- 📈 Identify Smarty calculation issues
- 📈 Improve data quality over time
- 📈 Build trust with users

### Long-Term Benefits

- 🎯 ML model to predict discrepancies
- 🎯 Automated suggestions for verification
- 🎯 Best-in-class property assessment

---

## 🔗 Related Documentation

- `USER_SPECIFIED_PRIORITY_UPDATE.md` - Full technical documentation
- `USER_SPECIFIED_PRIORITY_QUICK_REF.md` - Quick reference guide
- `UNIT_CALCULATION_FIXED_COMPLETE.md` - Unit calculation fixes
- `AVAILABLE_BUILD_SPACE_VERIFICATION_COMPLETE.md` - Verification workflow
- `AI_ASSESSMENT_BUG_FIXES_COMPLETE.md` - Previous assessment fixes

---

## 📝 Summary

### What Changed

User-specified available build space is now the **primary, trusted source** for AI assessments.

### Why Changed

Users have **local knowledge** that automated calculations cannot capture.

### How It Works

Use user input first, compare with Smarty data, flag large discrepancies (>20%).

### What's Next

Frontend visualization, admin dashboard, verification workflow, analytics.

---

**Status**: ✅ Backend implementation complete  
**Next**: Frontend updates to display comparison data  
**Impact**: HIGH - Core assessment logic improvement  
**Priority**: Complete frontend in next sprint

---

_Last Updated: October 8, 2025_
