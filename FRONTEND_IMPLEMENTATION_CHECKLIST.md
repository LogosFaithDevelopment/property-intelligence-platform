# 🎯 Frontend Implementation Checklist

**Last Updated:** January 2025  
**Status:** Documentation Complete → Ready for Development

---

## ✅ Documentation Complete

All planning documents have been created and updated:

- ✅ **FRONTEND_BUILD_PLAN.md** - Complete frontend architecture with all fields
- ✅ **FRONTEND_NEW_FIELDS_SUMMARY.md** - Detailed field mapping to backend
- ✅ Business model corrected (churches = external partners submitting ONE property)
- ✅ User personas updated (Churches, Logos Staff, Logos Executives)
- ✅ Page structure defined (Public, Church Portal, Admin Portal)
- ✅ All 5 new fields documented with validation rules

---

## 🔥 Required Fields for Church Submission Form

### **Section 1: Church Information** ✅ Documented

#### Entity & Tax Information (NEW)

| Field         | Type            | Required | Backend Field       | Status            |
| ------------- | --------------- | -------- | ------------------- | ----------------- |
| `entity_type` | dropdown        | Yes      | `tax_exempt_status` | ✅ Backend exists |
| `ein_number`  | string (masked) | No       | `tax_exempt_id`     | ✅ Backend exists |
| `website`     | URL             | No       | `website_url`       | ✅ Backend exists |

**Options for `entity_type` dropdown:**

- 501(c)(3) Nonprofit
- Religious Corporation
- Church/Religious Organization
- Unincorporated Association
- Other

**Validation:**

- EIN format: `XX-XXXXXXX` (regex: `^\d{2}-\d{7}$`)
- Website: Valid URL format (`https://...`)

---

### **Section 2: Property Details** ✅ Documented

#### Available Build Space (NEW)

| Field                  | Type     | Required | Backend Field          | Status            |
| ---------------------- | -------- | -------- | ---------------------- | ----------------- |
| `available_build_sqft` | number   | No       | `available_build_sqft` | ✅ Backend exists |
| `build_area_notes`     | textarea | No       | `build_area_notes`     | ✅ Backend exists |

**Validation:**

- `available_build_sqft` must be ≤ `lot_size_sqft`
- `build_area_notes` max 500 characters
- Warning if `available_build_sqft` < 10,000 sqft

**Business Logic:**

```typescript
// Use available_build_sqft for unit capacity if provided
const buildable_area = available_build_sqft || lot_size_sqft;
const max_units = calculateUnitCapacity(buildable_area);
```

---

### **Section 3: Ownership & Financial** ✅ Documented

| Field                      | Type    | Required | Status        |
| -------------------------- | ------- | -------- | ------------- |
| `owns_property_free_clear` | boolean | Yes      | ✅ Documented |
| `willing_to_ground_lease`  | boolean | Yes      | ✅ Documented |

**Deal Breaker:**

- If `owns_property_free_clear === false` → Cannot proceed

---

### **Section 4: Congregation Approval** ✅ Documented

| Field                | Type           | Required    | Status        |
| -------------------- | -------------- | ----------- | ------------- |
| `congregation_voted` | boolean        | Yes         | ✅ Documented |
| `vote_percentage`    | number (0-100) | Conditional | ✅ Documented |

**Validation:**

- If `congregation_voted === true`, `vote_percentage` required
- Must be >50% to proceed
- Warning if <66%

---

### **Section 5: Parking & Development** ✅ Documented

| Field                         | Type   | Required | Status        |
| ----------------------------- | ------ | -------- | ------------- |
| `parking_spaces_needed_after` | number | Yes      | ✅ Documented |

---

### **Section 6: Timeline & Preferences** ✅ Documented

| Field                  | Type     | Required | Status        |
| ---------------------- | -------- | -------- | ------------- |
| `timeline_preference`  | dropdown | Yes      | ✅ Documented |
| `preferred_unit_count` | number   | No       | ✅ Documented |
| `affordability_target` | dropdown | No       | ✅ Documented |

