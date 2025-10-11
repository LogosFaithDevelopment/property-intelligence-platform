# User-Specified Available Build Space Priority Update

**Date**: October 8, 2025  
**Status**: ✅ COMPLETE  
**Impact**: Critical - Changes AI assessment data source priority

---

## 🎯 Objective

Update the AI assessment system to **prioritize user-specified available build space** over Smarty calculated data, while maintaining both values for side-by-side comparison and verification.

---

## 🔄 What Changed

### Before (Smarty Priority)

```
Priority Order:
1. Smarty calculated available space (TRUSTED - no verification)
2. User-specified space (REQUIRES VERIFICATION)
3. Total lot size (REQUIRES VERIFICATION)
```

### After (User Priority)

```
Priority Order:
1. User-specified available space (TRUSTED - user knows their property)
2. Smarty calculated space (FALLBACK - for comparison)
3. Total lot size (LAST RESORT - requires verification)
```

---

## 📋 Implementation Details

### File Modified

- `backend/app/services/ai_assessment.py` (lines ~645-685)

### Key Changes

#### 1. **Priority Logic Reversal**

```python
# NEW: User-specified takes priority
if assessment.available_build_sqft and assessment.available_build_sqft > 0:
    lot_size_sqft = assessment.available_build_sqft
    build_space_source = "user_specified"
    requires_verification = False  # Trust user input
    using_available_space = True
```

#### 2. **Smart Comparison Logging**

When both user and Smarty data exist:

```python
if smarty_available_space and smarty_available_space > 0:
    difference = lot_size_sqft - smarty_available_space
    pct_diff = (difference / smarty_available_space) * 100

    # Flag significant discrepancies (>20% difference)
    if abs(pct_diff) > 20:
        logger.warning("Large discrepancy detected - may warrant verification call")
```

#### 3. **Verification Flags**

- **User-specified**: No verification needed (trusted)
- **Smarty fallback**: Flag for user confirmation
- **Total lot fallback**: Flag for user confirmation

---

## 🔍 Comparison Display

Both values are still stored and displayed for verification:

```python
"user_specified_available_sqft": assessment.available_build_sqft,
"smarty_calculated_available_sqft": smarty_available_space,
"used_value_sqft": lot_size_sqft,
"used_value_source": build_space_source,
"requires_manual_verification": requires_verification,
"verification_note": verification_note
```

---

## 📊 Example Scenarios

### Scenario 1: User Provides Value (Most Common)

```
Input:
- User specified: 10,000 sqft
- Smarty calculated: 11,220 sqft

Output:
✅ Using user-specified: 10,000 sqft
   Smarty calculated: 11,220 sqft (difference: -1,220 sqft / -10.9%)

Result: Use 10,000 sqft, no verification needed
```

### Scenario 2: Large Discrepancy Detected

```
Input:
- User specified: 15,000 sqft
- Smarty calculated: 10,000 sqft

Output:
✅ Using user-specified: 15,000 sqft
   Smarty calculated: 10,000 sqft (difference: +5,000 sqft / +50.0%)
   ⚠️ Large discrepancy detected - may warrant verification call

Result: Use 15,000 sqft, but flag for review
```

### Scenario 3: No User Input (Fallback to Smarty)

```
Input:
- User specified: (none)
- Smarty calculated: 11,220 sqft

Output:
⚠️ Using Smarty calculated: 11,220 sqft - USER CONFIRMATION RECOMMENDED
   Total lot size: 13,708 sqft

Result: Use 11,220 sqft, request user confirmation
```

### Scenario 4: No Data Available (Last Resort)

```
Input:
- User specified: (none)
- Smarty calculated: (none)
- Total lot size: 13,708 sqft

Output:
⚠️ Using total lot size: 13,708 sqft - USER CONFIRMATION REQUIRED

Result: Use 13,708 sqft, call user to verify actual available space
```

---

## 🎯 Rationale

### Why Prioritize User Input?

1. **Local Knowledge**: Users know about:

   - Recent demolitions
   - Parking requirements
   - Setback restrictions
   - Easements and encumbrances
   - Protected areas (historical, environmental)

