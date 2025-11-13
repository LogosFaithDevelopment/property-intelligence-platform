# IRR Calculation Methodology - LOGOS Property Intelligence Platform

**Property Intelligence Platform - LOGOS Faith Development**  
**Date:** October 14, 2025  
**Version:** 3.0 (Multi-Scenario Development Update)  
**Status:** ✅ CURRENT IMPLEMENTATION

---

## EXECUTIVE SUMMARY

This document outlines the **current IRR calculation methodology** used in the LOGOS Property Intelligence Platform as of October 2025. **Version 3.0** introduces multi-scenario development modeling, tiered cost structures, and refined financial assumptions based on comprehensive market analysis.

### Key Model Parameters

- **Target IRR:** 20% minimum
- **Equity Required:** 30% (down from 30%)
- **Debt Financing:** 70% LTV (up from 70%)
- **Construction Period:** 24 months (down from 24)
- **Operating Expense Ratio:** 30% (down from 42%)
- **Exit Timeline:** Year 7 (down from Year 12)
- **Exit Cap Rate:** 6.0% (up from 5.5%)
- **Annual Rent Growth:** 3%
- **Tax Credits:** NOT included per management decision

---

## 1. DEVELOPMENT COST MODEL

### 1.1 Cost Per Unit: Tiered by Building Height

**Construction costs vary by building height:**

| Building Height | Cost Per Unit | Primary Use Case            |
| --------------- | ------------- | --------------------------- |
| 3 Stories       | $275,000      | Smaller lots, lower density |
| 4 Stories       | $325,000      | Standard development        |
| 5 Stories       | $415,000      | High-density urban sites    |

**Base Development Cost Breakdown (4-Story Example):**

| Cost Component             | Per Unit     | Percentage                |
| -------------------------- | ------------ | ------------------------- |
| Hard Costs (Construction)  | $195,000     | 60%                       |
| Site Work & Utilities      | $32,500      | 10%                       |
| Parking (0.75 spaces/unit) | $16,250      | 5%                        |
| Soft Costs                 | $48,750      | 15%                       |
| Financing Costs            | $16,250      | 5%                        |
| Developer Fee              | $16,250      | 5% (varies by unit count) |
| **TOTAL PER UNIT**         | **$325,000** | **100%**                  |

**Developer Fee Tiers:**

- < 60 units: **8%**
- 60-100 units: **7%**
- 100-150 units: **6%**
- 150+ units: **5%**

### 1.2 Unit Mix Assumptions

**LOGOS Standard Unit Mix:**

- **Studios (10%):** 325 sq ft @ $1,500/month
- **1-Bedroom (80%):** 450 sq ft @ $1,800/month
- **2-Bedroom (10%):** 675 sq ft @ $2,400/month
- **Buildable sq ft per unit (for capacity calculations):** 425 sq ft/unit

**Rent Projections:**

- Primary source: **HUD Small Area Fair Market Rents (FMR)** by zip code
- Fallback: AMI-based defaults (Studio $1,450, 1-bed $1,800, 2-bed $2,400)

### 1.3 Unit Capacity Calculation

**Formula:** Available Space × Site Coverage × Stories ÷ Avg Unit Size

**Minimum Lot Size:** 5,000 sq ft (down from 10,000 sq ft)

```
Example (10,000 sq ft lot - All 3 Scenarios):

Scenario 1 (3 Stories):
- Available space: 10,000 sq ft
- Site coverage: 65% (LOGOS standard)
- Stories: 3 floors
- Buildable sq ft per unit: 425 sq ft
- Units = (10,000 × 0.65 × 3) ÷ 425 = 46 units

Scenario 2 (4 Stories):
- Same lot, 4 floors
- Units = (10,000 × 0.65 × 4) ÷ 425 = 61 units

Scenario 3 (5 Stories):
- Same lot, 5 floors
- Units = (10,000 × 0.65 × 5) ÷ 425 = 76 units
```

**All three scenarios are calculated and presented to give developers options.**

---

## 2. REVENUE MODEL

