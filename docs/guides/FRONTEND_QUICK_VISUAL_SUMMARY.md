# 🎯 Frontend Development - Quick Visual Summary

**Status:** ✅ Documentation Complete | 🚀 Ready to Build  
**Date:** October 5, 2025

---

## 📊 Project Overview

```
Property Intelligence Platform - Frontend
├── Business Model: Churches partner with Logos for affordable housing
├── Backend: ✅ All fields exist (no migration needed!)
├── Frontend: 🚧 Needs to be built
└── Timeline: 8 weeks to MVP
```

---

## 🆕 The 5 New Fields

### Visual Summary Table

| #   | Field Name                | Type                      | Required | Backend Column         | Location  |
| --- | ------------------------- | ------------------------- | -------- | ---------------------- | --------- |
| 1️⃣  | **Entity Type**           | Dropdown (5 options)      | ✅ Yes   | `tax_exempt_status`    | Section 1 |
| 2️⃣  | **EIN Number**            | Masked Input (XX-XXXXXXX) | ⭕ No    | `tax_exempt_id`        | Section 1 |
| 3️⃣  | **Website**               | URL Input                 | ⭕ No    | `website_url`          | Section 1 |
| 4️⃣  | **Available Build Space** | Number Input (sqft)       | ⭕ No    | `available_build_sqft` | Section 2 |
| 5️⃣  | **Build Area Notes**      | Textarea (500 chars)      | ⭕ No    | `build_area_notes`     | Section 2 |

---

## 🏗️ Form Structure (6 Sections)

```
Church Submission Form
│
├── 📋 Section 1: Church Information
│   ├── Church Name, Legal Name, Denomination
│   ├── 🆕 Entity Type (dropdown) ✅ REQUIRED
│   ├── 🆕 EIN Number (masked input)
│   ├── 🆕 Website (URL)
│   └── Contact Information
│
├── 🏘️ Section 2: Property Details
│   ├── Property Address (Google Places autocomplete)
│   ├── Map Picker (Mapbox)
│   ├── Lot Size
│   ├── 🆕 Available Build Space (number)
│   └── 🆕 Build Area Notes (textarea)
│
├── 🏦 Section 3: Ownership & Financial
│   ├── Owns Free & Clear? (boolean) ✅ REQUIRED = true
│   └── Willing to Ground Lease? (boolean)
│
├── 🗳️ Section 4: Congregation Approval
│   ├── Congregation Voted? (boolean)
│   └── Vote Percentage (if voted)
│
├── 🅿️ Section 5: Parking & Development
│   └── Parking Spaces Needed After Development
│
└── 📅 Section 6: Timeline & Preferences
    ├── Timeline Preference
    ├── Preferred Unit Count
    └── Affordability Target
```

---

## 🎨 UI Components to Build

### Phase 1: Church Submission Form (Weeks 1-2)

```
Components/
│
├── Form Layout (3 components)
│   ├── ChurchSubmissionForm.tsx ............ Main container
│   ├── FormStepper.tsx ..................... 6-step progress bar
│   └── FormSection.tsx ..................... Section wrapper
│
├── Section Components (6 components)
│   ├── Section1ChurchInfo.tsx .............. 🆕 Entity, EIN, Website
│   ├── Section2PropertyDetails.tsx ......... 🆕 Build space, Notes
│   ├── Section3Ownership.tsx
│   ├── Section4Approval.tsx
│   ├── Section5Parking.tsx
│   └── Section6Timeline.tsx
│
├── Custom Inputs (5 components) 🆕
│   ├── EntityTypeDropdown.tsx .............. 5 options dropdown
│   ├── EINInput.tsx ........................ Masked XX-XXXXXXX
│   ├── WebsiteInput.tsx .................... URL validation
│   ├── BuildSpaceInput.tsx ................. Number + tooltip
│   └── BuildNotesTextarea.tsx .............. 500 char limit
│
├── Integration Components (3 components)
│   ├── GooglePlacesAutocomplete.tsx
│   ├── MapboxMapPicker.tsx
│   └── FileUploader.tsx
│
├── State Management (3 hooks)
│   ├── useSubmissionForm.ts ................ React Hook Form + Zod
│   ├── useFormAutoSave.ts .................. localStorage
│   └── useSubmitProperty.ts ................ API submission
│
└── Pages (2 components)
    ├── SubmissionThankYou.tsx
    └── SubmissionStatus.tsx
```

