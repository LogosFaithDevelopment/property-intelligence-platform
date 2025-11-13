# Available Build Space Feature

## Overview
Churches can now specify how much space they're willing to dedicate to affordable housing development. This is different from the total lot size because churches may want to preserve existing facilities, parking, or green space.

## New Fields in Assessment Model

### `available_build_sqft` (Float) - **OPTIONAL**
- **Description**: Square footage available for housing development
- **Source**: Client-provided input (optional on forms)
- **Default Behavior**: If not provided, assume full lot is available
- **Example**: `10000` (10,000 sq ft available for housing)
- **Use Case**: Church has 5-acre lot but only wants to use 10,000 sq ft in southeast corner
- **When to Use**: Church wants to preserve existing facilities, parking, or green space

### `available_build_acres` (Float) - **OPTIONAL**
- **Description**: Acres available for housing (auto-calculated from sqft)
- **Calculation**: `available_build_sqft / 43,560`
- **Example**: `0.23` acres
- **Auto-populated**: Calculated automatically if `available_build_sqft` is provided

### `build_area_notes` (Text) - **OPTIONAL**
- **Description**: Additional context about the available space
- **When to Use**: Provide location details, constraints, or future plans
- **Examples**:
  - "Southeast corner of parking lot"
  - "Behind main sanctuary, flat terrain"
  - "Two parcels: north lot (5,000 sqft) + south lot (8,000 sqft)"
  - "Must maintain 50 parking spaces for Sunday services"
  - "Will be available after parking expansion in 2026"

## Difference from Property Fields

| Field | Model | Source | Purpose |
|-------|-------|--------|---------|
| `lot_size_sqft` | Property | API/County Records | Total property size |
| `available_build_sqft` | Assessment | Client Input | Space available for housing |

## Use Cases

### Example 1: Church Doesn't Know Yet (Field Left Blank)
```python
property.lot_size_sqft = 217,800  # 5 acres total
assessment.available_build_sqft = None  # Not specified
assessment.build_area_notes = None

# AI Assessment assumes full lot available for analysis
# Church can update later once they decide
```

### Example 2: Large Church, Small Development (Partial Lot)
```python
property.lot_size_sqft = 217,800  # 5 acres total
assessment.available_build_sqft = 10,000  # Only 10K sqft for housing
assessment.available_build_acres = 0.23  # Auto-calculated
assessment.build_area_notes = "Southeast parking lot corner, preserving main campus"
```

### Example 3: Multiple Phase Development
```python
# Phase 1 Assessment
assessment_1.available_build_sqft = 15,000
assessment_1.build_area_notes = "Phase 1: North parking lot"

# Phase 2 Assessment (same property)
assessment_2.available_build_sqft = 20,000
assessment_2.build_area_notes = "Phase 2: South field after parking expansion"
```

### Example 4: Full Lot Development (Vacant Land)
```python
property.lot_size_sqft = 50,000
assessment.available_build_sqft = 50,000  # Using entire lot
assessment.build_area_notes = "Vacant land, full lot available"
```

### Example 5: Early Exploration (Optional Fields Not Used)
```python
# Church just exploring options, doesn't know constraints yet
property.lot_size_sqft = 100,000
assessment.available_build_sqft = None  # Will decide later
assessment.preferred_unit_count = None  # Just want initial assessment
assessment.build_area_notes = "Early stage exploration"
```

## API Integration

### Creating Assessment with Build Space
```bash
POST /api/assessments
{
  "church_id": 1,
  "property_id": 1,
  "available_build_sqft": 10000,
  "build_area_notes": "Southeast corner, flat terrain, easy access",
  "preferred_unit_count": 24,
  "affordability_target": "60_ami"
}
```

### Response
```json
{
  "id": 1,
  "available_build_sqft": 10000.0,
  "available_build_acres": 0.23,
  "build_area_notes": "Southeast corner, flat terrain, easy access"
}
```

## AI Assessment Impact

The AI assessment service can now compare:
- **Available space** (`available_build_sqft`) vs **Desired units** (`preferred_unit_count`)
- Calculate realistic unit density
- Flag feasibility issues (e.g., 100 units on 5,000 sqft is impossible)

### Density Calculations
```python
# Typical densities (units per acre)
low_density = 10  # Single-family style
medium_density = 20  # Townhomes
high_density = 40+  # Multi-story apartments

# Check if desired units fit available space
available_acres = available_build_sqft / 43560
units_per_acre = preferred_unit_count / available_acres
```

## Migration Applied

```bash
# Migration: 71dd657881e1
# Date: 2025-10-05

✅ Added `available_build_sqft` column to assessments
✅ Added `available_build_acres` column to assessments  
✅ Added `build_area_notes` column to assessments
```

## Next Steps

1. **Frontend Form**: Add input fields for available build space
2. **Validation**: Add business logic to ensure `available_build_sqft <= lot_size_sqft`
3. **AI Enhancement**: Update AI assessment to use available space in feasibility calculations
4. **PDF Report**: Include available build space in property section
5. **Visual Tool**: Consider map tool where client can draw/outline available build area

## Example Test Script

```python
# test_available_build_space.py
async def test_create_assessment_with_build_space():
    """Test creating assessment with available build space"""
    
    assessment = Assessment(
        church_id=19,
        property_id=16,
        available_build_sqft=12000,  # 12,000 sq ft available
        build_area_notes="Northwest corner of property, near street access",
        preferred_unit_count=30,
        affordability_target="60_ami"
    )
    
    db.add(assessment)
    await db.commit()
    
    # Auto-calculate acres
    assessment.available_build_acres = assessment.available_build_sqft / 43560
    await db.commit()
    
    print(f"Assessment created with {assessment.available_build_acres:.2f} acres available")
```

## Database Schema

```sql
-- assessments table (new columns)
ALTER TABLE assessments 
  ADD COLUMN available_build_sqft FLOAT,
  ADD COLUMN available_build_acres FLOAT,
  ADD COLUMN build_area_notes TEXT;
```

## Benefits

1. **Realistic Planning**: Ensures development plans match available space
2. **Phased Development**: Allows multiple assessments on same property
3. **Flexibility**: Church can preserve existing facilities while developing housing
4. **Clear Communication**: Documented in notes what space is available
5. **AI Accuracy**: Improves feasibility scoring with accurate space data
