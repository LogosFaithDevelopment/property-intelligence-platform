# Available Build Space - UI/Form Guidelines

## Form Field Design

### Placement
Add this section to the **Assessment Form** after "Development Preferences" and before "Partnership Terms"

---

## Form Section: Available Build Space (Optional)

```
┌─────────────────────────────────────────────────────────────────┐
│  Available Build Space (Optional)                               │
│  ═══════════════════════════════════════════════════════════    │
│                                                                  │
│  💡 If you know how much space you'd like to dedicate to       │
│     housing, specify it here. Leave blank to explore options.   │
│                                                                  │
│  Available Square Footage (Optional)                            │
│  ┌─────────────────────┐  sq ft                                │
│  │     10,000          │                                        │
│  └─────────────────────┘                                        │
│                                                                  │
│  📊 This equals approximately 0.23 acres                        │
│     (Your total lot is 5.0 acres)                               │
│                                                                  │
│  Location & Notes (Optional)                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Southeast corner of parking lot, flat terrain with       │  │
│  │ easy street access. Must preserve 50 parking spaces.     │  │
│  │                                                            │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  Common Examples:                                               │
│  • "Southeast corner, approximately 10,000 sq ft"              │
│  • "Behind sanctuary building, will clear after renovation"    │
│  • "Not sure yet - exploring options"                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Field Specifications

### Field 1: Available Square Footage
- **Label**: "Available Square Footage (Optional)"
- **Type**: Number input (Float)
- **Placeholder**: "e.g., 10000"
- **Suffix**: "sq ft"
- **Required**: ❌ No (completely optional)
- **Validation**: 
  - If provided, must be > 0
  - Warning if > total lot size: "This exceeds your total lot size"
  - Suggestion: "Typical housing density: 20-40 units per acre"

### Field 2: Auto-Calculated Acres (Display Only)
- **Label**: "Approximately [X] acres"
- **Type**: Display text (not editable)
- **Calculation**: `available_build_sqft / 43,560`
- **Show When**: `available_build_sqft` is entered
- **Format**: "This equals approximately **0.23 acres**"
- **Context**: Also show total lot size for comparison

### Field 3: Location & Notes
- **Label**: "Location & Notes (Optional)"
- **Type**: Textarea (multi-line)
- **Placeholder**: "Describe where the housing will be located on your property..."
- **Max Length**: 500 characters
- **Required**: ❌ No
- **Examples**: Show common examples below field

---

## Form States

### State 1: Empty Form (Initial)
```
Available Square Footage (Optional)
┌─────────────────────┐
│                     │ sq ft
└─────────────────────┘

💡 Leave blank if you're not sure yet
```

### State 2: User Enters Value
```
Available Square Footage (Optional)
┌─────────────────────┐
│     10,000          │ sq ft  ✓
└─────────────────────┘

📊 This equals approximately 0.23 acres
   (Your total lot is 5.0 acres - 4.6% will be used)
```

### State 3: Validation Warning (Too Large)
```
Available Square Footage (Optional)
┌─────────────────────┐
│     300,000         │ sq ft  ⚠️
└─────────────────────┘

⚠️  This exceeds your total lot size (217,800 sq ft)
    Did you mean 30,000?
```

### State 4: With Notes
```
Available Square Footage (Optional)
┌─────────────────────┐
│     10,000          │ sq ft  ✓
└─────────────────────┘

📊 This equals approximately 0.23 acres

Location & Notes (Optional)
┌──────────────────────────────────────────────────────────┐
│ Southeast corner of parking lot. Flat terrain with      │
│ street access. Must maintain 50 parking spaces for      │
│ Sunday services.                                         │
└──────────────────────────────────────────────────────────┘
```

---

## Help Text & Tooltips

### Main Help Text
```
ℹ️ Available Build Space

This is the amount of space you're willing to dedicate to 
affordable housing. It may be less than your total lot size 
if you need to preserve:
• Existing buildings
• Parking areas
• Green space or playgrounds
• Future expansion areas

If you're not sure yet, leave this blank. We'll use your 
total lot size for initial feasibility analysis.
```

### Field Tooltip (on hover/click ⓘ icon)
```
Why provide this?

✓ More accurate feasibility assessment
✓ Better unit count recommendations
✓ Realistic financial projections
✓ Clear documentation for partners

You can always update this later as plans develop.
```

---

## Conditional Logic

### Show/Hide Validation Messages
```javascript
if (available_build_sqft > property.lot_size_sqft) {
  showWarning("Exceeds total lot size");
}

