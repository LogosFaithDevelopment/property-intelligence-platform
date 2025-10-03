# Property Intelligence Platform - Complete User Flow

## Overview

This document explains the complete end-to-end user experience for churches using the Property Intelligence Platform to assess their land for affordable housing development with Logos Faith Development.

---

## User Personas

### 1. **Church Leadership** (Primary Users)

- Pastors, board members, facility managers
- Want to explore affordable housing opportunities
- Need simple, clear assessment results
- May lack real estate expertise

### 2. **Logos Faith Development** (Platform Administrators)

- Review all submitted assessments
- Prioritize properties for development
- Access detailed financial and market data
- Make go/no-go decisions on partnerships

---

## Complete User Journey

### Phase 1: Discovery & Registration

#### Step 1.1: Church Arrives at Website

**What Happens:**

- Church leadership hears about Logos Faith Development through outreach
- Visits the Property Intelligence Platform website
- Sees value proposition: "Turn underutilized church land into affordable housing"

**User Actions:**

- Reviews platform benefits
- Watches explainer video (optional)
- Clicks "Get Started" or "Submit Your Property"

---

#### Step 1.2: Account Registration (Clerk Authentication)

**What Happens:**

- User is redirected to Clerk sign-up form
- Can sign up with:
  - Email + password
  - Google account
  - Microsoft account (for churches using O365)

**Technical Flow:**

```
1. User clicks "Sign Up"
2. Clerk hosted UI opens → https://accounts.clerk.dev/sign-up
3. User creates account with email/social login
4. Clerk sends verification email
5. User confirms email → account activated
6. Clerk webhook fires → POST /api/v1/auth/webhooks/clerk
7. Backend receives "user.created" event
8. User redirected to dashboard
```

**Data Captured:**

- Email address (primary identifier)
- Name
- Clerk User ID (stored for session management)

**Code Reference:** `backend/app/routers/auth.py` - `clerk_webhook()`

---

### Phase 2: Church Profile Creation

#### Step 2.1: Complete Church Profile

**What Happens:**

- After authentication, user sees "Complete Your Church Profile" wizard
- Multi-step form to gather church information

**Form Fields Required:**

**Basic Information:**

- Church/Organization Name
- Primary Contact Name & Phone
- Mailing Address
- Website (optional)

**Tax & Legal:**

- Federal Tax ID (EIN)
- 501(c)(3) Status (yes/no)
- State Incorporation Date

**Leadership Information:**

- Senior Pastor/Leader Name
- Board Chair Name
- Facility Manager Contact

**Congregation Details:**

- Weekly Attendance
- Congregation Size
- Year Established

**API Endpoint:** `POST /api/v1/churches`

**Request Body:**

```json
{
  "name": "First Community Church",
  "primary_contact_name": "Rev. Sarah Johnson",
  "primary_email": "pastor@firstcommunity.org",
  "primary_phone": "310-555-0123",
  "street_address": "123 Main St",
  "city": "Los Angeles",
  "state": "CA",
  "zip_code": "90001",
  "tax_exempt_id": "12-3456789",
  "is_501c3_verified": true,
  "congregation_size": 350,
  "weekly_attendance": 280,
  "year_established": 1985
}
```

**Backend Processing:**

```
1. Validates email is unique
2. Validates tax ID format (if provided)
3. Creates Church record in database
4. Sets verification_status = "PENDING"
5. Returns church_id for next step
```

**Data Stored:** `Church` model (`backend/app/models/church.py`)

**Code Reference:** `backend/app/routers/churches.py` - `create_church()`

---

### Phase 3: Property Submission

#### Step 3.1: Add Property Details

**What Happens:**

- User clicks "Add Property" from dashboard
- Completes property information form

**Form Fields Required:**

**Property Address:**

- Street Address
- City, State, ZIP Code
- County (auto-filled during enrichment)

**Property Characteristics:**

- Property Name/Description (optional)
- Current Use (e.g., "Parking lot", "Unused field", "Church building")
- Lot Size (if known)
  - Square feet OR
  - Acres
- Property Type:
  - Vacant Land
  - Church Building
  - Parking Lot
  - Mixed Use
  - Other

**Ownership Information:**

- Ownership Status:
  - Owned outright
  - Mortgaged (remaining balance)
  - Leased
  - Under contract

**Zoning & Legal (if known):**

- Current Zoning Classification (e.g., "R-2", "C-1") - optional
- Any known deed restrictions? (yes/no)
- Any environmental concerns? (yes/no)

**API Endpoint:** `POST /api/v1/properties`

**Request Body:**

