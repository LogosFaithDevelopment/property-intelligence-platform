# Assessment Schema Enhancements

## Logos-Specific API Response Fields

**Date:** October 3, 2025  
**File Modified:** `/backend/app/schemas/assessment.py`

---

## 🎯 Overview

Enhanced the `AssessmentResponse` schema to properly expose all Logos Faith Development-specific scoring metrics through the API. Frontend applications can now consume structured financial feasibility data without parsing complex JSON structures.

---

## ✅ New Schema Classes

### 1. `LogosFinancialMetrics` (New)

A structured schema for Logos-specific financial analysis data.

**Purpose:** Provides easy access to all enhanced financial calculations without requiring JSON parsing.

**Fields:**

#### Lot Size Validation

```python
lot_size_sqft: Optional[float]           # Lot size in square feet
lot_size_acres: Optional[float]          # Lot size in acres
meets_minimum: Optional[bool]            # ✅ Meets 10,000 sq ft minimum?
disqualified: Optional[bool]             # ❌ Property disqualified?
disqualification_reason: Optional[str]   # Why property was disqualified
```

#### Unit Capacity Analysis

```python
feasible_units: Optional[int]            # Calculated feasible unit count
within_target_range: Optional[bool]      # ✅ Within 40-140 unit range?
developable_acres: Optional[float]       # Developable acres (after setbacks)
units_per_acre_assumed: Optional[int]    # Density assumption (units/acre)
```

#### Cost Per Unit Analysis

```python
cost_per_unit: Optional[float]           # Estimated cost per unit
cost_per_unit_formatted: Optional[str]   # e.g., "$285,000"
target_cost_per_unit: Optional[int]      # Target: $325,000
under_target: Optional[bool]             # ✅ Under $325K target?
```

#### Cost Breakdown

```python
building_construction_cost: Optional[float]
site_work_cost: Optional[float]
parking_cost: Optional[float]
utilities_hookup_cost: Optional[float]
soft_costs: Optional[float]
financing_costs: Optional[float]
developer_fee: Optional[float]
```

#### Project Totals

```python
estimated_development_cost: Optional[float]
estimated_development_cost_formatted: Optional[str]  # e.g., "$27,075,000"
```

---

## 🔧 Enhanced AssessmentResponse

### New Computed Properties

#### 1. `logos_metrics` Property

**Type:** `Optional[LogosFinancialMetrics]`

**Description:** Extracts and structures all Logos-specific data from the `financial_projections` JSON field.

**Usage Example:**

```python
assessment = await get_assessment(assessment_id)
metrics = assessment.logos_metrics

if metrics:
    print(f"Feasible Units: {metrics.feasible_units}")
    print(f"Cost Per Unit: {metrics.cost_per_unit_formatted}")
    print(f"Within Target Range: {metrics.within_target_range}")
```

**API Response:**

```json
{
  "id": 1,
  "overall_score": 85.5,
  "logos_metrics": {
    "lot_size_sqft": 108900,
    "lot_size_acres": 2.5,
    "meets_minimum": true,
    "disqualified": false,
    "feasible_units": 95,
    "within_target_range": true,
    "cost_per_unit": 285000,
    "cost_per_unit_formatted": "$285,000",
    "target_cost_per_unit": 325000,
    "under_target": true,
    "building_construction_cost": 150000,
    "site_work_cost": 18000,
    "parking_cost": 18750,
    "estimated_development_cost": 27075000,
    "estimated_development_cost_formatted": "$27,075,000"
  }
}
```

---

#### 2. `logos_compliance_summary` Property

**Type:** `Dict[str, Any]`

**Description:** Provides a quick pass/fail summary for Logos' three core investment criteria:

1. **Minimum Lot Size** (10,000 sq ft)
2. **Unit Capacity** (40-140 units)
3. **Cost Per Unit** (<$325K)

**Usage Example:**

```python
assessment = await get_assessment(assessment_id)
compliance = assessment.logos_compliance_summary

if compliance["meets_criteria"]:
    print("✅ Property meets all Logos criteria!")
else:
    print(f"⚠️  {compliance['summary']}")

# Check individual criteria
for name, details in compliance["criteria"].items():
    print(f"{name}: {details['status']}")
```

**API Response (Compliant Property):**

```json
{
  "id": 1,
  "logos_compliance_summary": {
    "status": "compliant",
    "meets_criteria": true,
    "summary": "Passed 3/3 core requirements",
    "criteria": {
      "minimum_lot_size": {
        "passed": true,
        "requirement": "10,000 sq ft minimum",
        "actual": 108900,
        "status": "✅ Pass"
      },
      "unit_capacity": {
        "passed": true,
        "requirement": "40-140 units",
        "actual": 95,
        "status": "✅ Pass"
      },
      "cost_per_unit": {
        "passed": true,
        "requirement": "< $325,000 per unit",
        "actual": "$285,000",
        "status": "✅ Pass"
      }
    }
  }
}
```

**API Response (Disqualified Property):**

```json
{
  "id": 2,
  "logos_compliance_summary": {
    "status": "disqualified",
    "message": "Below Logos minimum lot size requirement",
    "meets_criteria": false
  }
}
```

**API Response (Partial Compliance):**

```json
{
  "id": 3,
  "logos_compliance_summary": {
    "status": "partial_compliance",
    "meets_criteria": false,
    "summary": "Passed 2/3 core requirements",
    "criteria": {
      "minimum_lot_size": {
        "passed": true,
        "requirement": "10,000 sq ft minimum",
        "actual": 65000,
        "status": "✅ Pass"
      },
      "unit_capacity": {
        "passed": false,
        "requirement": "40-140 units",
        "actual": 28,
        "status": "⚠️  Outside Range"
      },
      "cost_per_unit": {
        "passed": true,
        "requirement": "< $325,000 per unit",
        "actual": "$310,000",
        "status": "✅ Pass"
      }
    }
  }
}
```

