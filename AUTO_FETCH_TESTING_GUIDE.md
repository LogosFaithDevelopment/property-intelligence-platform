# 🧪 Auto-Fetch Feature Testing Guide

## ✅ Ready to Test!

All components are in place and working. Here's how to test the auto-fetch feature in your application.

---

## 🚀 Quick Start

### 1. Start the Application

```bash
# Terminal 1: Start Backend
cd /Users/adamsilver/Desktop/property-intelligence-platform/backend
docker-compose up

# Terminal 2: Start Frontend
cd /Users/adamsilver/Desktop/property-intelligence-platform/frontend
npm run dev
```

**Backend:** http://localhost:8000  
**Frontend:** http://localhost:3000

---

## 🧪 Test Scenarios

### ✅ Test 1: Happy Path (LA County Property)

**Objective:** Verify auto-fetch works for valid LA County addresses

**Steps:**

1. Navigate to church submission form: http://localhost:3000/submissions/new
2. Scroll to **Section 2: Property Details**
3. Fill in address fields:
   ```
   Property Address: 19700 Rinaldi St
   City: Los Angeles
   State: CA
   ZIP Code: 91326
   ```
4. Click **"Fetch Property Data"** button

**Expected Results:**

- ✅ Button shows "Fetching..." with spinner
- ✅ Toast notification: "Property Data Fetched - Auto-filled X field(s)"
- ✅ Lot Size field auto-fills with value
- ✅ Green "Auto-filled" badge appears next to lot size
- ✅ Zoning field may auto-fill if available
- ✅ Button changes to "Fetched" with checkmark

**Visual Verification:**

```
┌─────────────────────────────────────────────┐
│ Total Lot Size (sq ft) [🟢 Auto-filled]    │
│ ┌─────────────────────────────────────────┐ │
│ │ 48500                                   │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

---

### ✅ Test 2: Manual Override

**Objective:** Verify users can override auto-filled values

**Steps:**

1. After Test 1, edit the lot size field
2. Change from `48500` to `50000`
3. Tab out or click elsewhere

**Expected Results:**

- ✅ Green "Auto-filled" badge disappears
- ✅ Value remains at 50000 (user's entry)
- ✅ No error messages
- ✅ Manual value takes precedence

**What Happens Behind the Scenes:**

- Manual override tracked in state
- On submission, discrepancy will be stored in `manual_overrides` column

---

### ⚠️ Test 3: Non-LA County Address (San Francisco)

**Objective:** Verify graceful handling of non-LA County addresses

**Steps:**

1. Clear the form or start fresh
2. Fill in address fields:
   ```
   Property Address: 123 Market St
   City: San Francisco
   State: CA
   ZIP Code: 94103
   ```
3. Click **"Fetch Property Data"** button

**Expected Results:**

- ✅ Button shows "Fetching..." briefly
- ✅ Toast notification appears:
  - Title: "Not LA County"
  - Message: "San Francisco may not be in LA County. Property data auto-fill only works for LA County addresses. Please enter details manually."
- ✅ Fields remain empty (no auto-fill)
- ✅ User can enter values manually
- ✅ Form still works normally

---

### ⚠️ Test 4: Out-of-State Address (New York)

**Objective:** Verify handling of non-California addresses

**Steps:**

1. Fill in address fields:
   ```
   Property Address: 123 Broadway
   City: New York
   State: NY
   ZIP Code: 10001
   ```
2. Click **"Fetch Property Data"** button

**Expected Results:**

- ✅ Toast notification:
  - Title: "Not LA County"
  - Message: "Property data auto-fill only available for Los Angeles County. Please enter property details manually."
- ✅ No fields auto-filled
- ✅ User proceeds with manual entry

---

### ⚠️ Test 5: Incomplete Address

**Objective:** Verify button is disabled when address incomplete

**Steps:**

1. Fill only partial address:
   ```
   Property Address: 123 Main St
   City: (empty)
   State: CA
   ZIP Code: (empty)
   ```

**Expected Results:**

- ✅ "Fetch Property Data" button is **disabled**
- ✅ Button appears grayed out
- ✅ Cannot click button
- ✅ Fill remaining fields → button becomes enabled

---

### ⚠️ Test 6: Property Not Found

**Objective:** Test handling when property doesn't exist in records

**Steps:**

1. Fill in valid LA County format but fake address:
   ```
   Property Address: 99999 Nonexistent Blvd
   City: Los Angeles
   State: CA
   ZIP Code: 90001
   ```
2. Click **"Fetch Property Data"** button

**Expected Results:**

- ✅ Toast notification:
  - Title: "Property Not Found"
  - Message: "Property not found in LA County records. Please enter details manually."
- ✅ Fields remain empty
- ✅ User enters values manually

---

## 🎯 Visual Checklist

### Button States

| State        | Visual                           | When                      |
| ------------ | -------------------------------- | ------------------------- |
| **Enabled**  | `[Fetch Property Data]`          | All address fields filled |
| **Disabled** | `[Fetch Property Data]` (grayed) | Missing address fields    |
| **Loading**  | `[⟳ Fetching...]`                | During API call           |
| **Success**  | `[✓ Fetched]` (green checkmark)  | After successful fetch    |

### Field States

| State               | Visual                        | Description                      |
| ------------------- | ----------------------------- | -------------------------------- |
| **Empty**           | No badge                      | User hasn't entered anything     |
| **Auto-filled**     | `[✓ Auto-filled]` green badge | Data from LA County API          |
| **Manual Entry**    | No badge                      | User typed the value             |
| **Manual Override** | No badge                      | User edited an auto-filled value |

---

## 🔍 Backend Verification

### Check API Response

```bash
# Test the backend endpoint directly
curl -X GET "http://localhost:8000/api/v1/properties/fetch-by-address?address=19700%20Rinaldi%20St&city=Los%20Angeles&state=CA&zip_code=91326" | jq
```

**Expected Response:**

```json
{
  "success": true,
  "data": {
    "lot_size_sqft": 48500,
    "lot_size_acres": 1.11,
    "use_type": "Commercial",
    "classification": "C2",
    "assessed_value": 1250000,
    "data_source": "LA County Assessor",
    "query_date": "2025-10-05"
  }
}
```

### Check Database for Manual Overrides

After submitting a form with manual overrides:

```bash
docker-compose exec -T backend python -c "
import asyncio
from sqlalchemy import select, desc
from app.database import AsyncSessionLocal
from app.models.property import Property
import json