```json
{
  "church_id": 123,
  "name": "North Parking Lot",
  "street_address": "456 Church Ave",
  "city": "Los Angeles",
  "state": "CA",
  "zip_code": "90001",
  "current_use": "Parking - Underutilized",
  "lot_size_sqft": 25000,
  "property_type": "PARKING_LOT",
  "ownership_status": "OWNED_OUTRIGHT",
  "zoning_classification": "R-2",
  "has_deed_restrictions": false,
  "has_environmental_concerns": false,
  "notes": "Only used on Sundays, sits empty rest of week"
}
```

**Backend Processing:**

```
1. Validates church_id exists
2. Checks for duplicate address
3. Auto-calculates lot_size_acres from sqft (if provided)
4. Creates Property record with status = "DRAFT"
5. Schedules BACKGROUND TASK: enrich_property_data()
6. Returns property_id immediately
```

**User Sees:**

- Success message: "Property added! We're gathering data..."
- Property card shows "Enrichment in progress" badge
- Can continue adding more properties or proceed to assessment

**Data Stored:** `Property` model (`backend/app/models/property.py`)

**Code Reference:** `backend/app/routers/properties.py` - `create_property()`

---

#### Step 3.2: Automatic Property Enrichment (Background)

**What Happens:**

- System automatically fetches data from multiple APIs
- Happens asynchronously - user doesn't wait
- Takes 30-90 seconds typically

**Data Sources Used:**

**1. Geocoding (OpenStreetMap Nominatim - FREE):**

- Converts address → latitude/longitude
- Extracts county name

**2. US Census API (FREE):**

- Demographics by census tract:
  - Population density
  - Median household income
  - Poverty rate
  - Racial/ethnic composition
  - Housing occupancy rates

**3. HUD APIs (FREE - API key required):**

- **USPS Crosswalk:** ZIP → County FIPS code
- **Income Limits:** Area Median Income (AMI) thresholds
  - 30%, 50%, 60%, 80% AMI for 1-4 person households
  - Updates annually
- **Fair Market Rent (FMR):** Section 8 payment standards
  - Studio, 1BR, 2BR, 3BR, 4BR rents
  - Required for Section 8 viability analysis

**4. FEMA Flood Risk (FREE):**

- Flood zone classification
- Base flood elevation
- Flood insurance requirements

**5. Google Maps (PREMIUM - optional):**

- If API key configured and premium mode enabled:
  - Nearby schools (0.5 mile radius)
  - Transit stops (0.25 mile radius)
  - Grocery stores (1 mile radius)
  - Healthcare facilities (2 mile radius)
  - Parks & recreation

**Technical Flow:**

```
Background Task: enrich_property_data(property_id)
├─ Step 1: Geocode address → lat/long
├─ Step 2: Fetch Census demographics
├─ Step 3: Fetch HUD data (Income Limits + FMR)
├─ Step 4: Check FEMA flood risk
├─ Step 5: Fetch Google Places POIs (if premium)
└─ Step 6: Update Property record with enriched data
```

**Data Stored:**

- Property coordinates (latitude, longitude)
- County name
- Enriched data saved as JSON in `Property.data_sources`

**Example Enriched Data:**

```json
{
  "geocoding": {
    "status": "success",
    "latitude": 34.0522,
    "longitude": -118.2437,
    "source": "nominatim"
  },
  "demographics": {
    "status": "success",
    "data": {
      "median_income": 65420,
      "population_density": 8483,
      "poverty_rate": 14.2,
      "housing_vacancy_rate": 5.8
    }
  },
  "hud_data": {
    "status": "success",
    "data": {
      "county_fips": "06037",
      "county_name": "Los Angeles County, CA",
      "ami_data": {
        "median_income": 83300,
        "income_limits": {
          "80_pct_ami_2person": 66640,
          "60_pct_ami_2person": 49980
        }
      },
      "fmr_data": {
        "studio": 1474,
        "one_br": 1562,
        "two_br": 1852,
        "three_br": 2347,
        "four_br": 2760
      }
    }
  },
  "flood_risk": {
    "status": "success",
    "data": {
      "zone": "X",
      "risk_level": "minimal"
    }
  }
}
```

**User Experience:**

- Property status changes from "DRAFT" → "ENRICHED"
- Dashboard shows completion notification
- User can now proceed to assessment

**Code Reference:** `backend/app/services/property_enrichment.py`

---

### Phase 4: Assessment Questionnaire

#### Step 4.1: Complete Assessment Form

**What Happens:**

- User clicks "Request Assessment" on enriched property
- Completes detailed questionnaire about:
  - Church readiness
  - Development preferences
  - Timeline expectations

**Form Sections:**

