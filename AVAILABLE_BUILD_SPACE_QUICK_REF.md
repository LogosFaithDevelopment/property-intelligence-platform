# 📝 Available Build Space - Quick Reference Card

## What Is It?
Churches can specify how much of their property they want to use for housing (optional field on forms).

---

## 3 New Fields (All Optional)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. available_build_sqft  (Float, Optional)                  │
│    → Square footage available for housing                   │
│    → Client enters: 10,000                                  │
│                                                              │
│ 2. available_build_acres (Float, Optional)                  │
│    → Auto-calculated: sqft / 43,560                         │
│    → Result: 0.23 acres                                     │
│                                                              │
│ 3. build_area_notes     (Text, Optional)                    │
│    → Context about the space                                │
│    → Example: "Southeast corner, flat terrain"             │
└─────────────────────────────────────────────────────────────┘
```

---

## When to Use

### ✅ Use This Field When:
- Church wants to preserve existing buildings
- Need to maintain parking areas
- Want to keep green space
- Planning phased development
- Only certain area is suitable for housing

### ⏭️ Skip This Field When:
- Church hasn't decided yet
- Early exploration phase
- Vacant land (using entire lot)
- Not sure of constraints yet

---

## Examples

### Example 1: Partial Lot (Specify Space)
```
Total Lot: 5.0 acres (217,800 sq ft)
Available: 10,000 sq ft
Notes: "Southeast parking lot corner"

→ AI assesses 10,000 sq ft, not full lot
```

### Example 2: Full Lot (Leave Blank)
```
Total Lot: 2.3 acres (100,000 sq ft)  
Available: [blank]
Notes: [blank]

→ AI assumes full 100,000 sq ft available
```

### Example 3: Phased Development
```
Assessment #1: 15,000 sq ft - "Phase 1: North lot"
Assessment #2: 20,000 sq ft - "Phase 2: South field"

→ Two different scenarios on same property
```

---

## Form Behavior

### User Enters Value:
```
┌─────────────────────┐
│     10,000          │ sq ft  ✓
└─────────────────────┘

📊 This equals approximately 0.23 acres
   (Your total lot is 5.0 acres)
```

### User Leaves Blank:
```
┌─────────────────────┐
│                     │ sq ft
└─────────────────────┘

💡 Leave blank if you're not sure yet
   We'll use your full lot for analysis
```

---

## API Examples

### With Build Space:
```json
{
  "available_build_sqft": 10000,
  "build_area_notes": "Southeast corner"
}
```

### Without Build Space (Omit or Null):
```json
{
  "available_build_sqft": null,
  "build_area_notes": null
}
```

Both valid! ✅

---

## Database Status

```bash
✅ Migration Applied: 71dd657881e1
✅ Columns Added: 3 (all nullable)
✅ Ready to Use: Yes
```

---

## Benefits

| Stakeholder | Benefit |
|------------|---------|
| **Church** | Preserve facilities, control development scope |
| **Platform** | Accurate feasibility, realistic unit counts |
| **Partners** | Clear site boundaries, better planning |

---

## Related Documentation

- **Full Guide**: `AVAILABLE_BUILD_SPACE_FEATURE.md`
- **UI Guidelines**: `AVAILABLE_BUILD_SPACE_UI_GUIDE.md`
- **Summary**: `AVAILABLE_BUILD_SPACE_SUMMARY.md`

---

## Remember

✅ **All 3 fields are OPTIONAL**  
✅ **If blank, AI assumes full lot**  
✅ **Can update later as plans evolve**  
✅ **Multiple assessments can use different areas**

---

**Status: ✅ Ready for Frontend Implementation**