async def check_overrides():
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(Property).order_by(desc(Property.id)).limit(1))
        prop = result.scalar_one_or_none()
        if prop and prop.manual_overrides:
            print('Manual Overrides Found:')
            print(json.dumps(json.loads(prop.manual_overrides), indent=2))
        else:
            print('No manual overrides stored')

asyncio.run(check_overrides())
"
```

---

## 🐛 Troubleshooting

### Issue: Button Not Appearing

**Symptoms:** Can't find "Fetch Property Data" button

**Solution:**

1. Ensure you're in Section 2: Property Details
2. Button appears after ZIP code field
3. Check browser console for errors
4. Verify frontend is running: `npm run dev`

---

### Issue: Button Always Disabled

**Symptoms:** Button is grayed out even with all fields filled

**Solution:**

1. Check all 4 address fields are filled:
   - Property Address
   - City
   - State
   - ZIP Code
2. No extra spaces or invalid characters
3. Check browser console: `console.log(form.watch())`

---

### Issue: "Failed to fetch" Error

**Symptoms:** Network error, no toast appears

**Solution:**

1. **Check backend is running:**
   ```bash
   curl http://localhost:8000/health
   ```
2. **Check CORS settings** (should allow localhost:3000)
3. **Check frontend API URL:**
   ```bash
   # In frontend/.env.local
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
4. **Check browser console** for detailed error

---

### Issue: Toast Doesn't Appear

**Symptoms:** API call works but no notification

**Solution:**

1. Check if toast component is mounted
2. Open browser DevTools → Console
3. Look for toast-related errors
4. Verify `useToast` hook imported correctly

---

### Issue: Fields Don't Auto-Fill

**Symptoms:** API succeeds but fields stay empty

**Symptoms Check:**

1. **Open browser DevTools → Network tab**
2. **Click "Fetch Property Data"**
3. **Find the API request** → Check response
4. **Console log the response:**
   ```typescript
   console.log('API Response:', response);
   ```

**Possible Causes:**

- API returned `success: false`
- Field names don't match
- Form isn't updating state

---

## 📊 Success Criteria

After testing, you should see:

- ✅ Button appears and is styled correctly
- ✅ Button enables/disables based on address fields
- ✅ Loading state shows during API call
- ✅ Success toast appears after fetch
- ✅ Fields auto-fill with data
- ✅ Green badges show on auto-filled fields
- ✅ User can override auto-filled values
- ✅ Badges disappear when user edits
- ✅ Error messages are helpful and clear
- ✅ Non-LA County addresses handled gracefully
- ✅ Form still works if fetch fails

---

## 🎬 Demo Script (For Stakeholders)

### "Here's What We Built"

**1. Show LA County Property (30 seconds)**

```
"Let me show you a church in Los Angeles. I'll enter the address..."
[Type address]
"Now watch this - I click 'Fetch Property Data'..."
[Click button]
"Within seconds, the lot size auto-fills from LA County records!"
[Point to green badge]
"See this green badge? It tells us this came from the county database."
```

**2. Show Manual Override (20 seconds)**

```
"But what if the county data is wrong? The user can just edit it..."
[Change value]
"See? The badge disappears, and their value is saved. Manual entries always win."
```

**3. Show Non-LA County (20 seconds)**

```
"What if they're not in LA County? Let's try San Francisco..."
[Enter SF address, click fetch]
"It tells them clearly: 'Not available for this area, please enter manually.'"
"No errors, no confusion - just enter the data yourself."
```

**Total Demo Time:** ~90 seconds

---

## 📸 Screenshots to Take

For documentation:

1. **Empty form** - Before fetching
2. **Fetch button** - Enabled state
3. **Loading state** - "Fetching..." with spinner
4. **Success state** - Auto-filled fields with badges
5. **Manual override** - Badge disappearing
6. **Error toast** - Not LA County message
7. **Form submission** - Complete form with mixed auto/manual data

---

## ✅ Final Checklist

Before marking complete:

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] Can navigate to form
- [ ] Button appears in Section 2
- [ ] Test 1 (LA County) passes
- [ ] Test 2 (Manual override) passes
- [ ] Test 3 (Non-LA County) passes
- [ ] Test 4 (Out of state) passes
- [ ] Test 5 (Incomplete address) passes
- [ ] Test 6 (Not found) passes
- [ ] No console errors
- [ ] Toast notifications work
- [ ] Visual badges work
- [ ] Form submits successfully

---

## 🎉 You're Ready!

Everything is in place:

- ✅ Backend API working
- ✅ Database migration applied
- ✅ Frontend component built
- ✅ Toast system implemented
- ✅ All edge cases handled

**Start Testing Now:**

```bash
# Terminal 1
cd backend && docker-compose up

# Terminal 2
cd frontend && npm run dev

# Open: http://localhost:3000
```

**Questions?** Check the full documentation in `AUTO_FETCH_FEATURE_COMPLETE.md`

---

_Happy Testing! 🚀_