---

## 📊 Frontend Integration Examples

### React Example

```tsx
interface LogosMetrics {
  feasible_units?: number;
  cost_per_unit_formatted?: string;
  within_target_range?: boolean;
  under_target?: boolean;
}

interface Assessment {
  id: number;
  overall_score: number;
  logos_metrics?: LogosMetrics;
  logos_compliance_summary: {
    status: string;
    meets_criteria: boolean;
    criteria?: Record<string, any>;
  };
}

function AssessmentCard({ assessment }: { assessment: Assessment }) {
  const { logos_metrics, logos_compliance_summary } = assessment;

  return (
    <div className='assessment-card'>
      <h3>Score: {assessment.overall_score}/100</h3>

      {/* Compliance Status */}
      <div className={`status-badge ${logos_compliance_summary.status}`}>
        {logos_compliance_summary.meets_criteria
          ? '✅ Meets Logos Criteria'
          : '⚠️  Does Not Meet Criteria'}
      </div>

      {/* Key Metrics */}
      {logos_metrics && (
        <div className='metrics'>
          <MetricItem
            label='Feasible Units'
            value={logos_metrics.feasible_units}
            status={logos_metrics.within_target_range ? 'pass' : 'warning'}
          />
          <MetricItem
            label='Cost Per Unit'
            value={logos_metrics.cost_per_unit_formatted}
            status={logos_metrics.under_target ? 'pass' : 'warning'}
          />
        </div>
      )}

      {/* Detailed Criteria */}
      {logos_compliance_summary.criteria && (
        <div className='criteria-details'>
          {Object.entries(logos_compliance_summary.criteria).map(
            ([key, details]) => (
              <div key={key} className='criterion'>
                <span>{details.status}</span>
                <span>{details.requirement}</span>
                <span>Actual: {details.actual}</span>
              </div>
            )
          )}
        </div>
      )}
    </div>
  );
}
```

### Vue Example

```vue
<template>
  <div class="assessment-card">
    <h3>Score: {{ assessment.overall_score }}/100</h3>

    <!-- Compliance Badge -->
    <div :class="['status-badge', complianceClass]">
      {{ complianceText }}
    </div>

    <!-- Logos Metrics -->
    <div v-if="assessment.logos_metrics" class="metrics-grid">
      <div class="metric">
        <label>Feasible Units</label>
        <value :class="{ success: withinRange }">
          {{ assessment.logos_metrics.feasible_units }}
        </value>
      </div>

      <div class="metric">
        <label>Cost Per Unit</label>
        <value :class="{ success: underTarget }">
          {{ assessment.logos_metrics.cost_per_unit_formatted }}
        </value>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{ assessment: Assessment }>();

const complianceClass = computed(() =>
  props.assessment.logos_compliance_summary.meets_criteria
    ? 'success'
    : 'warning'
);

const complianceText = computed(() =>
  props.assessment.logos_compliance_summary.meets_criteria
    ? '✅ Meets Logos Criteria'
    : '⚠️  Does Not Meet Criteria'
);

const withinRange = computed(
  () => props.assessment.logos_metrics?.within_target_range ?? false
);

const underTarget = computed(
  () => props.assessment.logos_metrics?.under_target ?? false
);
</script>
```

---

## 🔄 Migration Notes

### Backwards Compatibility

✅ **Fully backwards compatible** - No breaking changes

- Existing API consumers will continue to work
- New fields are optional computed properties
- Original `financial_projections` JSON field still available

### Database Changes

❌ **No database migrations required**

- All changes are at the schema/serialization layer
- Existing data automatically supports new properties

### API Versioning

- Current API version: `v1`
- No version bump needed (additive changes only)

---

## 🧪 Testing the Enhanced Schema

### Using cURL

```bash
# Get assessment with Logos metrics
curl -X GET http://localhost:8000/api/v1/assessments/1 \
  -H "Content-Type: application/json" | jq .

# Look for these new fields:
# - .logos_metrics
# - .logos_compliance_summary
```

### Using Python

```python
import httpx

response = httpx.get("http://localhost:8000/api/v1/assessments/1")
assessment = response.json()

# Access Logos metrics
metrics = assessment.get("logos_metrics")
if metrics:
    print(f"Feasible Units: {metrics['feasible_units']}")
    print(f"Meets Minimum: {metrics['meets_minimum']}")
    print(f"Cost Per Unit: {metrics['cost_per_unit_formatted']}")

# Check compliance
compliance = assessment["logos_compliance_summary"]
print(f"Status: {compliance['status']}")
print(f"Summary: {compliance['summary']}")
```

---

## 📝 Summary of Changes

### Files Modified

1. `/backend/app/schemas/assessment.py`
   - Added `LogosFinancialMetrics` schema class
   - Enhanced `AssessmentResponse` with 2 new computed properties
   - ~120 lines of new code

### New API Fields

- `logos_metrics` - Structured financial metrics
- `logos_compliance_summary` - Pass/fail compliance summary

### Benefits

1. ✅ **Easier Frontend Integration** - No JSON parsing needed
2. ✅ **Type Safety** - Fully typed with Pydantic
3. ✅ **Self-Documenting** - Clear field names and descriptions
4. ✅ **Real-Time Compliance** - Instant pass/fail status
5. ✅ **Backwards Compatible** - Existing code unaffected

---

**Implementation Time:** 30 minutes  
**Lines Added:** ~120 lines  
**Breaking Changes:** None  
**Database Migrations:** None required  
**Testing Status:** Ready for testing