**Total: 17 components to build**

---

## ✅ Validation Rules Quick Reference

### Section 1: Church Information

```typescript
✅ church_name         Required
✅ entity_type         Required (dropdown with 5 options)
⭕ ein_number          Optional, format: ^\d{2}-\d{7}$
⭕ website             Optional, valid URL
✅ primary_contact_*   Required (name, email, phone)
```

### Section 2: Property Details

```typescript
✅ property_address    Required (Google Places)
✅ latitude/longitude  Required (map picker)
⭕ lot_size_sqft       Optional
⭕ available_build_sqft Optional, must be <= lot_size_sqft
⭕ build_area_notes    Optional, max 500 chars

⚠️ Warnings:
   - If available_build_sqft < 10,000 → "May not qualify"
   - If available_build_sqft provided → Use for unit capacity
```

### Section 3: Ownership

```typescript
✅ owns_property_free_clear  Required = true (deal breaker!)
✅ willing_to_ground_lease   Required (boolean)
```

### Section 4: Congregation

```typescript
✅ congregation_voted    Required (boolean)
   If true:
   ✅ vote_percentage    Required, must be > 50%
   ⚠️ If < 66% → Warning about support level
```

### Section 5: Parking

```typescript
✅ parking_spaces_needed_after  Required (number)
```

### Section 6: Timeline

```typescript
✅ timeline_preference   Required (dropdown)
⭕ preferred_unit_count  Optional
⭕ affordability_target  Optional
```

---

## 🔧 Backend Field Mapping

### Frontend → Backend Translation

```typescript
// Section 1: Church Information
{
  entity_type  → tax_exempt_status   (Church.tax_exempt_status)
  ein_number   → tax_exempt_id       (Church.tax_exempt_id)
  website      → website_url         (Church.website_url)
}

// Section 2: Property Details
{
  available_build_sqft → available_build_sqft  (Assessment.available_build_sqft)
  build_area_notes     → build_area_notes      (Assessment.build_area_notes)
}
```

**Key Point:** All fields already exist in database! Just map names.

---

## 📅 8-Week Roadmap (Visual Timeline)

```
Week 1-2: 🔥 Church Submission Form (HIGHEST PRIORITY)
┌─────────────────────────────────────────────────────┐
│ ✅ Section 1: Church Info (with 3 NEW fields)      │
│ ✅ Section 2: Property Details (with 2 NEW fields) │
│ ✅ Sections 3-6: Remaining form sections           │
│ ✅ Google Places + Mapbox integration              │
│ ✅ Form validation (Zod)                           │
│ ✅ API submission                                  │
│ ✅ Thank you page                                  │
└─────────────────────────────────────────────────────┘

Week 3-4: Admin Dashboard
┌─────────────────────────────────────────────────────┐
│ ✅ Submissions queue with filters                  │
│ ✅ Submission detail view (show all 5 NEW fields)  │
│ ✅ Assessment scores display                       │
│ ✅ Deal breaker alerts                             │
│ ✅ Approve/reject workflow                         │
└─────────────────────────────────────────────────────┘

Week 5-6: Reports & Pipeline
┌─────────────────────────────────────────────────────┐
│ ✅ PDF report viewer                               │
│ ✅ Pipeline/Kanban board                           │
│ ✅ Deal stage tracking                             │
└─────────────────────────────────────────────────────┘

Week 7-8: Analytics & Polish
┌─────────────────────────────────────────────────────┐
│ ✅ Executive dashboard                             │
│ ✅ ROI metrics                                     │
│ ✅ Testing & bug fixes                             │
│ ✅ Mobile optimization                             │
└─────────────────────────────────────────────────────┘
```

---

## 🚀 Getting Started Commands