**Section A: Church Readiness**

1. **Congregation Approval Status**

   - [ ] Not yet discussed
   - [ ] Informally discussed
   - [ ] Formally presented
   - [ ] Voted and approved
   - [ ] Voted and denied

2. **Leadership Support Level**

   - Scale: 1-5 (Low to High)
   - "How supportive is your leadership team?"

3. **Timeline Readiness**
   - Within 6 months
   - 6-12 months
   - 1-2 years
   - 2+ years
   - Exploring options

**Section B: Development Preferences** 4. **Preferred Unit Count** (text input)

- "How many units would you like to see built?"
- System recommends based on lot size

5. **Affordability Target**

   - 30% AMI (Extremely Low Income)
   - 50% AMI (Very Low Income)
   - 60% AMI (Low Income) - RECOMMENDED
   - 80% AMI (Low Income) - RECOMMENDED
   - Market Rate
   - Mixed Income

6. **Revenue Sharing Preference**

   - Ground lease (church retains ownership)
   - Joint venture partnership
   - Outright sale
   - Unsure - need guidance

7. **Development Involvement Level**
   - Passive (Logos handles everything)
   - Collaborative (regular check-ins)
   - Active (committee involvement)

**Section C: Special Considerations** 8. **Special Requirements** (text area)

- "Any specific needs? (e.g., ground-floor community space, parking requirements, design preferences)"

9. **Constraints or Concerns** (text area)
   - "Are there any known issues or concerns?"

**API Endpoint:** `POST /api/v1/assessments`

**Request Body:**

```json
{
  "church_id": 123,
  "property_id": 456,
  "congregation_approval": "FORMALLY_PRESENTED",
  "leadership_support": 4,
  "timeline_readiness": "6_TO_12_MONTHS",
  "preferred_unit_count": 75,
  "affordability_target": "60_80_AMI",
  "revenue_sharing_preference": "GROUND_LEASE",
  "development_involvement_level": "COLLABORATIVE",
  "special_requirements": "Need ground-floor community space for church outreach programs",
  "priority": "HIGH"
}
```

**Backend Processing:**

```
1. Validates church_id and property_id exist
2. Creates Assessment record with status = "SUBMITTED"
3. Schedules BACKGROUND TASK: process_assessment()
4. Returns assessment_id
5. Sends confirmation email to church
```

**User Sees:**

- Success message: "Assessment submitted!"
- "Our AI is analyzing your property. Results ready in 2-5 minutes."
- Progress indicator on dashboard

**Data Stored:** `Assessment` model (`backend/app/models/assessment.py`)

**Code Reference:** `backend/app/routers/assessments.py` - `create_assessment()`

---

### Phase 5: AI Assessment Processing (Background)

#### Step 5.1: Automated Scoring System

**What Happens:**

- Background task processes assessment using AI + data
- Combines OpenAI analysis with hard data from enrichment
- Takes 2-5 minutes typically

**Scoring Categories (6 total):**

---

#### **1. FINANCIAL VIABILITY (0-100 points) - Weight: 30%**

**Hard Filter Applied First:**

```python
if lot_size_sqft < 10000:
    return score=0.0, reason="DISQUALIFIED: Lot size below 10,000 sq ft minimum"
```

**What's Analyzed:**

**A. Unit Capacity Calculation**

- Target: 40-140 units (Logos sweet spot)
- Formula: `units = (lot_size_acres × 45 units/acre) × 0.85 site_coverage`
- Scoring:
  - ✅ **+15 points**: 40-140 units (ideal)
  - ⚠️ **-5 points**: 30-40 units (marginal)
  - ⚠️ **-10 points**: <30 or >140 units (outside range)

**B. Cost Per Unit Estimation**

- Target: <$325,000 per unit
- Comprehensive cost model includes:
  - Construction ($250-$280/sqft based on size)
  - Site work & parking ($15K-$35K/unit)
  - Utilities ($10K-$20K/unit)
  - Soft costs (15% of hard costs)
  - Financing costs (8% construction, 3% interest)
  - Developer fee (15%)
  - Contingency (10%)
- Economies of scale adjustments (20% reduction for 100+ units)
- Scoring:
  - ✅ **+10 points**: ≤$300K/unit (excellent)
  - ✅ **+5 points**: $300K-$325K/unit (good)
  - ⚠️ **0 points**: $325K-$350K/unit (marginal)
  - ❌ **-10 points**: >$350K/unit (too expensive)

**C. Project Totals**

- Calculated automatically:
  - `total_development_cost = cost_per_unit × unit_capacity`
  - `annual_revenue = units × (2BR_FMR × 12 months)`
  - `yield_on_cost = annual_revenue / total_cost`