---

## 🚧 What Still Needs to Be Built

### **Phase 1 (Weeks 1-2): Church Submission Form** 🔥 HIGHEST PRIORITY

**Frontend Components to Build:**

#### 1. Form Layout Components

- [ ] `ChurchSubmissionForm.tsx` - Main multi-step form container
- [ ] `FormStepper.tsx` - Step progress indicator (6 steps)
- [ ] `FormSection.tsx` - Reusable section wrapper

#### 2. Section Components

- [ ] `Section1ChurchInfo.tsx` - Church details + NEW entity/EIN/website fields
- [ ] `Section2PropertyDetails.tsx` - Property info + NEW available build space fields
- [ ] `Section3Ownership.tsx` - Ownership & financial questions
- [ ] `Section4Approval.tsx` - Congregation voting questions
- [ ] `Section5Parking.tsx` - Parking & development requirements
- [ ] `Section6Timeline.tsx` - Timeline & preferences

#### 3. Custom Input Components

- [ ] `EntityTypeDropdown.tsx` - Dropdown with 5 entity type options
- [ ] `EINInput.tsx` - Masked input (XX-XXXXXXX format)
- [ ] `WebsiteInput.tsx` - URL input with validation
- [ ] `BuildSpaceInput.tsx` - Number input with tooltip/help text
- [ ] `BuildNotesTextarea.tsx` - Textarea (max 500 chars) with character count

#### 4. Integration Components

- [ ] `GooglePlacesAutocomplete.tsx` - Property address search
- [ ] `MapboxMapPicker.tsx` - Interactive map for lat/lng selection
- [ ] `FileUploader.tsx` - Upload property photos (optional)

#### 5. Validation & State Management

- [ ] `useSubmissionForm.ts` - Form state hook (React Hook Form + Zod)
- [ ] `submission.schema.ts` - Zod validation schema with all rules
- [ ] `useFormAutoSave.ts` - Local storage auto-save hook

#### 6. API Integration

- [ ] `useSubmitProperty.ts` - API hook for form submission
- [ ] `useCheckSubmissionStatus.ts` - Check submission status

#### 7. Confirmation & Status Pages

- [ ] `SubmissionThankYou.tsx` - Success page after submission
- [ ] `SubmissionStatus.tsx` - Simple status tracker (no scores/reports)

---

### **Phase 2 (Weeks 3-4): Logos Admin Dashboard**

**Components to Build:**

#### 1. Dashboard Layout

- [ ] `AdminDashboard.tsx` - Main dashboard with metrics
- [ ] `SubmissionsQueue.tsx` - List of pending submissions
- [ ] `SubmissionBadges.tsx` - Badge counts (New, In Review, Qualified, Rejected)

#### 2. Submission Review

- [ ] `SubmissionDetailView.tsx` - Full submission details
- [ ] `AssessmentScoresCard.tsx` - Display all 12 assessment scores
- [ ] `DealBreakerAlerts.tsx` - Red flag warnings
- [ ] `ApproveRejectButtons.tsx` - Workflow actions

#### 3. Property Enrichment

- [ ] `EnrichmentStatus.tsx` - Show auto-enrichment progress
- [ ] `ManualEnrichmentForm.tsx` - Override/add missing data
- [ ] `PropertyDataTabs.tsx` - Zoning, demographics, crime, transit, etc.

---

### **Phase 3 (Weeks 5-6): Reports & Pipeline**

**Components to Build:**

#### 1. PDF Reports

- [ ] `PDFReportViewer.tsx` - Embedded PDF viewer
- [ ] `GenerateReportButton.tsx` - Trigger report generation
- [ ] `ReportDownloadLink.tsx` - Download PDF

#### 2. Pipeline/Kanban

- [ ] `PipelineBoard.tsx` - Drag-and-drop Kanban board
- [ ] `DealStageCard.tsx` - Deal cards (Submitted → Qualified → Approved → Development)
- [ ] `DealProgressTracker.tsx` - Timeline view

