# 🛠️ Backend Scripts & Utilities

**Last Updated:** October 11, 2025

This directory contains utility scripts, one-off tests, and admin tools that support the Property Intelligence Platform backend.

---

## 📂 Directory Structure

```
scripts/
├── admin/          # Admin user management scripts
├── testing/        # One-off test scripts (not pytest tests)
├── utilities/      # Helper scripts for data operations
└── README.md       # This file
```

---

## 👥 Admin Scripts (`admin/`)

Scripts for managing admin users and roles.

### `assign_admin_role.py`

Assign or update admin roles for Clerk users.

```bash
# Usage
python scripts/admin/assign_admin_role.py <clerk_user_id> <email> <role>

# Example
python scripts/admin/assign_admin_role.py user_2abc123XYZ adam@logos.com superadmin

# Roles: superadmin, admin, viewer
```

### `create_superuser.py`

Interactive CLI to create the first superuser admin account.

```bash
python scripts/admin/create_superuser.py
```

### `create_superuser_simple.py`

Simplified version for programmatic superuser creation.

```bash
python scripts/admin/create_superuser_simple.py
```

---

## 🧪 Testing Scripts (`testing/`)

One-off test scripts used during development. These are **NOT** pytest tests.

**Note:** For formal pytest tests, see `backend/tests/`

### Property Testing

- `test_85th_street.py` - Test Smarty data for 706 W 85th St
- `test_la_county_api.py` - Test LA County API integration
- `test_attom_api.py` - Test ATTOM API calls
- `test_attom_integration.py` - Test ATTOM data integration
- `test_attom_lot_size.py` - Test lot size calculations
- `test_smarty_*.py` - Various Smarty Streets API tests

### Assessment Testing

- `test_assessment_50.py` - Test assessment #50
- `test_manual_assessment.py` - Manual assessment testing
- `test_reassess_50.py` - Re-assessment testing
- `test_gpt4o_assessment.py` - GPT-4 assessment testing
- `test_ai_grading_with_build_space.py` - AI grading with build space

### API Testing

- `test_census_fema_direct.py` - Census & FEMA API tests
- `test_hud_*.py` - Various HUD API tests
- `test_enrichment_*.py` - Data enrichment tests

### Church Properties

- `test_elevation_church.py` - Elevation Church property test
- `test_la_church_complete.py` - LA Church complete flow test
- `test_oasis_church_full.py` - Oasis Church full test
- `test_shepherd_church_*.py` - Shepherd Church tests

### PDF & Reports

- `test_pdf_generation.py` - PDF generation testing
- `test_generate_report_29.py` - Report #29 generation
- `test_generate_oasis_report.py` - Oasis report generation
- `test_oasis_report.py` - Oasis report validation

### Integration Tests

- `test_phase2_3.py` - Phase 2 & 3 integration test
- `test_phase4_integration.py` - Phase 4 integration test
- `test_complete_flow_with_build_space.py` - Complete flow test
- `test_end_to_end_flow.py` - End-to-end flow test

### Geographic/Disaster

- `test_geographic_filtering.py` - Geographic filtering
- `test_nearby_fires.py` - Nearby fires detection
- `test_la_fire_distances.py` - LA fire distance calculations
- `test_disaster_enrichment.py` - Disaster data enrichment
- `test_check_fire_events.py` - Fire event checking

### Miscellaneous

- `test_create_enriched_property.py` - Property enrichment
- `test_enrichment_speed.py` - Enrichment performance
- `test_quick_api.py` - Quick API tests
- `test_specific_assessment.py` - Specific assessment testing

---

## 🔧 Utility Scripts (`utilities/`)

Helper scripts for data operations, report generation, and debugging.

### Data Checking

- `check_assessment_38.py` - Check assessment #38 data
- `check_assessment_risk_factors.py` - Verify risk factor calculations
- `check_shepherd_disaster_data.py` - Check Shepherd property disaster data

### Report Generation

- `generate_report_41.py` - Generate report for property #41
- `generate_sample_pdf.py` - Generate sample PDF report
- `generate_shepherd_pdf.py` - Generate Shepherd Church PDF
- `generate_shepherd_pdf_fixed.py` - Fixed version of Shepherd PDF

### Data Operations

- `recalculate_irr.py` - Recalculate IRR for properties
- `regenerate_assessment.py` - Regenerate assessment for a property (from root)
- `rerun_assessment_50.py` - Re-run assessment #50 (from root)
- `fetch_second_address.py` - Fetch Smarty data for secondary address

### Database Cleanup

- `delete_jack_submission.sql` - SQL to delete Jack's test submission
- `delete_test_churches.sql` - SQL to delete test church records
- `delete_test_churches.sh` - Shell script to clean up test churches

