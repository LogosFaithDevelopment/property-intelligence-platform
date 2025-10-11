# Manchester Report Verification Checklist

**Date:** October 9, 2025  
**Purpose:** Verify all sections of IRR_CALCULATION_REPORT_MANCHESTER.md reflect CIO's updated parameters

---

## ✅ VERIFIED SECTIONS

### Executive Summary

- ✅ IRR: 23.03% (not 55.34%)
- ✅ Units: 62 (not 45)
- ✅ NO LIHTC mentioned
- ✅ 30% equity requirement stated

### Section 1: Project Overview

- ✅ Property details show 62 units
- ✅ Unit calculation uses 481 sqft average (not 640)
- ✅ Unit mix: 20% studios, 55% 1BD, 25% 2BD (no 3BDs)
- ✅ Total: 62 units

### Section 2: Development Costs

- ⚠️ **NEEDS UPDATE:** Still shows "Total (45 units)" in cost table
- Cost per unit: $328,450 (correct)
- Should recalculate for 62 units

### Section 3: Tax Benefits Analysis

- ✅ Completely replaced with "REMOVED" notice
- ✅ States NO LIHTC, NO syndication, NO property tax exemption

### Section 4: Revenue Projections

- ✅ Updated rental income for new unit mix (studios/1BD/2BD)
- ✅ OpEx: 30% (not 42%)
- ✅ NOI: $1,121,450
- ✅ Lease-up: 4 months (not 6)

### Section 5: IRR Calculation

- ✅ Timeline: 18-month construction, Year 7 exit
- ✅ Cash flows: NO LIHTC proceeds in Year 2
- ✅ Exit cap: 6% (not 4.25%)
- ✅ IRR: 23.03%
- ✅ 8-year hold (not 12 years)

### Section 6: Sensitivity Analysis

- ✅ Base case: 6% exit cap, 30% OpEx, 23.03% IRR
- ✅ NO LIHTC syndication row
- ✅ Scenarios without tax credits
- ✅ Updated key insight

### Section 7: Comparison to LOGOS Target

- ✅ IRR: 23.03% vs 20% target
- ✅ Units: 62
- ✅ Equity: $4.1M (no LIHTC offset)
- ✅ Four reasons WITHOUT tax credits

### Section 8: Risk Factors

- ✅ NO LIHTC syndication mentioned
- ✅ Exit cap: 6% (not 4.25%)
- ✅ OpEx: 30%
- ✅ Property size: 62 units
- ✅ OpEx control as risk factor

### Section 9: Methodology Validation

- ✅ Steps: NO LIHTC calculation
- ✅ Cash flow: 8-year hold, Year 7 exit
- ✅ Database query showing 23.03%
- ✅ 7-year timeframe

### Section 10: Recommendations

- ✅ NO LIHTC validation
- ✅ NO property tax exemption verification
- ✅ Focus on OpEx ratio validation
- ✅ Unit feasibility (62 units)

### Section 11: Conclusion

- ✅ IRR: 23.03%
- ✅ NO tax credits
- ✅ 62 units
- ✅ Risk assessment: Moderate
- ✅ Four key drivers WITHOUT tax credits

### Appendix A: Data Sources

- ⚠️ **COULD UPDATE:** Still mentions "IRC Section 42: LIHTC 4% credits"
- ⚠️ **COULD UPDATE:** Still mentions "CA Revenue & Taxation Code §214: Welfare Exemption"
- Note: These can stay as reference sources, just not used in calculations

### Appendix B: Formulas

- ✅ Unit capacity: 481 sqft, 62 units
- ✅ NO LIHTC credits formula
- ✅ NO property tax savings formula
- ✅ Revenue & NOI with 30% OpEx
- ✅ Exit value with 6% cap
- ✅ IRR with 8-year cash flows

---

## ⚠️ ITEMS TO UPDATE

### 1. Section 2: Development Costs Table

**Current:** Shows "Total (45 units)" column header  
**Should be:** "Total (62 units)" with recalculated costs

**Current totals (45 units):**

- Building Construction: $6,750,000
- Total Development Cost: $13,745,250

**Should be (62 units at $328,450/unit):**

- Building Construction: $9,300,000 (62 × $150K)
- Site Work: $1,116,000 (12% of construction)
- Parking: $1,162,500 (62 × 0.75 × $25K)
- Utilities: $930,000 (62 × $15K)
- Soft Costs: $2,749,650 (22% of hard costs)
- Financing: $751,020 (6% of hard costs)
- Developer Fee: $1,502,040 (12% of hard costs)
- Subtotal: $17,511,210
- Flood Mitigation: $1,426,000 (62 × $23K)
- **TOTAL: $18,937,210** (not $13,745,250)

**Impact on calculations:**

- Equity (30%): $5,681,163 (not $4,123,575)
- Debt (70%): $13,256,047 (not $9,621,675)
- This would change the IRR calculation!

**Note:** The current IRR (23.03%) in the database may be using the OLD cost basis. Need to verify if costs should scale with unit count or if there's a fixed development budget.

### 2. Appendix A: Data Sources (Optional)

Could add note: "Tax credit data sources listed for reference only - not used in this calculation per CIO feedback"

---

## 🎯 RECOMMENDATION

**Option 1:** Keep development cost at $13.7M (45-unit basis)

- Reasoning: Fixed land/site costs don't scale linearly with units
- More efficient $/unit due to density (62 units on same footprint)
- IRR stays at 23.03%

**Option 2:** Recalculate costs for 62 units

- Reasoning: More accurate for larger unit count
- Would need to re-run IRR calculation
- IRR would likely change

**Best approach:** Verify with CIO which cost basis to use:

- Are we using fixed site/land costs (doesn't scale)?
- Or should hard costs scale with unit count?

---

## ✅ CURRENT STATUS

**Report is 95% updated** with CIO feedback:

- ✅ NO LIHTC credits
- ✅ NO syndication
- ✅ NO property tax exemption
- ✅ OpEx: 30%
- ✅ Unit mix: studios/1BD/2BD
- ✅ Construction: 18 months
- ✅ Lease-up: 4 months
- ✅ Exit: Year 7
- ✅ Exit cap: 6%
- ✅ IRR: 23.03%

**Only question:** Should development costs be recalculated for 62 units vs 45?

---

**Verification completed by:** AI Assistant  
**Next step:** Clarify with CIO if cost basis should change with unit count