**Example Output:**

```json
{
  "financial_score": 85.0,
  "logos_metrics": {
    "lot_size_sqft": 25000,
    "lot_size_acres": 0.57,
    "meets_minimum_lot_size": true,
    "unit_capacity": 22,
    "within_target_unit_range": false,
    "estimated_cost_per_unit": 318500,
    "within_cost_per_unit_target": true,
    "total_development_cost": 7007000,
    "estimated_annual_revenue": 489456,
    "cost_breakdown": {
      "construction_cost_per_unit": 247500,
      "site_work_per_unit": 18000,
      "parking_per_unit": 8500,
      "utilities_per_unit": 12000,
      "soft_costs": 42825,
      "financing_costs": 22968,
      "developer_fee": 42825,
      "contingency": 28550
    }
  }
}
```

---

#### **2. SECTION 8 VIABILITY (0-100 points) - Weight: 20%**

**What's Analyzed:**

**A. Fair Market Rent (FMR) Analysis**

- Uses real HUD FMR data from enrichment
- Focus on 2BR units (most common for affordable housing)
- Scoring:
  - ✅ **+10 points**: 2BR FMR ≥$2,000/month (strong)
  - ✅ **+5 points**: 2BR FMR $1,500-$2,000/month (viable)
  - ⚠️ **0 points**: 2BR FMR $1,200-$1,500/month (marginal)
  - ❌ **-10 points**: 2BR FMR <$1,200/month (not viable)

**B. AMI Tenant Pool Alignment**

- Target: 60-80% AMI households
- Uses HUD Income Limits data
- Checks if 80% AMI for 2-person household falls in $50K-$80K range
- Scoring:
  - ✅ **+5 points**: Perfect alignment
  - ⚠️ **-5 points**: Outside target range

**Example Output:**

```json
{
  "section8_viability_score": 75.0,
  "market_analysis": {
    "section8_viability": {
      "two_br_fmr": 1852,
      "fmr_rating": "VIABLE",
      "annual_section8_revenue": 22224,
      "supports_project_economics": true
    },
    "ami_alignment": {
      "target_ami_level": "60-80%",
      "two_person_80pct_ami": 66640,
      "in_target_range": true,
      "tenant_pool_size": "large"
    }
  }
}
```

---

#### **3. LOCATION QUALITY (0-100 points) - Weight: 15%**

**What's Analyzed:**

**AI-Powered Analysis using OpenAI GPT-4:**

- Access to public transportation
- Proximity to schools and essential services
- Neighborhood quality and safety perception
- Job access and economic opportunity
- Walkability and livability

**Data Sources Used:**

- Census demographics (income, population density)
- Google Places POIs (if available)
- Coordinates and address

**Example AI Prompt:**

```
Analyze this property location for affordable housing development:

Property: North Parking Lot
Address: 456 Church Ave, Los Angeles, CA 90001
Lot Size: 0.57 acres
Zoning: R-2

Demographics:
- Median Income: $65,420
- Population Density: 8,483/sq mi
- Poverty Rate: 14.2%

Nearby Amenities:
- 2 schools within 0.5 miles
- Metro stop 0.3 miles away
- 3 grocery stores within 1 mile

Assess on 0-100 scale considering transit, services, safety, jobs, walkability.
Provide score and 2-3 sentence analysis.
```

**Example Output:**

```json
{
  "location_score": 82.0,
  "location_analysis": "Strong location with excellent transit access and nearby schools. Dense urban area supports walkability and job access. Moderate-income neighborhood aligns well with affordable housing mission."
}
```

---

#### **4. MARKET DEMAND (0-100 points) - Weight: 15%**

**What's Analyzed:**

**AI-Powered Analysis:**

- Local affordable housing need (based on demographics)
- Rental market conditions
- Competition from other affordable housing
- Population growth trends
- Employment opportunities nearby

**Data Sources Used:**

- Census poverty rate, housing vacancy rate
- HUD AMI data (indicates income distribution)
- Enriched demographic data

**Example Output:**

```json
{
  "market_score": 78.0,
  "market_analysis": {
    "narrative": "High demand area with 14.2% poverty rate and low vacancy (5.8%). Section 8 vouchers likely underserved. Strong renter population with limited affordable inventory.",
    "demand_indicators": {
      "poverty_rate": 14.2,
      "housing_vacancy": 5.8,
      "assessment": "HIGH_DEMAND"
    }
  }
}
```

---

#### **5. PARTNERSHIP FIT (0-100 points) - Weight: 10%**

**What's Analyzed:**

**Church Readiness Factors:**