### Day 1: Set Up Project

```bash
# Navigate to project
cd /Users/adamsilver/Desktop/property-intelligence-platform

# Create Next.js app
npx create-next-app@latest frontend --typescript --tailwind --app

# Navigate to frontend
cd frontend

# Install core dependencies
npm install react-hook-form zod @hookform/resolvers

# Install UI components
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu
npm install @radix-ui/react-select @radix-ui/react-tabs

# Install map libraries
npm install @googlemaps/js-api-loader mapbox-gl react-map-gl

# Install state management
npm install @tanstack/react-query zustand

# Install utilities
npm install axios date-fns lucide-react clsx tailwind-merge
```

### Day 2: Create Project Structure

```bash
# Create directories
mkdir -p src/components/forms/church-submission
mkdir -p src/components/inputs
mkdir -p src/components/maps
mkdir -p src/hooks
mkdir -p src/lib
mkdir -p src/schemas
mkdir -p src/types
mkdir -p src/app/submit-property

# Create type definitions
touch src/types/submission.ts

# Create validation schema
touch src/schemas/submission.schema.ts

# Create hooks
touch src/hooks/useSubmissionForm.ts
touch src/hooks/useSubmitProperty.ts
touch src/hooks/useFormAutoSave.ts
```

---

## 📋 Component Checklist

### Week 1 Tasks

- [ ] **Day 1:** Project setup + dependencies
- [ ] **Day 2:** Create folder structure + TypeScript types
- [ ] **Day 3:** Build FormStepper + FormSection components
- [ ] **Day 4:** Build Section1ChurchInfo.tsx
  - [ ] Add EntityTypeDropdown component
  - [ ] Add EINInput component (masked)
  - [ ] Add WebsiteInput component
- [ ] **Day 5:** Build Section2PropertyDetails.tsx
  - [ ] Add BuildSpaceInput component
  - [ ] Add BuildNotesTextarea component
  - [ ] Add GooglePlacesAutocomplete
  - [ ] Add MapboxMapPicker

### Week 2 Tasks

- [ ] **Day 6:** Build Section3Ownership.tsx
- [ ] **Day 7:** Build Section4Approval.tsx
- [ ] **Day 8:** Build Section5Parking.tsx
- [ ] **Day 9:** Build Section6Timeline.tsx
- [ ] **Day 10:** Integration
  - [ ] Connect all sections with form state
  - [ ] Add validation with Zod
  - [ ] Add auto-save to localStorage
  - [ ] Build submission API hook
  - [ ] Create thank you page
  - [ ] Test end-to-end flow

---

## 🎨 Entity Type Dropdown Options

```typescript
const ENTITY_TYPE_OPTIONS = [
  {
    value: '501c3_nonprofit',
    label: '501(c)(3) Nonprofit',
    description: 'Tax-exempt nonprofit organization',
  },
  {
    value: 'religious_corporation',
    label: 'Religious Corporation',
    description: 'Incorporated religious entity',
  },
  {
    value: 'church_religious_org',
    label: 'Church/Religious Organization',
    description: 'Unincorporated church or religious group',
  },
  {
    value: 'unincorporated_association',
    label: 'Unincorporated Association',
    description: 'Informal religious association',
  },
  {
    value: 'other',
    label: 'Other',
    description: 'Other entity type (please explain)',
  },
];
```

---

## 💾 API Payload Example

### Frontend Form Submission