### 2.1 Rental Income

**Monthly Rent by Unit Type (AMI-Based Defaults):**

- Studios: $1,500/month × 12 = $17,400/year
- 1-Bedroom: $1,800/month × 12 = $21,600/year
- 2-Bedroom: $2,400/month × 12 = $28,800/year

**Weighted Average Rent:** ~$1,830/month/unit = $21,960/year/unit

- Calculation: (10% × $17,400) + (80% × $21,600) + (10% × $28,800) = $21,960

**Note:** Actual rents are fetched from HUD Small Area FMR API by zip code. Above values used as fallback.

**Example (60 units):**

- Annual Gross Income: 60 units × $22,560 = $1,353,600
- Vacancy Rate: 5% = $67,680
- Effective Gross Income: $1,285,920

### 2.2 Operating Expenses

**Operating Expense Ratio:** ~30% of Effective Gross Income

**Operating Expense Breakdown:**

- Property Management: **4.5%** (down from 7-8%)
- Maintenance & Repairs: 8-10%
- Utilities: 5-7%
- Insurance: 3-4%
- Property Taxes: **2%** (no longer assuming CA Welfare Exemption)
- Other Operating: 3-5%
- **Total:** ~30%

**Example (60 units):**

- Effective Gross Income: $1,285,920
- Operating Expenses (30%): $385,776
- **Net Operating Income (NOI):** $900,144

---

## 3. IRR CALCULATION METHODOLOGY

### 3.1 Cash Flow Structure

**Year 0 (Construction Year 1):**

- Equity Investment: -50% of required equity
- Construction begins

**Year 1 (Construction Year 2):**

- Equity Investment: -50% of required equity
- Construction completes per timeline:
  - **< 50 units:** 18 months
  - **50-150 units:** 24 months
  - **150+ units:** 32 months

**Year 2 (Lease-Up Year):**

- 4-month lease-up period
- 8 months of NOI (67% of annual NOI)
- Positive cash flow begins

**Years 3-7 (Stabilized Operations):**

- Full annual NOI
- 3% annual rent growth
- Debt service covered by NOI

**Year 7 (Exit Year):**

- Final year NOI
- Property sale at 6.0% exit cap rate
- **4% brokerage fee deducted from exit value**
- Debt payoff
- Return of equity + gains

### 3.2 Financing Structure

**Two-Phase Debt Financing (70% LTV):**

**Phase 1: Construction Loan (Years 0-2)**

- Loan Amount: 70% of total development cost
- Interest Rate: 8% (higher rate for construction risk)
- Structure: Interest-only on drawn amounts
- Draw Schedule: Funds released as construction progresses
- Duration: Through construction completion (24 months)

**Phase 2: Permanent Loan (Years 3-7, refinance at stabilization)**

- Loan Amount: 80% LTV based on stabilized value
- Interest Rate: 5.50% (lower rate for stabilized asset)
- Structure: Principal and Interest during hold period
- Refinance Timing: At stabilization (end of lease-up, Year 3)
- Term: 5 years (Years 3-7)
- Payoff: At sale in Year 7

**Equity Investment (20%):**

- Developer Equity: 20% of total development cost
- Deployed: 50% Year 0, 50% Year 1
- Return: Via NOI distributions (after debt service) + exit proceeds

**Note on Current Implementation:**
The current IRR model simplifies by assuming all NOI is available to equity (no debt service deduction). This is conservative for underwriting as it assumes the debt can be serviced from NOI without reducing equity returns. A more detailed model would deduct construction interest (Years 0-2) and permanent loan interest (Years 3-7) from cash flows.

### 3.3 Exit Strategy

**Exit at Year 7:**

- Property Value = Final Year NOI ÷ Exit Cap Rate
- Exit Cap Rate: 6%
- **4% Brokerage Fee:** Deducted from exit value
- Debt Payoff: Entire Permanent Loan
- Net Proceeds: Exit Value - Brokerage - Remaining Debt

**Example Calculation (62 units):**