---

### **Phase 4 (Weeks 7-8): Analytics & Polish**

**Components to Build:**

#### 1. Executive Dashboard

- [ ] `ExecutiveDashboard.tsx` - High-level metrics
- [ ] `ROIMetricsCard.tsx` - Financial projections
- [ ] `QualifiedLeadsFilter.tsx` - Filter by score (75+)

#### 2. Testing & Optimization

- [ ] Unit tests for validation logic
- [ ] Integration tests for form submission
- [ ] Mobile responsive testing
- [ ] Accessibility testing (WCAG 2.1 AA)

---

## 📦 Backend Status (No Work Needed!)

### Database Fields

✅ **All fields already exist** in the database:

| Frontend Field         | Backend Column         | Model      | Status    |
| ---------------------- | ---------------------- | ---------- | --------- |
| `entity_type`          | `tax_exempt_status`    | Church     | ✅ Exists |
| `ein_number`           | `tax_exempt_id`        | Church     | ✅ Exists |
| `website`              | `website_url`          | Church     | ✅ Exists |
| `available_build_sqft` | `available_build_sqft` | Assessment | ✅ Exists |
| `build_area_notes`     | `build_area_notes`     | Assessment | ✅ Exists |

### API Endpoints

✅ **All endpoints already exist** in `/backend/app/routers/properties.py`:

- `POST /properties/submit` - Church submission endpoint
- `GET /properties/{id}` - Get property details
- `POST /properties/{id}/enrich` - Trigger enrichment
- `GET /assessments/{property_id}` - Get assessment scores

### Schemas

✅ **All schemas already support new fields**:

- `ChurchCreate` schema has `tax_exempt_id`, `tax_exempt_status`, `website_url`
- `AssessmentCreate` schema has `available_build_sqft`, `build_area_notes`

---

## 🎯 Next Steps

### Immediate Actions (Start Week 1)

1. **Set up frontend project structure**

   ```bash
   cd frontend
   npm install
   ```

2. **Install required dependencies**

   ```bash
   npm install react-hook-form zod @hookform/resolvers
   npm install @googlemaps/js-api-loader
   npm install mapbox-gl react-map-gl
   npm install axios react-query
   npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu
   ```

3. **Create base form structure**

   - Create `src/components/forms/church-submission/` folder
   - Set up TypeScript types for all form fields
   - Create Zod validation schema

4. **Build Section 1 first** (Church Information)

   - Implement entity_type dropdown
   - Implement EIN number masked input
   - Implement website URL input
   - Add validation for all fields

5. **Test Section 1 before moving to Section 2**
   - Validate form submission
   - Test field mapping to backend
   - Verify error handling

---

## 📚 Reference Documents

- **FRONTEND_BUILD_PLAN.md** - Complete architecture and component specs
- **FRONTEND_NEW_FIELDS_SUMMARY.md** - Field mapping and backend details
- **backend/app/models/church.py** - Church model with existing fields
- **backend/app/models/assessment.py** - Assessment model with build space fields
- **backend/app/schemas/church.py** - Church schemas for API payloads

---

## 🚨 Critical Notes

1. **Churches have LIMITED access** - No scores, no reports, only submission + status
2. **Logos Staff have FULL access** - All data, scores, enrichment, approval workflow
3. **All 5 new fields already exist in backend** - No database migration needed!
4. **Focus on form validation** - Especially entity_type (required), EIN format, build space logic
5. **Week 1-2 is HIGHEST PRIORITY** - Get church submission form working first

---

## ✅ Ready to Start Development!

All planning is complete. You can now:

- Start building the church submission form (Phase 1)
- Follow the 8-week MVP roadmap
- Reference FRONTEND_BUILD_PLAN.md for detailed component specs
- Reference FRONTEND_NEW_FIELDS_SUMMARY.md for backend field mapping

**No backend work required** - All fields exist, just need to build the frontend! 🎉