2. **Real-World Accuracy**: User values often reflect:

   - Architect/engineer assessments
   - Zoning pre-application feedback
   - Site surveys
   - Title report findings

3. **Smarty Limitations**: Automated calculations may miss:
   - Recent property changes
   - Multiple parcel combinations
   - Covenant restrictions
   - Irregular lot shapes
   - Access issues

### Why Keep Both Values?

1. **Sanity Check**: Large discrepancies warrant investigation
2. **Data Quality**: Helps identify data entry errors
3. **Audit Trail**: Documents decision-making process
4. **Learning**: Improves future automated assessments

---

## 📈 Impact on Assessment #50 (709 Manchester)

### Before (Smarty Priority)

```
Used: 11,220 sqft (Smarty calculated)
Units: 45
Source: smarty_calculated
Verification: Not needed
```

### After (User Priority)

```
Used: 10,000 sqft (User specified)
Units: 41
Source: user_specified
Verification: Not needed
Comparison: User 10,000 vs Smarty 11,220 (-10.9% difference)
```

**Result**: Slightly more conservative unit count, but trusts user's local knowledge.

---

## 🔧 Frontend Integration Points

### Display Requirements

1. **Assessment Results Page**:

   ```
   Available Build Space:
   ✓ User Specified: 10,000 sqft (used for calculations)
   ℹ Smarty Calculated: 11,220 sqft (for comparison)

   Difference: -1,220 sqft (-10.9%)
   ```

2. **Admin Review Panel**:

   ```
   Data Source: user_specified
   Verification Status: ✅ Trusted

   [Show Comparison] button
   ```

3. **Alert for Large Discrepancies**:

   ```
   ⚠️ Large discrepancy detected
   User: 15,000 sqft vs Smarty: 10,000 sqft (+50%)

   Consider verification call to confirm accurate value.
   [Schedule Call] [Mark as Verified]
   ```

---

## ✅ Testing Checklist

- [x] Updated priority logic in `_analyze_financials()`
- [x] Added smart comparison logging
- [x] Implemented discrepancy detection (>20% threshold)
- [x] Updated verification flags and notes
- [x] Preserved both values for display
- [x] Tested with Assessment #50
- [ ] Frontend visualization updates (pending)
- [ ] Admin dashboard enhancements (pending)
- [ ] Re-process historical assessments (pending)

---

## 🚀 Next Steps

### 1. Frontend Updates (Immediate)

- Update assessment results page to show comparison
- Add visual indicators (badges, icons)
- Display verification notes when present
- Add "Confirm Smarty Value" button when user didn't specify

### 2. Admin Dashboard (High Priority)

- Add filter for "Discrepancy > 20%"
- Show comparison in submission detail view
- Add manual override capability
- Track verification call outcomes

### 3. Workflow Enhancements (Medium Priority)

- Add "Request Confirmation" email template
- Create verification call script
- Track which values were confirmed
- Update assessment after verification

### 4. Analytics (Low Priority)

- Track user vs Smarty accuracy over time
- Identify patterns in discrepancies
- Improve Smarty calculation logic
- Generate data quality reports

---

## 📝 Summary

**Key Change**: User-specified available build space is now the **primary, trusted source** for AI assessments, with Smarty data serving as a **comparison point** for verification.

**Impact**: More accurate assessments that respect user knowledge while maintaining automated cross-checks for quality assurance.

**User Experience**: Users see their input is trusted while getting the benefit of automated validation.

**Data Quality**: Both values preserved for audit trail and continuous improvement.

---

## 🔗 Related Documentation

- `UNIT_CALCULATION_FIXED_COMPLETE.md` - Original unit calculation fix
- `AVAILABLE_BUILD_SPACE_VERIFICATION_COMPLETE.md` - Verification workflow
- `AI_ASSESSMENT_BUG_FIXES_COMPLETE.md` - Previous assessment fixes
- `ASSESSMENT_VIZ_SMARTY_DATA_COMPLETE.md` - Frontend visualization

---

**Status**: ✅ Backend changes complete, frontend updates pending