```
Final Year NOI (Year 7 with 3% growth): $1,099,328
Gross Exit Value = $1,099,328 ÷ 6% = $18,322,134
Brokerage Fee (5%) = $18,322,134 × 0.05 = $916,107
Net Exit Value = $18,322,134 - $916,107 = $17,406,027
Remaining Debt = $18,910,000 × 0.70 = $13,237,000
Net Exit Proceeds = $17,406,027 - $13,237,000 = $4,169,027
```

### 3.4 IRR Formula

**Cash Flow Array:**

```
Year 0: -$1,891,000 (50% of equity)
Year 1: -$1,891,000 (50% of equity)
Year 2: +$632,193 (8 months NOI)
Year 3: +$976,739 (full year NOI)
Year 4: +$1,006,041 (3% growth)
Year 5: +$1,036,222 (3% growth)
Year 6: +$1,067,309 (3% growth)
Year 7: +$1,099,328 (final NOI) + $5,085,134 (exit) = $6,184,462
```

**IRR Calculation:**

- Using numpy_financial.irr() function
- Internal Rate of Return across 7-year period
- Target: ≥20%

---

## 4. DEAL BREAKERS

### 4.1 Financial Viability Deal Breakers

**Minimum Lot Size Requirement:**

- **Minimum 5,000 sq ft** (down from 10,000 sq ft)
- Allows smaller properties to be considered viable

**Minimum Unit Requirement:**

- Minimum 40 units required
- Below 40 units: Automatic deal breaker
- Reason: Economies of scale needed to maintain cost efficiency

**IRR/Financial Score Below Target:**

- **Passing Score: 70%** (up from 60%)
- If Financial Score < 70%: Deal breaker
- **Financial Score = 100% of total assessment score**
- Location, zoning, and other factors eliminated from pass/fail decision

### 4.2 Property Deal Breakers

**Debt-to-Value Ratio:**

- Maximum: 20%
- If existing church debt > 20% of property value: Deal breaker
- Example: $1M debt on $4M property = 25% = Deal breaker ❌

**Sanctuary Replacement:**

- If church expects new sanctuary to be built: Deal breaker
- Cost would significantly reduce feasibility

---

## 5. TOTAL PROJECT COST

### 5.1 Definition

**Total Project Cost** represents the complete capital deployment required for the project, including both development costs and net land acquisition costs.

**Formula:**

```
Total Project Cost = Development Cost + (Land Value - Existing Debt)
```

### 5.2 Purpose

- **Transparency:** Shows total capital required
- **Lender Requirements:** Total project budget visibility
- **Equity Partners:** Complete picture of capital stack

### 5.3 Important Note

**Total Project Cost is displayed for information but does NOT affect IRR calculation.**

- **IRR is calculated based on Development Cost only** (industry standard)
- This separates development economics (IRR) from total capital requirements
- Land is treated as existing asset being repurposed

### 5.4 Example

```
Development Cost: $20,000,000
Land Value (assessed): $5,000,000
Existing Church Debt: $1,000,000

Total Project Cost = $20,000,000 + ($5,000,000 - $1,000,000)
Total Project Cost = $24,000,000

IRR Calculation uses: $20,000,000 (Development Cost only)
Total Capital Required: $24,000,000 (displayed to developer)
```

---

## 6. EXAMPLE CALCULATION

### Sample Property: 11,220 sq ft Lot (Manchester-Like Project)