### Test Data

- `la_county_test_result.json` - LA County API test result data

---

## 🚀 Usage Guidelines

### Running Scripts

Most scripts can be run directly from the backend directory:

```bash
# From backend directory
python scripts/admin/assign_admin_role.py user_123 email@example.com admin
python scripts/testing/test_85th_street.py
python scripts/utilities/check_assessment_38.py
```

### Environment Requirements

All scripts require:

- Active virtual environment: `source venv/bin/activate`
- Environment variables loaded (`.env` file)
- Database connection available (for most scripts)
- API keys configured (for API testing scripts)

### Before Running Tests

```bash
# Activate virtual environment
cd backend
source venv/bin/activate

# Ensure environment variables are loaded
cat .env  # Verify .env exists

# Run script
python scripts/testing/test_85th_street.py
```

---

## 📋 Script Categories

### By Purpose:

**Admin Management:**

- All files in `scripts/admin/`

**API Testing:**

- `test_attom_*.py`
- `test_census_fema_*.py`
- `test_hud_*.py`
- `test_smarty_*.py`
- `test_la_county_api.py`

**Property Analysis:**

- `test_*_church_*.py`
- `test_85th_street.py`
- `check_assessment_*.py`

**Report Generation:**

- `generate_*.py`
- `test_*_report.py`
- `test_pdf_generation.py`

**Data Operations:**

- `recalculate_*.py`
- `regenerate_*.py`
- `rerun_*.py`
- `fetch_*.py`

---

## ⚠️ Important Notes

### Not Pytest Tests

The scripts in `scripts/testing/` are **NOT** formal pytest tests. They are one-off debugging and verification scripts created during development.

**For formal pytest tests, see:** `backend/tests/`

### Script Maintenance

Many of these scripts were created for specific debugging scenarios and may:

- Reference specific property IDs (e.g., assessment #38, #50)
- Use hardcoded addresses
- Contain experimental code
- Not be maintained regularly

### Production Use

These scripts are **NOT** intended for production use. They are development tools for:

- Debugging issues
- Testing API integrations
- Verifying data calculations
- Generating test reports
- Admin user management

---

## 🗂️ File Count

- **Admin Scripts:** 3 files
- **Testing Scripts:** 61 Python files + 3 PDFs
- **Utility Scripts:** 15 files (12 Python + 2 SQL + 1 shell script + 1 JSON)

**Total:** 79 scripts + 4 data files organized

---

## 🔍 Finding Scripts

### By Property:

```bash
# Manchester property (709 W Manchester + 706 W 85th St)
ls scripts/testing/*85th* scripts/testing/*manchester*

# Shepherd Church
ls scripts/testing/*shepherd* scripts/utilities/*shepherd*

# Oasis Church
ls scripts/testing/*oasis*
```

### By Feature:

```bash
# PDF/Report generation
ls scripts/testing/*pdf* scripts/testing/*report* scripts/utilities/generate_*

# Assessment/Grading
ls scripts/testing/*assessment* scripts/testing/*grading* scripts/utilities/check_assessment*

# API Integration
ls scripts/testing/test_*api* scripts/testing/test_attom* scripts/testing/test_hud*
```

### By Date:

```bash
# Recently modified
ls -lt scripts/testing/ | head -20
ls -lt scripts/utilities/ | head -10
```

---

## 📝 Contributing

When adding new scripts:

1. **Choose the right directory:**

   - Admin tasks → `scripts/admin/`
   - Testing/debugging → `scripts/testing/`
   - Data operations → `scripts/utilities/`

2. **Use descriptive names:**

   - Tests: `test_<feature>_<variant>.py`
   - Utilities: `<action>_<target>.py` (e.g., `check_assessment_38.py`)
   - Admin: `<action>_<noun>.py` (e.g., `assign_admin_role.py`)

3. **Add docstrings:**

   ```python
   #!/usr/bin/env python3
   """
   Brief description of what the script does
   Usage: python scripts/testing/test_example.py
   """
   ```

4. **Make scripts executable (optional):**
   ```bash
   chmod +x scripts/testing/test_example.py
   ```

---

## 🧹 Cleanup Recommendations

Some scripts may be obsolete and could be archived or deleted:

- Empty files: `test_end_to_end_flow.py`, `test_hud_api_fixed.py`, `test_quick_api.py`
- Duplicate/similar tests: Multiple `test_shepherd_*` variants, multiple `test_hud_*` variants
- Old debugging scripts: Consider archiving scripts not used in 3+ months

---

**Need to run a script?** Most scripts include usage instructions in their docstring at the top of the file.

**Need formal tests?** See `backend/tests/` for pytest test suites.
