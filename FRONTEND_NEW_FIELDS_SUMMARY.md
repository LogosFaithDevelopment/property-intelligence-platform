# 🆕 New Fields Added to Frontend Submission Form

**Date:** January 2025  
**Status:** Ready for Backend Implementation

---

## 📝 Summary of New Fields

Added 5 new fields to the church property submission form based on business requirements:

1. **Entity Type** (required dropdown)
2. **EIN Number** (optional, validated)
3. **Website** (optional URL)
4. **Available Build Space** (optional square footage - manual override)
5. **Build Area Notes** (optional text - explains constraints)

---

## 🔧 Backend Implementation Needed

### **1. Church Model Updates ✅ ALREADY EXISTS!**

**File:** `/backend/app/models/church.py`

Good news! The Church model **already has these fields** with slightly different names:

```python
# ✅ ALREADY EXISTS (Line 37-38)
tax_exempt_id = Column(String(50), nullable=True, unique=True)
  # Can be used for EIN number (XX-XXXXXXX format)
  # Frontend label: "EIN Number"

tax_exempt_status = Column(String(50), nullable=True)
  # Can be used for entity_type dropdown
  # Frontend label: "Entity Type"
  # Options: "501(c)(3) Nonprofit", "Religious Corporation", etc.

# ✅ ALREADY EXISTS (Line 46)
website_url = Column(String(255), nullable=True)
  # Frontend label: "Website"
```

**No database migration needed!** Just update frontend to use existing fields.

### **2. Assessment Model Updates**

**File:** `/backend/app/models/assessment.py`

These fields already exist (added in LA County feature):

```python
# ✅ Already exists - Available Build Space
available_build_sqft = Column(Float, nullable=True)
available_build_acres = Column(Float, nullable=True)
build_area_notes = Column(Text, nullable=True)
```

**No changes needed to Assessment model** - the fields are already there! 🎉

### **3. Schema Updates ✅ ALREADY EXISTS!**

**File:** `/backend/app/schemas/church.py`

Good news! The schemas **already support these fields**:

```python
# ✅ ALREADY EXISTS in ChurchBase (lines 17-31)
class ChurchBase(BaseSchema):
    # ...existing fields...

    primary_email: EmailStr = Field(..., description="Primary contact email")
    website_url: Optional[HttpUrl] = Field(None, description="Church website URL")
    # ✅ website_url already exists!

# ✅ ALREADY EXISTS in ChurchCreate (lines 49-50)
class ChurchCreate(ChurchBase):
    tax_exempt_id: Optional[str] = Field(None, max_length=50, description="Tax-exempt ID (EIN)")
    # ✅ Can be used for EIN number

    tax_exempt_status: Optional[str] = Field(None, max_length=50, description="Tax-exempt status type")
    # ✅ Can be used for entity_type dropdown
```

**No schema changes needed!** Just map frontend field names to existing backend fields.

**File:** `/backend/app/schemas/assessment.py`

✅ These fields already exist in `AssessmentBase`:

```python
# Already implemented:
available_build_sqft: Optional[float] = Field(None, description="Available build space in sqft")
available_build_acres: Optional[float] = Field(None, description="Available build space in acres")
build_area_notes: Optional[str] = Field(None, description="Notes about buildable area")
```

---

## 🎯 Frontend Form Structure

### **Section 1: Church Information**

```typescript
// NEW FIELDS ADDED:
entity_type: string (required - dropdown)
  Options:
  - "501(c)(3) Nonprofit"
  - "Religious Corporation"
  - "Church/Religious Organization"
  - "Unincorporated Association"
  - "Other"

ein_number: string (optional)
  Format: XX-XXXXXXX (masked input)
  Validation: Must match pattern \d{2}-\d{7}
  Tooltip: "Employer Identification Number for tax purposes"

website: string (optional)
  Format: URL validation
  Placeholder: "https://yourchurch.org"
```

### **Section 2: Property Details**