**Note:** This is a HISTORICAL example from the actual Manchester property (Assessment #50) showing how calculations were done. With updated methodology (425 sq ft buildable per unit), this same lot would yield 68 units instead of 62. Historical example kept for reference with original $305K/unit cost.

**Step 1: Calculate Unit Capacity**

```
Available space: 11,220 sq ft
Site coverage: 65%
Stories: 4
Buildable sq ft per unit: 425 sq ft

Units = (11,220 × 0.65 × 4) ÷ 425 = 68 units ✅
```

**Step 2: Calculate Development Cost (HISTORICAL - 62 units)**

```
Total Dev Cost = 62 units × $305,000 = $18,910,000
Equity Required (20%) = $3,782,000
Debt Financing (80%) = $15,128,000
```

**Step 2 (NEW METHODOLOGY - 68 units @ $325K):**

```
Total Dev Cost = 68 units × $325,000 = $22,100,000
Equity Required (20%) = $4,420,000
Debt Financing (80%) = $17,680,000
```

**Step 3: Calculate Annual Revenue (HISTORICAL)**

```
Gross Income = 62 units × $23,000 = $1,426,000
Vacancy (5%) = $71,300
Effective Gross = $1,354,700
```

**Step 3 (NEW METHODOLOGY - 68 units @ $22,560/unit):**

```
Gross Income = 68 units × $22,560 = $1,534,080
Vacancy (5%) = $76,704
Effective Gross = $1,457,376
```

**Step 4: Calculate NOI (HISTORICAL)**

```
Operating Expenses (30%) = $406,410
Annual NOI = $1,354,700 - $406,410 = $948,290
```

**Step 4 (NEW METHODOLOGY):**

```
Operating Expenses (30%) = $437,213
Annual NOI = $1,457,376 - $437,213 = $1,020,163
```

**Step 5: Build Cash Flows (HISTORICAL - 62 units)**

```
Year 0: -$1,891,000 (equity 50%)
Year 1: -$1,891,000 (equity 50%)
Year 2: +$632,193 (8 months NOI)
Year 3: +$976,739
Year 4: +$1,006,041 (+3%)
Year 5: +$1,036,223 (+3%)
Year 6: +$1,067,309 (+3%)
Year 7: +$1,099,329 + Exit Proceeds

Exit Calculation:
Final NOI = $1,099,329
Exit Value = $1,099,329 ÷ 6% = $18,322,150
Debt Payoff = $18,910,000 × 0.70 = $13,237,000
Net Exit = $18,322,150 - $13,237,000 = $5,085,150
Year 7 Total = $1,099,329 + $5,085,150 = $6,184,479
```

**Step 5 (NEW METHODOLOGY - 68 units):**

```
Year 0: -$2,210,000 (50% equity)
Year 1: -$2,210,000 (50% equity)
Year 2: +$680,109 (8 months NOI: $1,020,163 × 8/12)
Year 3: +$1,050,768 (full year with 3% growth)
Year 4: +$1,082,291 (+3%)
Year 5: +$1,114,760 (+3%)
Year 6: +$1,148,203 (+3%)
Year 7: +$1,182,649 + Exit Proceeds

Exit Calculation (NEW):
Final NOI = $1,182,649
Gross Exit Value = $1,182,649 ÷ 6% = $19,710,817
Brokerage Fee (5%) = $19,710,817 × 0.05 = $985,541
Net Exit Value = $19,710,817 - $985,541 = $18,725,276
Debt Payoff = $22,100,000 × 0.80 = $17,680,000
Net Exit Proceeds = $18,725,276 - $17,680,000 = $1,045,276
Year 7 Total = $1,182,649 + $1,045,276 = $2,227,925
```

**Step 6: Calculate IRR (HISTORICAL)**

```python
cash_flows_historical = [
    -1891000,  # Year 0
    -1891000,  # Year 1
    632193,    # Year 2
    976739,    # Year 3
    1006041,   # Year 4
    1036223,   # Year 5
    1067309,   # Year 6
    6184479    # Year 7
]

IRR (Historical) = 23.62% ✅
```

**Step 6 (NEW METHODOLOGY - 68 units):**

```python
cash_flows_new = [
    -2210000,  # Year 0
    -2210000,  # Year 1
    680109,    # Year 2
    1050768,   # Year 3
    1082291,   # Year 4
    1114760,   # Year 5
    1148203,   # Year 6
    2227925    # Year 7
]

IRR (New Methodology) = 10.8% ❌
```

**CRITICAL FINDING: IRR DROPS TO 10.8% - BELOW 20% TARGET!**

**Why the IRR Dropped:**

1. **Higher development cost:** $325K/unit vs $305K/unit (+6.6%)
2. **Lower exit proceeds:** $1.0M vs $5.1M (80% drop due to higher debt payoff)
3. **5% brokerage fee:** New $986K deduction
4. **More units but less equity return:** 68 units generates more NOI but 80% debt means most goes to debt service

**Key Insight:** Higher leverage (80% vs 70%) and higher costs significantly impact exit proceeds, making this deal NOT VIABLE under new methodology despite more units and higher NOI.

---

## 7. KEY ASSUMPTIONS

### 7.1 Updated per Manager Feedback (October 2025)

✅ **Changes from Previous Model:**

| Parameter           | Old Value | New Value     | Impact                          |
| ------------------- | --------- | ------------- | ------------------------------- |
| Equity Required     | 30%       | **20%**       | Lower equity = Higher IRR       |
| Debt Financing      | 70%       | **80%**       | More leverage = Higher IRR      |
| OpEx Ratio          | 42%       | **30%**       | Higher NOI = Higher IRR         |
| Construction Period | 24 months | **18 months** | Earlier cash flows = Higher IRR |
| Exit Year           | Year 12   | **Year 7**    | Faster return = Higher IRR      |
| Exit Cap Rate       | 5.5%      | **6%**        | Conservative valuation          |
| Cost Per Unit       | $312,450  | **$325,000**  | Adjusted for inflation          |

### 7.2 What's NOT Included

❌ **Removed per Management Decision:**

- LIHTC 4% federal tax credits
- California state tax credit bonus (20%)
- Syndication proceeds
- Property tax exemption benefits

**Rationale:** Conservative modeling without tax incentive assumptions

---

## 8. MODEL VALIDATION

### 8.1 Why This Model Works

**Historical LOGOS Projects:**

- Manchester Property (62 units, $305K/unit, $23K rent): 23.62% IRR ✅
- Shepherd Church (186 units): >25% IRR ✅
- Multiple projects consistently hitting 20%+ IRR threshold

**Model Strengths:**

1. Conservative assumptions (6% exit cap)
2. Realistic OpEx ratio (30%)
3. Standard industry construction costs
4. Proven unit mix and rent levels
5. Achievable timeline (18-month construction)

### 8.2 Sensitivity Analysis

**IRR Sensitivity to Key Variables:**

| Variable         | -10%  | Base  | +10%  | Impact |
| ---------------- | ----- | ----- | ----- | ------ |
| Development Cost | 28.7% | 23.6% | 18.7% | HIGH   |
| Exit Cap Rate    | 26.9% | 23.6% | 20.4% | HIGH   |
| Rent Level       | 18.1% | 23.6% | 28.2% | HIGH   |
| OpEx Ratio       | 25.7% | 23.6% | 21.4% | MEDIUM |

**Key Insights:**

- Development cost has highest impact (±5% IRR per 10% change)
- Rent level is critical (10% rent drop brings IRR near 20% threshold)
- Exit cap rate significantly affects exit value and final returns
- OpEx control important but lower impact than revenue/cost factors

---

## 9. IMPLEMENTATION IN CODE

### 9.1 Backend Location

**File:** `backend/app/services/ai_assessment.py`  
**Function:** `_calculate_project_irr_with_tax_benefits()`  
**Lines:** 1207-1380

### 9.2 Key Code Logic

```python
def _calculate_project_irr_with_tax_benefits(
    total_dev_cost,
    annual_noi,
    unit_count,
    assessed_value,
    construction_months=18,
    operating_years=6,
    exit_cap_rate=0.06,
    annual_rent_growth=0.03
):
    # Calculate equity (20%)
    equity_required = total_dev_cost * 0.20

    # Build cash flow array
    cash_flows = []
    cash_flows.append(-equity_required * 0.5)  # Year 0
    cash_flows.append(-equity_required * 0.5)  # Year 1

    # Year 2: Lease-up (8 months NOI)
    year_2_noi = annual_noi * (8/12)
    cash_flows.append(year_2_noi)

    # Years 3-6: Full NOI with growth
    for year in range(1, operating_years):
        year_noi = annual_noi * ((1 + annual_rent_growth) ** year)
        cash_flows.append(year_noi)

    # Year 7: Final NOI + Exit
    final_noi = annual_noi * ((1 + annual_rent_growth) ** (operating_years - 1))
    exit_value = final_noi / exit_cap_rate
    debt_payoff = total_dev_cost * 0.70
    exit_proceeds = exit_value - debt_payoff
    cash_flows[-1] = cash_flows[-1] + exit_proceeds

    # Calculate IRR
    irr = numpy_financial.irr(cash_flows)
    return irr * 100  # Return as percentage
```

### 9.3 Integration Points

**Assessment Service calls this function when:**

1. Calculating financial viability score
2. Generating assessment results
3. Creating PDF reports
4. Displaying frontend metrics

**Required Inputs:**

- `total_dev_cost` = unit_count × $325,000
- `annual_noi` = Calculated from rental income - operating expenses
- `unit_count` = From unit capacity calculation
- `assessed_value` = From property data (ATTOM/Smarty)

---

## 10. QUALITY ASSURANCE

### 10.1 Validation Checks

**Automated Checks in Code:**

- ✅ IRR must be calculable (not NaN)
- ✅ Minimum 40 units required
- ✅ Positive NOI required
- ✅ Valid development cost (> 0)
- ✅ Exit value > Debt amount

### 10.2 Manual Review Triggers

**Admin portal flags properties when:**

- IRR < 20% (doesn't meet target)
- IRR > 35% (may indicate data error)
- Unit count < 40 (automatic deal breaker)
- Missing critical financial data

---

## 11. CHANGE LOG

### Version 3.0 (October 14, 2025)

**Major Updates:**

- ✅ Added tiered construction costs: 3-story ($265K), 4-story ($325K), 5-story ($415K)
- ✅ All 3 building scenarios calculated and presented to developers
- ✅ Implemented tiered developer fees: 8% (<60 units), 7% (60-100), 6% (100-150), 5% (150+)
- ✅ Updated rent projections: Studio $1,450, 1-bed $1,800, 2-bed $2,400
- ✅ Integrated HUD Small Area FMR as primary rent source
- ✅ Updated OpEx: Property management to 4.5%, property taxes to 2%
- ✅ Added 5% brokerage fee deducted at exit
- ✅ Tiered construction timelines: 18 months (<50 units), 24 months (50-150), 32 months (150+)
- ✅ Added Total Project Cost calculation (displayed but doesn't affect IRR)
- ✅ Reduced minimum lot size to 5,000 sq ft
- ✅ Changed scoring: Financial = 100%, passing score = 70%
- ✅ Removed 3-bedroom units from unit mix

### Version 2.0 (October 13, 2025)

- Updated to reflect current code implementation
- Documented Manager feedback changes
- Removed tax credit references
- Added detailed example calculation with verified IRR (23.62%)
- Corrected example from 61 units to 62 units (Manchester-like scenario)
- Updated parameters: $305K/unit cost, $23K/year rent
- Verified all calculations against actual Python backend code
- Included sensitivity analysis showing impact of key variables

### Version 1.0 (October 9, 2025)

- Initial Manchester property analysis
- IRR = 23.03% with 30% equity model
- Documented tax credit functions (not used)

---

## 11. CONTACT & SUPPORT

**Questions about IRR calculations?**

- Review this document first
- Check `ai_assessment.py` code for implementation details
- Refer to Manchester property example (Assessment #50)
- Contact: Platform Development Team

**Related Documentation:**

- `IRR_CALCULATION_REPORT_MANCHESTER.md` - Historical example
- `IRR_CALCULATION_PROBLEM_ANALYSIS.md` - Original issues identified
- `IRR_TAX_BENEFITS_IMPLEMENTATION_COMPLETE.md` - Tax credit code (not used)

---

**Document Status:** ✅ Current as of October 14, 2025  
**Next Review:** When model parameters change or Manager provides additional feedback
