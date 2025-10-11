# PHASE 2 & 3 DATABASE SCHEMA COMPLETE

## Overview

Successfully added LOGOS-specific deal breaker and partnership enhancement fields to the Assessment model.

---

## Phase 2: Deal Breaker Fields ✅

### Purpose

Track critical LOGOS deal breakers that would disqualify a property regardless of score.

### Fields Added

#### 1. Existing Debt Tracking

- **`existing_debt_amount`** (Float, nullable)
  - Church's current outstanding debt on the property
  - Used to calculate debt-to-value ratio
- **`debt_to_value_ratio`** (Float, nullable)
  - Calculated: `existing_debt_amount / property_assessed_value`
  - **Deal Breaker Threshold:** >20%
  - LOGOS requires minimal debt (<20% of property value)

#### 2. Sanctuary Replacement

- **`expects_sanctuary_replacement`** (Boolean, nullable)
  - Does the church expect LOGOS to replace their sanctuary?
  - **Potential Issue:** Yes = complicates development significantly
- **`sanctuary_replacement_cost_estimate`** (Float, nullable)
  - Estimated cost if sanctuary replacement is needed
  - Used for risk assessment and scoring adjustments

### Scoring Impact (Phase 2)

```python
# Debt-to-Value Ratio
if debt_to_value_ratio > 0.20:
    # CRITICAL DEAL BREAKER
    financial_score -= 20
    deal_breakers.append("Existing debt exceeds 20% of property value")

# Sanctuary Replacement
if expects_sanctuary_replacement == True:
    # POTENTIAL ISSUE
    partnership_score -= 10
    risk_score -= 5
```

---

## Phase 3: Partnership Enhancement Fields ✅

### Purpose

Evaluate church partnership quality based on LOGOS's key requirements for successful collaborations.

### Fields Added

#### 1. Decision-Making Authority

- **`decision_making_authority`** (String(50), nullable)
  - **Options:** "pastor", "board", "congregation", "denomination"
  - **Best:** "pastor" or "board" (clear authority)
  - **Worst:** "congregation" or "denomination" (slow, complex)

#### 2. Decision Timeline

- **`decision_timeline`** (String(50), nullable)
  - **Options:** "immediate", "1-3_months", "3-6_months", "6-12_months", "unsure"
  - **Best:** "immediate" or "1-3_months" (fast)
  - **Acceptable:** "3-6_months"
  - **Poor:** "6-12_months" or "unsure"

#### 3. Ownership Expectations

- **`accepts_60_40_ownership`** (Boolean, nullable)
  - Is church willing to accept 60% LOGOS / 40% Church ownership split?
  - **Required:** Yes (LOGOS standard structure)
  - **Deal Breaker:** No (expectations misalignment)

#### 4. Financial Commitment

- **`willing_to_pay_deposit`** (Boolean, nullable)
  - Is church willing to pay $5,000 refundable deposit?
  - **Indicator:** Yes = serious commitment
  - **Red Flag:** No = may not be serious partner

### Scoring Impact (Phase 3)

```python
# Decision-Making Authority (max +20 points)
if decision_making_authority in ["pastor", "board"]:
    partnership_score += 20
    logger.info("✓ Clear decision-making authority (+20)")
elif decision_making_authority == "congregation":
    partnership_score += 5
    logger.info("⚠ Congregation-based decisions (slower process, +5)")
elif decision_making_authority == "denomination":
    partnership_score -= 10
    logger.info("✗ Denomination approval required (complex process, -10)")

# Decision Timeline (max +10 points)
if decision_timeline in ["immediate", "1-3_months"]:
    partnership_score += 10
    logger.info("✓ Fast decision timeline (+10)")
elif decision_timeline == "3-6_months":
    partnership_score += 5
    logger.info("△ Moderate decision timeline (+5)")
elif decision_timeline in ["6-12_months", "unsure"]:
    partnership_score -= 5
    logger.info("✗ Slow/uncertain timeline (-5)")

# Ownership Expectations (max +20 points)
if accepts_60_40_ownership == True:
    partnership_score += 20
    logger.info("✓ Accepts 60/40 ownership split (+20)")
elif accepts_60_40_ownership == False:
    partnership_score -= 15
    deal_breakers.append("Does not accept LOGOS 60/40 ownership structure")
    logger.info("✗ DEAL BREAKER: Rejects 60/40 split (-15)")

# Financial Commitment (max +10 points)
if willing_to_pay_deposit == True:
    partnership_score += 10
    logger.info("✓ Willing to pay $5K deposit (serious commitment, +10)")
elif willing_to_pay_deposit == False:
    partnership_score -= 5
    logger.info("△ Not willing to pay deposit (commitment concern, -5)")
```

