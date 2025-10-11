# User-Specified Available Build Space - Quick Reference

**Date**: October 8, 2025  
**Status**: ✅ COMPLETE

---

## 🎯 What Changed

**User-specified available build space now takes priority over Smarty calculated data.**

---

## 📊 Priority Order

### ✅ NEW (User Priority)

1. **User-specified** → TRUSTED (use immediately)
2. **Smarty calculated** → FALLBACK (user confirmation recommended)
3. **Total lot size** → LAST RESORT (user confirmation required)

### ❌ OLD (Smarty Priority)

1. **Smarty calculated** → TRUSTED (use immediately)
2. **User-specified** → REQUIRES VERIFICATION
3. **Total lot size** → REQUIRES VERIFICATION

---

## 🔍 Key Behaviors

### When User Provides Value

```
✅ Use user value immediately
✅ Compare with Smarty data (if available)
⚠️ Flag if difference > 20%
```

### When User Doesn't Provide Value

```
⚠️ Fall back to Smarty data
⚠️ Flag for user confirmation
📞 Recommend verification call
```

### When No Data Available

```
⚠️ Fall back to total lot size
⚠️ Flag for user confirmation
📞 Require verification call
```

---

## 💾 Data Stored

Both values are preserved for comparison:

- `user_specified_available_sqft` - User input
- `smarty_calculated_available_sqft` - Smarty calculation
- `used_value_sqft` - Value used for assessment
- `used_value_source` - Source identifier
- `requires_manual_verification` - Verification flag
- `verification_note` - Contextual notes

---

## 🎨 Frontend Display

### Assessment Results

```
Available Build Space:
✓ User Specified: 10,000 sqft (used for calculations)
ℹ Smarty Calculated: 11,220 sqft (for comparison)

Difference: -1,220 sqft (-10.9%)
```

### Large Discrepancy Alert

```
⚠️ Large discrepancy detected
User: 15,000 sqft vs Smarty: 10,000 sqft (+50%)

Consider verification call to confirm accurate value.
```

---

## 🧪 Test with Assessment #50

**Property**: 709 Manchester Ave, Los Angeles, CA 90044

```
User Specified:  10,000 sqft
Smarty Calculated: 11,220 sqft
Difference: -1,220 sqft (-10.9%)

Used: 10,000 sqft (user_specified)
Units: 41 (vs 45 with Smarty)
Verification: Not needed (within 20% threshold)
```

---

## 📝 Rationale

### Why User Priority?

1. **Local Knowledge** - Users know demolitions, restrictions, easements
2. **Professional Input** - Often based on architect/engineer assessment
3. **Real-World Accuracy** - Reflects site surveys, zoning feedback

### Why Keep Smarty?

1. **Sanity Check** - Catch data entry errors
2. **Quality Assurance** - Validate user input
3. **Audit Trail** - Document decisions
4. **Continuous Improvement** - Learn from discrepancies

---

## 🚀 Next Steps

### Immediate

- [ ] Update frontend visualization
- [ ] Add comparison display
- [ ] Add discrepancy alerts

### High Priority

- [ ] Admin dashboard filters
- [ ] Manual override capability
- [ ] Verification workflow

### Medium Priority

- [ ] Email templates
- [ ] Verification call scripts
- [ ] Analytics tracking

---

## 📁 Files Modified

- `backend/app/services/ai_assessment.py` (lines ~645-685)

---

## 🔗 Full Documentation

See `USER_SPECIFIED_PRIORITY_UPDATE.md` for complete details.

---

**Summary**: User knows their property best. Trust their input, but validate with automated data.