- Congregation approval status (from questionnaire)
- Leadership support level (1-5 scale)
- Timeline readiness (urgency)
- Development involvement preference
- Revenue sharing openness

**Scoring Logic:**

```python
score = 0
if congregation_approval == "VOTED_APPROVED": score += 30
elif congregation_approval == "FORMALLY_PRESENTED": score += 20

if leadership_support >= 4: score += 20
elif leadership_support >= 3: score += 10

if timeline_readiness in ["6_MONTHS", "6_TO_12_MONTHS"]: score += 15

if development_involvement in ["COLLABORATIVE", "PASSIVE"]: score += 10

# Cap at 100
return min(score, 100)
```

**Example Output:**

```json
{
  "partnership_score": 75.0,
  "partnership_analysis": "Church shows strong readiness with formal congregation presentation and high leadership support (4/5). 6-12 month timeline indicates serious intent. Collaborative approach aligns with Logos model."
}
```

---

#### **6. RISK ASSESSMENT (0-100 points) - Weight: 10%**

**What's Analyzed:**

**Risk Factors Evaluated:**

- Flood risk (from FEMA data)
- Zoning complexity
- Environmental concerns (self-reported)
- Deed restrictions (self-reported)
- Title/ownership issues
- Market volatility (based on demographics)

**Scoring Logic:**

```python
score = 100  # Start perfect, deduct for risks

if flood_zone in ["A", "AE", "V", "VE"]: score -= 20  # High risk
elif flood_zone in ["X", "C"]: score -= 0  # Minimal risk

if has_environmental_concerns: score -= 15
if has_deed_restrictions: score -= 10
if ownership_status == "LEASED": score -= 20
if ownership_status == "MORTGAGED": score -= 10

return max(score, 0)
```

**Example Output:**

```json
{
  "risk_score": 85.0,
  "risk_factors": {
    "flood_risk": "MINIMAL (Zone X)",
    "environmental": "NONE REPORTED",
    "deed_restrictions": "NONE",
    "ownership": "OWNED_OUTRIGHT",
    "overall_risk": "LOW"
  }
}
```

---

#### Step 5.2: Calculate Overall Score

**Weighted Composite Formula:**

```python
overall_score = (
    financial_score * 0.30 +
    section8_viability_score * 0.20 +
    location_score * 0.15 +
    market_score * 0.15 +
    partnership_score * 0.10 +
    risk_score * 0.10
)
```

**Letter Grade Assignment:**

```python
if overall_score >= 85: grade = "A"  # Excellent - Priority Development
elif overall_score >= 75: grade = "B"  # Strong - Recommended
elif overall_score >= 65: grade = "C"  # Viable - Conditional Approval
elif overall_score >= 50: grade = "D"  # Marginal - Needs Improvement
else: grade = "F"  # Not Viable
```

**Example Final Score:**

```json
{
  "assessment_id": 789,
  "overall_score": 81.3,
  "grade": "B",
  "category_scores": {
    "financial": 85.0,
    "section8_viability": 75.0,
    "location": 82.0,
    "market": 78.0,
    "partnership": 75.0,
    "risk": 85.0
  },
  "recommendation": "STRONG_CANDIDATE",
  "priority_level": "HIGH"
}
```

**Backend Processing:**

```
1. Status: SUBMITTED → PROCESSING
2. Run all 6 scoring algorithms
3. Calculate weighted overall score
4. Assign letter grade
5. Generate AI recommendations
6. Status: PROCESSING → COMPLETED
7. Send email notification to church
8. Flag for Logos review if score ≥75
```

**Processing Time:** 2-5 minutes

**Code Reference:** `backend/app/services/ai_assessment.py`

---

### Phase 6: Results Delivery

#### Step 6.1: Church Views Assessment Results

**What Happens:**

- Email notification: "Your assessment is ready!"
- User logs into dashboard
- Sees assessment results card

**Results Dashboard View:**

**Header Section:**

```
┌─────────────────────────────────────────────────────────┐
│  North Parking Lot Assessment                           │
│  456 Church Ave, Los Angeles, CA 90001                  │
│                                                          │
│  Overall Score: 81 / 100         Grade: B               │
│  █████████████████░░░░░░░░░░░░░░░░░░░░                 │
│                                                          │
│  Status: ✅ Strong Candidate for Development            │
│  Recommended Unit Count: 22 units                       │
│  Estimated Project Cost: $7.0M                          │
└─────────────────────────────────────────────────────────┘
```

**Category Breakdown:**