---

## Phase 4: Geographic Enhancement (Visual Only, No Score Impact)

### Purpose

Display whether property is in LOGOS's target geographic markets (LA City or San Diego City - NOT counties).

### Implementation

```python
# Parse city from property.city field
property_city = property.city.strip().lower() if property.city else None

# Check target market match
is_target_market = property_city in ["los angeles", "san diego"]

# Display as visual indicator (NO score impact)
if is_target_market:
    display_badge = "✓ Target Market - LA/SD City"
    badge_color = "green"
else:
    display_badge = "⚠ Outside Target Market"
    badge_color = "yellow"
```

### Why Not Scoring?

- Geographic location is a **binary qualifier**, not a quality metric
- Properties outside LA/SD City shouldn't be assessed at all
- Adding points would artificially inflate scores
- Better approach: Filter submissions at intake or flag as ineligible

---

## Database Migrations

### Migration Files Created

1. **`2025_10_07_1845-add_phase2_deal_breaker_fields.py`**

   - Revision ID: `a1b2c3d4e5f6`
   - Revises: `c273519300a9`
   - Added: `existing_debt_amount`, `debt_to_value_ratio`, `expects_sanctuary_replacement`, `sanctuary_replacement_cost_estimate`

2. **`2025_10_07_1900-add_phase3_partnership_fields.py`**
   - Revision ID: `b2c3d4e5f6g7`
   - Revises: `a1b2c3d4e5f6`
   - Added: `decision_making_authority`, `decision_timeline`, `accepts_60_40_ownership`, `willing_to_pay_deposit`

### Running Migrations

```bash
# Run all pending migrations
docker-compose exec backend alembic upgrade head

# Check current migration status
docker-compose exec backend alembic current

# Rollback one migration
docker-compose exec backend alembic downgrade -1
```

---

## Next Steps

### 1. Update AI Assessment Service

**File:** `/backend/app/services/ai_assessment.py`

**Tasks:**

- [ ] Add Phase 2 deal breaker logic to `_analyze_financials()` method
- [ ] Add Phase 3 partnership scoring to `_analyze_partnership()` method
- [ ] Calculate `debt_to_value_ratio` from `existing_debt_amount` and `property_assessed_value`
- [ ] Add deal breaker flags to assessment results
- [ ] Update logging to show Phase 2/3 scoring impacts

### 2. Update Frontend Submission Form

**File:** `/frontend/src/app/dashboard/new-submission/page.tsx`

**Tasks:**

- [ ] Add Phase 2 fields to form:
  - Existing debt amount input (currency)
  - Sanctuary replacement checkbox
- [ ] Add Phase 3 fields to form:
  - Decision-making authority dropdown
  - Decision timeline dropdown
  - 60/40 ownership acceptance checkbox
  - $5K deposit willingness checkbox
- [ ] Add validation and help text
- [ ] Update form submission handler

### 3. Update Frontend Assessment Display

**File:** `/frontend/src/app/admin/submissions/[id]/assessment/page.tsx`

**Tasks:**