if (available_build_sqft < 5000 && preferred_unit_count > 10) {
  showWarning("Limited space for desired unit count");
}
```

### Auto-Calculate Acres
```javascript
if (available_build_sqft) {
  available_build_acres = available_build_sqft / 43560;
  percentage = (available_build_sqft / property.lot_size_sqft) * 100;
  
  showMessage(`
    This equals approximately ${available_build_acres.toFixed(2)} acres
    (${percentage.toFixed(1)}% of your total lot)
  `);
}
```

---

## Form Submission

### API Payload (With Data)
```json
{
  "church_id": 19,
  "property_id": 16,
  "available_build_sqft": 10000,
  "build_area_notes": "Southeast corner, flat terrain",
  "preferred_unit_count": 24,
  "affordability_target": "60_ami"
}
```

### API Payload (Without Data - Fields Omitted or Null)
```json
{
  "church_id": 19,
  "property_id": 16,
  "available_build_sqft": null,
  "build_area_notes": null,
  "preferred_unit_count": 30,
  "affordability_target": "60_ami"
}
```

---

## Mobile Responsive Design

### Mobile View
```
┌─────────────────────────────────┐
│ Available Build Space (Optional)│
│                                  │
│ 💡 Leave blank if not sure      │
│                                  │
│ Square Footage                   │
│ ┌─────────────────────────────┐ │
│ │         10,000              │ │
│ └─────────────────────────────┘ │
│ sq ft                            │
│                                  │
│ 📊 ≈ 0.23 acres                 │
│ (5.0 acres total)               │
│                                  │
│ Location Notes                   │
│ ┌─────────────────────────────┐ │
│ │ Southeast corner...         │ │
│ │                             │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

---

## Accessibility

### ARIA Labels
```html
<label for="available_build_sqft">
  Available Square Footage (Optional)
</label>
<input 
  type="number" 
  id="available_build_sqft"
  name="available_build_sqft"
  aria-label="Available square footage for housing development"
  aria-describedby="sqft-help"
  aria-required="false"
  min="0"
  step="100"
  placeholder="e.g., 10000"
/>
<span id="sqft-help" class="help-text">
  Leave blank if you're not sure yet
</span>
```

---

## Form Validation Messages

### Success Messages
```
✓ Available space saved (10,000 sq ft)
✓ This allows for approximately 5-12 housing units
```

### Warning Messages
```
⚠️ This exceeds your total lot size
⚠️ Limited space for desired 50 units (consider reducing to 20-30)
⚠️ Very small area - recommend at least 5,000 sq ft for housing
```

### Info Messages
```
💡 Not specified - we'll use your full lot (5.0 acres) for analysis
💡 You can update this later as your plans develop
```

---

## Example User Journeys

### Journey 1: Early Stage Church
1. Church fills out basic info
2. Skips available build space (doesn't know yet)
3. Gets assessment based on full lot potential
4. Later returns and updates with specific area

### Journey 2: Church with Clear Plans
1. Church knows they want to use parking lot corner
2. Enters 12,000 sq ft in form
3. Adds notes: "Southeast corner, near bus route"
4. Assessment is tailored to this specific space

### Journey 3: Multiple Phase Planning
1. Church creates Assessment #1 for Phase 1
   - Available: 10,000 sq ft (north parking)
2. Later creates Assessment #2 for Phase 2
   - Available: 15,000 sq ft (south field)
3. Can compare both scenarios

---

## Integration with AI Assessment

### AI Behavior When Field is Blank
```python
if assessment.available_build_sqft:
    buildable_area = assessment.available_build_sqft
    notes = f"Church has allocated {buildable_area:,} sq ft for development"
else:
    buildable_area = property.lot_size_sqft
    notes = "Using full lot size (client has not specified constraints)"

# Continue with feasibility calculations
```

### AI Feasibility Check
```python
# Check if desired units fit available space
available_acres = buildable_area / 43560
units_per_acre = preferred_unit_count / available_acres

if units_per_acre > 60:
    flag_warning("Density too high - not feasible")
elif units_per_acre > 40:
    flag_info("High density - will require multi-story construction")
```

---

## Future Enhancements

### Phase 2: Visual Map Tool
- Allow users to draw/outline available area on property map
- Auto-calculate square footage from drawn polygon
- Show surrounding context (streets, neighbors)

### Phase 3: Smart Suggestions
- Suggest optimal build area based on:
  - Zoning setback requirements
  - Existing structures
  - Topography
  - Street access

---

## Testing Scenarios

1. ✅ Form submits successfully with field blank
2. ✅ Form submits successfully with value entered
3. ✅ Acres auto-calculate when sqft entered
4. ✅ Warning appears if value exceeds lot size
5. ✅ Assessment processes correctly with/without value
6. ✅ PDF report handles both scenarios
7. ✅ Mobile layout displays correctly
8. ✅ Screen reader announces field properly