```typescript
// POST /properties/submit
{
  // Section 1: Church Information
  "church_name": "Shepherd Community Church",
  "legal_name": "Shepherd Community Church, Inc.",
  "denomination": "Non-denominational",
  "entity_type": "501c3_nonprofit",           // 🆕 NEW FIELD
  "ein_number": "12-3456789",                 // 🆕 NEW FIELD
  "website": "https://shepherdchurch.org",    // 🆕 NEW FIELD
  "street_address": "123 Main St",
  "city": "Los Angeles",
  "state": "CA",
  "zip_code": "90001",
  "congregation_size": "300-500",
  "primary_contact_name": "John Smith",
  "primary_contact_email": "john@shepherdchurch.org",
  "primary_contact_phone": "(555) 123-4567",

  // Section 2: Property Details
  "property_address": "456 Church Ave, Los Angeles, CA 90001",
  "property_city": "Los Angeles",
  "property_state": "CA",
  "property_zip": "90001",
  "latitude": 34.0522,
  "longitude": -118.2437,
  "lot_size_sqft": 50000,
  "available_build_sqft": 30000,             // 🆕 NEW FIELD
  "build_area_notes": "Existing building occupies 20,000 sqft", // 🆕 NEW FIELD
  "current_usage": "Parking lot",

  // Section 3: Ownership & Financial
  "owns_property_free_clear": true,
  "willing_to_ground_lease": true,

  // Section 4: Congregation Approval
  "congregation_voted": true,
  "vote_percentage": 85,
  "leadership_support": "Strong Majority",

  // Section 5: Parking & Development
  "current_parking_spaces": 80,
  "parking_spaces_needed_after": 50,
  "special_requirements": "Need community room for church programs",

  // Section 6: Timeline & Preferences
  "timeline_preference": "12-18 months",
  "preferred_unit_count": 60,
  "affordability_target": "Mix of income levels"
}
```

### Backend Maps To

```python
# Church model receives:
{
  "tax_exempt_status": "501c3_nonprofit",     # From entity_type
  "tax_exempt_id": "12-3456789",              # From ein_number
  "website_url": "https://shepherdchurch.org" # From website
}

# Assessment model receives:
{
  "available_build_sqft": 30000,              # From available_build_sqft
  "build_area_notes": "Existing building..."  # From build_area_notes
}
```

---

## 📚 Documentation Files Reference

| File                                   | Purpose               | Lines |
| -------------------------------------- | --------------------- | ----- |
| `FRONTEND_BUILD_PLAN.md`               | Complete architecture | 1434  |
| `FRONTEND_NEW_FIELDS_SUMMARY.md`       | Field mapping details | 395   |
| `FRONTEND_IMPLEMENTATION_CHECKLIST.md` | Development checklist | 337   |
| `FRONTEND_DOCUMENTATION_COMPLETE.md`   | Final summary         | 500+  |
| `FRONTEND_QUICK_START.md`              | Quick reference       | ~200  |

---

## ✅ Pre-Flight Checklist

Before starting development:

- ✅ Backend is running and accessible
- ✅ Database has all required fields (they exist!)
- ✅ API endpoints are documented and working
- ✅ Google Places API key obtained
- ✅ Mapbox API key obtained
- ✅ Clerk authentication configured
- ✅ All documentation reviewed
- ✅ Development environment set up

---

## 🎯 Success Criteria

### Week 1-2 (Church Form) Success = ✅ When:

1. ✅ Church can submit form with all 6 sections
2. ✅ All 5 NEW fields are functional:
   - Entity type dropdown works
   - EIN input validates format
   - Website input validates URL
   - Available build space calculates correctly
   - Build notes saves with submission
3. ✅ Google Places autocomplete works for addresses
4. ✅ Mapbox map picker sets lat/lng correctly
5. ✅ Form validation catches all errors
6. ✅ Submission sends to backend successfully
7. ✅ Thank you page displays after submission
8. ✅ Form auto-saves to localStorage

### Phase 1 Complete = 🎉 When:

- Churches can submit properties (Weeks 1-2) ✅
- Admins can view submissions (Weeks 3-4) ✅
- Reports can be generated (Weeks 5-6) ✅
- Analytics dashboard works (Weeks 7-8) ✅

---

## 🔥 Start Here!

**👉 Next Action:** Run Day 1 setup commands and start building Section 1!

```bash
cd /Users/adamsilver/Desktop/property-intelligence-platform
npx create-next-app@latest frontend --typescript --tailwind --app
cd frontend
npm install react-hook-form zod @hookform/resolvers
```

**Good luck! 🚀**

---

**Last Updated:** October 5, 2025  
**Status:** 📋 Documentation Complete → 🚀 Ready for Development