```
Financial Viability       85/100 ████████████████████░
Section 8 Viability       75/100 ███████████████░░░░░
Location Quality          82/100 ████████████████░░░░
Market Demand             78/100 ███████████████░░░░░
Partnership Fit           75/100 ███████████████░░░░░
Risk Assessment           85/100 █████████████████░░░
```

**Key Insights Section:**

```
✅ STRENGTHS:
- Lot size meets minimum requirements (25,000 sq ft)
- Estimated cost per unit within target ($318K)
- Strong Section 8 viability (2BR FMR: $1,852)
- Minimal flood risk (Zone X)
- Excellent location with transit access

⚠️ CONSIDERATIONS:
- Unit capacity (22 units) below target range (40-140)
  → Consider adjacent parcel acquisition
- 6-12 month timeline - begin entitlement process soon
```

**Financial Projections:**

```
DEVELOPMENT ESTIMATE:
- Estimated Units: 22
- Cost Per Unit: $318,500
- Total Development Cost: $7,007,000
- Estimated Annual Revenue: $489,456
- Projected Yield on Cost: 7.0%
```

**Next Steps Section:**

```
📋 RECOMMENDED ACTIONS:
1. Schedule consultation with Logos team
2. Begin preliminary site survey
3. Research adjacent parcel availability
4. Prepare congregation presentation materials

📞 CONTACT LOGOS:
[Schedule Meeting Button]
```

**API Endpoint:** `GET /api/v1/assessments/{assessment_id}`

**Response Body:**

```json
{
  "id": 789,
  "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "church_id": 123,
  "property_id": 456,
  "status": "COMPLETED",
  "overall_score": 81.3,
  "grade": "B",
  "category_scores": {
    "financial_score": 85.0,
    "section8_viability_score": 75.0,
    "location_score": 82.0,
    "market_score": 78.0,
    "partnership_score": 75.0,
    "risk_score": 85.0
  },
  "logos_metrics": {
    "lot_size_sqft": 25000,
    "meets_minimum_lot_size": true,
    "unit_capacity": 22,
    "within_target_unit_range": false,
    "estimated_cost_per_unit": 318500,
    "within_cost_per_unit_target": true,
    "total_development_cost": 7007000,
    "estimated_annual_revenue": 489456
  },
  "logos_compliance_summary": {
    "lot_size_compliant": true,
    "unit_capacity_compliant": false,
    "cost_per_unit_compliant": true,
    "overall_compliant": false
  },
  "market_analysis": {
    "section8_viability": {
      "two_br_fmr": 1852,
      "fmr_rating": "VIABLE",
      "supports_project_economics": true
    },
    "ami_alignment": {
      "two_person_80pct_ami": 66640,
      "in_target_range": true
    }
  },
  "risk_factors": {
    "flood_risk": "MINIMAL",
    "overall_risk": "LOW"
  },
  "recommendation": "STRONG_CANDIDATE",
  "next_steps": [
    "Schedule consultation with Logos team",
    "Begin preliminary site survey",
    "Research adjacent parcel availability"
  ],
  "created_at": "2025-10-03T14:30:00Z",
  "completed_at": "2025-10-03T14:33:45Z"
}
```

**Code Reference:** `backend/app/routers/assessments.py` - `get_assessment()`

---

#### Step 6.2: Church Takes Action

**User Options:**

**1. Schedule Consultation**

- Button: "Schedule Meeting with Logos"
- Opens Calendly/scheduling tool
- 30-minute discovery call with Logos team

**2. Download PDF Report**

- Button: "Download Full Report"
- API: `GET /api/v1/assessments/{id}/report`
- Generates comprehensive PDF with all details
- Includes charts, maps, financial projections
- Branded for presentation to board/congregation

**3. Request Site Visit**

- Button: "Request Site Visit"
- Form submission to Logos team
- Triggers email to Logos development team

**4. Update Assessment**

- Button: "Edit Responses"
- Returns to questionnaire
- Re-runs AI assessment with updated data

---

### Phase 7: Logos Leadership Review

#### Step 7.1: Logos Dashboard View

**What Logos Sees:**

**Properties Needing Review:**