```typescript
// NEW FIELDS ADDED:
available_build_sqft: number (optional)
  Label: "Available Build Space (if different from total lot size)"
  Tooltip: "If only part of your property can be developed, enter the buildable area"
  Validation: Must be <= lot_size_sqft
  Help: "Leave blank if entire lot is available for development"

build_area_notes: string (optional - textarea)
  Label: "Build Area Notes"
  Max Length: 500 characters
  Placeholder: "Describe any constraints (e.g., 'Southeast corner available')"
```

---

## ✅ Validation Rules

### **Entity Type**

- **Required**: Yes
- **Type**: Dropdown selection
- **Options**: 5 predefined values

### **EIN Number**

- **Required**: No (optional)
- **Format**: XX-XXXXXXX (9 digits total)
- **Validation**: Regex pattern `^\d{2}-\d{7}$`
- **Security**: Should be encrypted/masked in database

### **Website**

- **Required**: No (optional)
- **Format**: Valid URL (must start with http:// or https://)
- **Validation**: URL validation (Pydantic HttpUrl)

### **Available Build Space**

- **Required**: No (optional)
- **Type**: Number (float)
- **Validation**:
  - Must be positive
  - Must be <= `lot_size_sqft`
  - If provided, triggers warning if < 10,000 sqft
- **Usage**: Overrides `lot_size_sqft` for unit capacity calculations

### **Build Area Notes**

- **Required**: No (optional)
- **Type**: Text (textarea)
- **Max Length**: 500 characters
- **Purpose**: Explain constraints on buildable area

---

## 🔄 Business Logic Impact

### **1. Unit Capacity Calculation**

When `available_build_sqft` is provided:

```python
# In AI Assessment Service
if assessment.available_build_sqft:
    buildable_area = assessment.available_build_sqft
else:
    buildable_area = property_obj.lot_size_sqft

# Calculate units based on buildable area
max_units = calculate_unit_capacity(buildable_area)
```

### **2. Deal Breaker Logic**

Update deal breaker checks:

```python
# Check minimum buildable area (not just lot size)
effective_area = assessment.available_build_sqft or property_obj.lot_size_sqft

if effective_area < 10000:
    deal_breakers.append("Buildable area less than 10,000 sqft minimum")

# Calculate unit capacity based on effective area
feasible_units = calculate_units(effective_area)
if feasible_units < 40:
    deal_breakers.append("Cannot build minimum 40 units")
```

### **3. PDF Report Display**

Show available build space in reports:

```python
# In Property Details section
if assessment.available_build_sqft:
    report.add_field("Total Lot Size", f"{property.lot_size_sqft:,} sqft")
    report.add_field("Available Build Space", f"{assessment.available_build_sqft:,} sqft")
    if assessment.build_area_notes:
        report.add_field("Build Constraints", assessment.build_area_notes)
else:
    report.add_field("Lot Size", f"{property.lot_size_sqft:,} sqft")
```

---

## 📊 Database Migration

### ✅ **NO MIGRATION NEEDED!**

All required database fields already exist in the `churches` table:

- ✅ `tax_exempt_id` → Use for EIN Number
- ✅ `tax_exempt_status` → Use for Entity Type
- ✅ `website_url` → Use for Website

### **Frontend-to-Backend Field Mapping**

```typescript
// Frontend form field → Backend database column
{
  entity_type → tax_exempt_status
  ein_number  → tax_exempt_id
  website     → website_url
}
```

**Action Required:** Update frontend API calls to use correct backend field names.

---

## 🧪 Testing Checklist

### **Frontend Tests**

- [ ] Entity type dropdown renders with all 5 options
- [ ] EIN number input validates format XX-XXXXXXX
- [ ] Website input validates URL format
- [ ] Available build space validates <= lot size
- [ ] Build area notes has 500 char limit
- [ ] Form submits successfully with all new fields
- [ ] Form submits successfully with new fields empty (optional)

### **Backend Tests**

- [ ] Church model accepts new fields
- [ ] EIN number stored securely (encrypted?)
- [ ] Available build space used in unit capacity calc
- [ ] Deal breaker logic uses available_build_sqft when provided
- [ ] PDF report shows available build space
- [ ] API returns new fields in responses

### **Integration Tests**

- [ ] Church submits form with entity type → stored correctly
- [ ] Church submits form with EIN → stored and masked
- [ ] Church submits form with website → validated and stored
- [ ] Church submits form with available build space → used in assessment
- [ ] Build area notes appear in PDF report

---

## 📝 API Payload Example

### **Church Submission Payload**

```json
{
  "church": {
    "name": "Grace Community Church",
    "legal_name": "Grace Community Church of Los Angeles Inc.",
    "entity_type": "501(c)(3) Nonprofit",
    "ein_number": "95-1234567",
    "website": "https://gracecommunityla.org",
    "denomination": "Non-denominational",
    "street_address": "123 Church St",
    "city": "Los Angeles",
    "state": "CA",
    "zip_code": "90012",
    "congregation_size": 450,
    "primary_contact_name": "John Smith",
    "primary_contact_email": "john@gracecommunityla.org",
    "primary_contact_phone": "(323) 555-0100"
  },
  "property": {
    "street_address": "456 Property Ave",
    "city": "Los Angeles",
    "state": "CA",
    "zip_code": "90015",
    "latitude": 34.0407,
    "longitude": -118.2662,
    "lot_size_sqft": 50000,
    "current_usage": "Parking lot"
  },
  "assessment": {
    "available_build_sqft": 30000,
    "build_area_notes": "Southeast corner available. Existing church building occupies 20,000 sqft. Must preserve memorial garden in northwest corner.",
    "parking_spaces_needed_after": 50,
    "congregation_voted": true,
    "vote_percentage": 82,
    "owns_property_free_clear": true,
    "willing_to_ground_lease": true
  }
}
```

---

## 🎯 Priority Implementation Order

### **✅ Phase 1: Backend Updates (COMPLETE!)**

1. ~~Update Church model with 3 new fields~~ ✅ Already exists!
2. ~~Update Church schemas (Pydantic)~~ ✅ Already exists!
3. ~~Create and run database migration~~ ✅ Not needed!
4. ~~Test API endpoints~~ ✅ Already working!

### **Phase 2: Frontend Form (2-3 hours)**

1. Add entity_type dropdown to church info section
2. Add EIN number input with validation
3. Add website input with URL validation
4. Add available build space input to property section
5. Add build area notes textarea
6. Test form submission

### **Phase 3: Business Logic (1-2 hours)**

1. Update unit capacity calculations to use available_build_sqft
2. Update deal breaker logic
3. Update PDF reports to show build constraints
4. Test end-to-end flow

---

## ✅ Completion Checklist

- [ ] Church model updated with entity_type, ein_number, website
- [ ] Database migration created and applied
- [ ] Church schemas updated
- [ ] Assessment model already has available_build_sqft (no changes needed)
- [ ] Frontend form includes all 5 new fields
- [ ] Form validation working correctly
- [ ] Unit capacity calc uses available_build_sqft when provided
- [ ] PDF reports show build constraints
- [ ] End-to-end testing complete

---

## 📞 Questions?

**Q: Should EIN numbers be encrypted in the database?**  
A: Yes, consider encrypting sensitive tax IDs. Use field-level encryption or hash them.

**Q: What if church doesn't know their entity type?**  
A: Make it required but add "Other" option. Help text can explain common types.

**Q: What if available_build_sqft > lot_size_sqft?**  
A: Show validation error: "Build space cannot exceed total lot size"

**Q: Should we show available_build_sqft in the admin dashboard?**  
A: Yes! Show both total lot size and available build space (if different)

---

**Last Updated:** January 2025  
**Status:** Ready for Implementation  
**Priority:** Add to Week 1-2 church submission form 🔥