- [ ] Add Phase 4 geographic indicator badge
- [ ] Display Phase 2 deal breakers prominently
- [ ] Show Phase 3 partnership assessment
- [ ] Update scoring breakdown to reflect new factors

### 4. Update PDF Report Generator

**File:** `/backend/app/services/report_generator.py`

**Tasks:**

- [ ] Add Phase 2 deal breaker section
- [ ] Add Phase 3 partnership assessment section
- [ ] Add Phase 4 geographic market indicator
- [ ] Update scoring explanation to include new factors

### 5. Update Schemas

**Files:**

- `/backend/app/schemas/assessment.py`
- `/backend/app/schemas/submission.py`

**Tasks:**

- [ ] Add Phase 2 fields to `AssessmentSubmissionData`
- [ ] Add Phase 3 fields to `AssessmentSubmissionData`
- [ ] Update response schemas to include new fields

---

## Testing Checklist

### Phase 2 Testing

- [ ] Create submission with high debt (>20%) → Should flag as deal breaker
- [ ] Create submission with low debt (<20%) → Should pass
- [ ] Create submission with sanctuary replacement = Yes → Should impact scores
- [ ] Verify debt-to-value ratio calculation is accurate

### Phase 3 Testing

- [ ] Test all decision-making authority options → Verify scoring
- [ ] Test all decision timeline options → Verify scoring
- [ ] Test ownership acceptance = Yes → Should add +20 points
- [ ] Test ownership acceptance = No → Should flag as deal breaker
- [ ] Test deposit willingness impacts

### Phase 4 Testing

- [ ] Property in Los Angeles → Should show "✓ Target Market"
- [ ] Property in San Diego → Should show "✓ Target Market"
- [ ] Property in Pasadena (LA County but not City) → Should show "⚠ Outside Target"
- [ ] Property in other city → Should show "⚠ Outside Target"

---

## LOGOS Requirements Summary

### Non-Negotiables (Deal Breakers)

1. ✅ **40+ units** (already implemented)
2. ✅ **<20% existing debt** (Phase 2)
3. ✅ **60/40 ownership acceptance** (Phase 3)
4. ⚠️ **No sanctuary replacement** (Phase 2 - scored but not automatic disqualification)
5. ⚠️ **LA/SD City only** (Phase 4 - visual indicator only)

### Financial Thresholds

1. ✅ **20% IRR** (already implemented)
2. ✅ **7% Yield on Cost** (already implemented)
3. ⚠️ **7% church return** (not yet implemented)

### Partnership Quality Indicators

1. ✅ **Clear authority** (Phase 3 - pastor/board)
2. ✅ **Fast decision-making** (Phase 3 - <3 months)
3. ✅ **Financial commitment** (Phase 3 - $5K deposit)

---

## Database Schema Reference

```sql
-- Phase 2: Deal Breaker Fields
ALTER TABLE assessments ADD COLUMN existing_debt_amount FLOAT;
ALTER TABLE assessments ADD COLUMN debt_to_value_ratio FLOAT;
ALTER TABLE assessments ADD COLUMN expects_sanctuary_replacement BOOLEAN;
ALTER TABLE assessments ADD COLUMN sanctuary_replacement_cost_estimate FLOAT;

-- Phase 3: Partnership Enhancement Fields
ALTER TABLE assessments ADD COLUMN decision_making_authority VARCHAR(50);
ALTER TABLE assessments ADD COLUMN decision_timeline VARCHAR(50);
ALTER TABLE assessments ADD COLUMN accepts_60_40_ownership BOOLEAN;
ALTER TABLE assessments ADD COLUMN willing_to_pay_deposit BOOLEAN;
```

---

## Status: ✅ DATABASE SCHEMA COMPLETE

All database migrations for Phases 2, 3, and 4 are complete. Ready to proceed with:

1. Backend scoring logic implementation
2. Frontend form updates
3. Assessment display enhancements
4. PDF report updates