```
┌──────────────────────────────────────────────────────────────┐
│  NEW ASSESSMENTS (15)                                        │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  [A] First Community Church - Los Angeles                   │
│      North Parking Lot • 25,000 sqft • Score: 88/100       │
│      💰 $7.0M project • 22 units • $318K/unit               │
│      ✅ Meets lot size  ⚠️ Below unit target                │
│      [View Details] [Approve] [Request More Info]           │
│                                                              │
│  [B] Grace Methodist - Pasadena                             │
│      Unused Field • 43,560 sqft • Score: 81/100            │
│      💰 $15.2M project • 45 units • $338K/unit              │
│      ✅ All criteria met                                     │
│      [View Details] [Approve] [Request More Info]           │
│                                                              │
│  [C] St. John's Episcopal - Santa Monica                    │
│      Back Lot • 18,000 sqft • Score: 72/100                │
│      💰 $5.4M project • 17 units • $318K/unit               │
│      ✅ Cost target met  ⚠️ Below unit & lot minimums       │
│      [View Details] [Flag for Review] [Decline]             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Filtering & Sorting:**

- Filter by score range (A, B, C, D, F)
- Filter by compliance (all criteria met vs. partial)
- Filter by location (county, city)
- Sort by score, project size, submission date
- Search by church name or address

**API Endpoint:** `GET /api/v1/assessments?status=COMPLETED&sort=-overall_score`

---

#### Step 7.2: Detailed Review

**What Logos Sees (Expanded View):**

**Full Assessment Details:**

- All scoring category breakdowns
- Complete financial analysis with cost breakdown
- HUD data (AMI thresholds, FMR rates)
- Census demographics
- Church questionnaire responses
- Property enrichment data
- Risk factors
- AI-generated recommendations

**Additional Logos-Only Data:**

- Church verification status
- Historical submission count
- Previous assessments (if any)
- Internal notes/flags

**Administrative Actions:**

```
[✓ Approve for Development]
[→ Request Additional Information]
[✉ Schedule Site Visit]
[📝 Add Internal Notes]
[❌ Decline with Feedback]
[⏸ Put on Hold]
```

**API Endpoint:** `GET /api/v1/assessments/{id}?include=church,property,enrichment`

---

#### Step 7.3: Logos Makes Decision

**Option 1: Approve for Development**

- Logos clicks "Approve"
- Assessment status: COMPLETED → APPROVED
- Automated email to church: "Congratulations! Logos would like to move forward..."
- Kickoff meeting scheduled
- Moves to active pipeline

**Option 2: Request More Information**

- Logos clicks "Request Info"
- Modal form: "What additional information do you need?"
- Assessment status: COMPLETED → PENDING_INFO
- Email to church with specific questions
- Church can respond via platform

**Option 3: Decline**

- Logos clicks "Decline"
- Modal form: "Provide feedback for church"
- Assessment status: COMPLETED → DECLINED
- Respectful email to church with reasons
- Suggestions for improvement (if applicable)

**API Endpoints:**

- `PATCH /api/v1/assessments/{id}/approve`
- `PATCH /api/v1/assessments/{id}/request-info`
- `PATCH /api/v1/assessments/{id}/decline`

---

## Data Flow Summary

### Complete Technical Flow

```
CHURCH USER JOURNEY:
1. Sign Up (Clerk) → Webhook → User Created in DB
2. Create Church Profile → POST /churches
3. Add Property → POST /properties
4. [Background] Enrich Property → External APIs → Update Property
5. Complete Assessment → POST /assessments
6. [Background] AI Scoring → OpenAI + Data → Update Assessment
7. View Results → GET /assessments/{id}
8. Download Report → GET /assessments/{id}/report

LOGOS ADMIN JOURNEY:
1. Login (Clerk - admin role)
2. View All Assessments → GET /assessments
3. Filter/Sort by Criteria
4. Review Details → GET /assessments/{id}
5. Make Decision → PATCH /assessments/{id}/approve|decline
6. Email Notification → Church receives outcome
```

### Database Flow

```
User (Clerk)
  ↓
Church (Profile)
  ↓
Property (Address) → PropertyEnrichment (APIs)
  ↓
Assessment (Questionnaire) → AIAssessment (Scoring)
  ↓
Report (PDF Generation)
```

### API Integrations Used

| API                  | Purpose         | When Called                    | Data Returned               |
| -------------------- | --------------- | ------------------------------ | --------------------------- |
| Clerk                | Authentication  | Sign up, Login                 | User ID, Email              |
| OpenStreetMap        | Geocoding       | Property creation              | Lat/Long, County            |
| US Census            | Demographics    | Property enrichment            | Income, Population, Poverty |
| HUD USPS Crosswalk   | County Mapping  | Property enrichment            | County FIPS code            |
| HUD Income Limits    | AMI Data        | Property enrichment            | 30-80% AMI thresholds       |
| HUD Fair Market Rent | Section 8 Rates | Property enrichment            | FMR by bedroom count        |
| FEMA                 | Flood Risk      | Property enrichment            | Flood zone                  |
| Google Maps\*        | POI Data        | Property enrichment (optional) | Nearby amenities            |
| OpenAI               | AI Analysis     | Assessment scoring             | Location/Market scores      |

\*Google Maps is optional/premium

---

## Key Features Highlighted

### For Churches:

✅ **Simple Process** - 3 main steps (profile, property, questionnaire)
✅ **Automated Analysis** - No real estate expertise needed
✅ **Fast Results** - Assessment ready in 2-5 minutes
✅ **Transparent Scoring** - See exactly why score is what it is
✅ **Actionable Insights** - Clear next steps provided
✅ **Free to Use** - No cost to submit assessments

### For Logos:

✅ **Consistent Evaluation** - All properties scored on same criteria
✅ **Data-Driven Decisions** - Real HUD data, not guesses
✅ **Prioritization** - Automatically ranks properties by score
✅ **Compliance Filtering** - Instantly see which meet all criteria
✅ **Efficient Screening** - Focuses attention on best candidates
✅ **Audit Trail** - All assessments logged with timestamps

---

## Technical Architecture Notes

### Background Jobs

- **Property Enrichment:** 30-90 seconds
- **AI Assessment:** 2-5 minutes
- Both run asynchronously so users don't wait

### API Performance

- **Geocoding:** <1 second
- **Census API:** 1-2 seconds
- **HUD APIs (3 calls):** 2-3 seconds total
- **FEMA API:** 1-2 seconds
- **OpenAI API:** 30-60 seconds per category (6 categories = 3-5 minutes)

### Scalability Considerations

- All external API calls cached for 30 days
- Property enrichment only runs once per property
- Assessment re-runs only if questionnaire changes
- Database indexed on: church_id, property_id, status, overall_score

### Security & Privacy

- Clerk handles all authentication
- Church data isolated by church_id
- Logos admins have elevated permissions
- No church sees another church's data
- All API keys stored in environment variables

---

## Example Real-World Scenario

**Church:** First Community Church, Los Angeles
**Property:** 25,000 sqft parking lot, underutilized

### Day 1 - Monday

- **10:00 AM**: Pastor hears about Logos at conference
- **2:00 PM**: Visits website, signs up with email
- **2:15 PM**: Completes church profile (10 minutes)
- **2:30 PM**: Adds parking lot property details (15 minutes)
- **2:35 PM**: System begins enrichment (automatic)

### Day 1 - Monday (continued)

- **2:36 PM**: Property enriched with APIs (90 seconds)
- **3:00 PM**: Pastor completes assessment questionnaire (20 minutes)
- **3:01 PM**: AI assessment begins (automatic)
- **3:05 PM**: Assessment complete (4 minutes)
- **3:06 PM**: Email notification sent: "Results ready!"

### Day 1 - Monday (continued)

- **4:00 PM**: Pastor reviews results
  - Score: 81/100 (Grade B)
  - Status: Strong Candidate
  - 22 units, $7M project
  - Cost per unit: $318K ✅
  - Below unit target (40-140) ⚠️
- **4:15 PM**: Downloads PDF report for board meeting
- **4:30 PM**: Schedules consultation call with Logos

### Day 2 - Tuesday

- **9:00 AM**: Logos team reviews overnight submissions
- **9:30 AM**: First Community Church appears in dashboard
  - High priority (score 81, meets most criteria)
- **10:00 AM**: Logos developer reviews full assessment
  - Flags: "Consider adjacent parcel acquisition"
  - Notes: "Strong church partner, good location"
- **10:30 AM**: Approves for next phase

### Day 2 - Tuesday (continued)

- **11:00 AM**: Church receives approval email
- **2:00 PM**: Consultation call happens
  - Discuss adjacent parcel possibilities
  - Review timeline expectations
  - Explain partnership structure

### Week 2

- **Site visit scheduled**
- **Preliminary design concepts shared**
- **Congregation presentation materials provided**

### Month 2

- **Congregation votes and approves**
- **Term sheet negotiated**
- **Entitlement process begins**

---

## Conclusion

This platform streamlines the entire property assessment workflow from **weeks to minutes**, enabling Logos Faith Development to:

1. **Efficiently screen** hundreds of church properties
2. **Focus resources** on the most viable candidates
3. **Make data-driven decisions** using real HUD and Census data
4. **Maintain consistency** across all evaluations
5. **Scale partnerships** with churches across California

For churches, it provides:

1. **Transparency** into viability before investing time
2. **Education** on affordable housing economics
3. **Confidence** in moving forward (or not)
4. **Clear roadmap** of next steps
5. **Professional assessment** at no cost

The AI-powered scoring system combines the best of both worlds: **objective data analysis** (lot size, costs, HUD rates) with **nuanced AI assessment** (location quality, market demand) to produce comprehensive, actionable results.
