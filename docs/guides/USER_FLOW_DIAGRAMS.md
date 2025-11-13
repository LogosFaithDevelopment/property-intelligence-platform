# 🎯 User Flow Diagrams - Property Intelligence Platform

**Visual guide to all user journeys**

---

## 📋 Table of Contents

1. [Church Admin Flow](#church-admin-flow)
2. [Property Analyst Flow](#property-analyst-flow)
3. [Executive Flow](#executive-flow)
4. [Page Wireframes](#page-wireframes)
5. [Component Hierarchy](#component-hierarchy)

---

## 👤 Flow 1: Church Administrator Journey

### **Goal:** Submit property and get assessment

```
┌─────────────────────────────────────────────────────────────────┐
│                     CHURCH ADMIN JOURNEY                         │
└─────────────────────────────────────────────────────────────────┘

START
  │
  ├─> [Landing Page]
  │     • Value proposition
  │     • How it works
  │     • CTA: "Get Started"
  │
  ├─> [Sign Up/Login] (Clerk)
  │     • Email/password or SSO
  │     • Email verification
  │
  ├─> [Onboarding] (First-time users)
  │     • "Tell us about your church"
  │     • Name, location, size
  │     • Skip option available
  │
  ├─> [Dashboard] ⭐ Main Hub
  │     ┌──────────────────────────┐
  │     │ Welcome Card             │
  │     │ "Add your first property"│
  │     ├──────────────────────────┤
  │     │ Quick Stats (if data)    │
  │     │ - Properties submitted   │
  │     │ - Assessments completed  │
  │     ├──────────────────────────┤
  │     │ Recent Activity          │
  │     │ - Property updates       │
  │     │ - Assessment results     │
  │     └──────────────────────────┘
  │       │
  │       ├─> [Add Property Button]
  │       │     │
  │       │     ├─> [Property Form]
  │       │     │     Step 1: Address
  │       │     │     • Google Places autocomplete
  │       │     │     • Map preview
  │       │     │     • Confirm location
  │       │     │     │
  │       │     │     Step 2: Details
  │       │     │     • Lot size (optional)
  │       │     │     • Current use
  │       │     │     • Zoning (optional)
  │       │     │     │
  │       │     │     Step 3: Church
  │       │     │     • Select existing church
  │       │     │     • OR create new church
  │       │     │     │
  │       │     │     Step 4: Review
  │       │     │     • Summary of info
  │       │     │     • Submit button
  │       │     │
  │       │     ├─> [Property Created!]
  │       │           • Success message
  │       │           • "Request Assessment" button
  │       │
  │       ├─> [Request Assessment]
  │             │
  │             ├─> [Enrichment Started]
  │             │     • Progress indicator
  │             │     • "7 APIs running..."
  │             │     • Estimated time: 2-3 min
  │             │     │
  │             │     [Email Notification]
  │             │     "Your assessment is ready!"
  │             │
  │             ├─> [Assessment Results] ⭐ KEY PAGE
  │                   ┌────────────────────────────────┐
  │                   │ Grade Badge: B (73.8/100)      │
  │                   ├────────────────────────────────┤
  │                   │ RECOMMENDATION                 │
  │                   │ ✗ NOT RECOMMENDED              │
  │                   │ Deal Breaker: 4 units only     │
  │                   ├────────────────────────────────┤
  │                   │ Score Breakdown                │
  │                   │ - Financial: 50/100 ✗          │
  │                   │ - Market: 97/100 ✓             │
  │                   │ - Location: 75/100 ✓           │
  │                   │ - Partnership: 100/100 ✓       │
  │                   │ - Risk: 39/100 ✗               │
  │                   ├────────────────────────────────┤
  │                   │ Key Data Cards                 │
  │                   │ - Financial projections        │
  │                   │ - Market analysis              │
  │                   │ - Risk assessment              │
  │                   ├────────────────────────────────┤
  │                   │ Actions                        │
  │                   │ [Download PDF] [Share] [Help]  │
  │                   └────────────────────────────────┘
  │                         │
  │                         ├─> [Download PDF Report]
  │                         │     • Professional report
  │                         │     • Share with board
  │                         │
  │                         ├─> [View Recommendations]
  │                               • Next steps
  │                               • How to fix issues
  │
  └─> [Help/Support]
        • Documentation
        • Video tutorials
        • Contact support

END
```

### **Key Screens**

1. **Dashboard** - Overview and quick actions
2. **Property Form** - Multi-step wizard
3. **Assessment Results** - Main value delivery
4. **PDF Report** - Professional output

---

## 🔍 Flow 2: Property Analyst (Logos Staff)

### **Goal:** Process multiple properties efficiently

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROPERTY ANALYST JOURNEY                      │
└─────────────────────────────────────────────────────────────────┘

START
  │
  ├─> [Login] (Clerk - Staff role)
  │
  ├─> [Analyst Dashboard] ⭐ Power User View
  │     ┌──────────────────────────────────────┐
  │     │ TODAY'S QUEUE                        │
  │     │ - 5 pending enrichments              │
  │     │ - 3 ready for review                 │
  │     │ - 2 awaiting approval                │
  │     ├──────────────────────────────────────┤
  │     │ THIS WEEK                            │
  │     │ - 23 properties processed            │
  │     │ - 8 approved for development         │
  │     │ - 4 deal breakers identified         │
  │     ├──────────────────────────────────────┤
  │     │ ALERTS                               │
  │     │ ⚠️ 2 properties need attention       │
  │     │ ✓ 1 executive approval pending       │
  │     └──────────────────────────────────────┘
  │       │
  │       ├─> [Properties List] ⭐ Main Work Area
  │       │     ┌──────────────────────────────────┐
  │       │     │ FILTERS                          │
  │       │     │ [Status ▾] [Score ▾] [Date ▾]    │
  │       │     │ [Church ▾] [Location ▾]          │
  │       │     ├──────────────────────────────────┤
  │       │     │ BULK ACTIONS                     │
  │       │     │ ☐ Select All                     │
  │       │     │ [Enrich Selected] [Export CSV]   │
  │       │     ├──────────────────────────────────┤
  │       │     │ PROPERTY TABLE                   │
  │       │     │ ┌─────────────────────────────┐  │
  │       │     │ │ Name │ Church │ Score │ ... │  │
  │       │     │ ├─────────────────────────────┤  │
  │       │     │ │ Oasis │ Oasis  │ 73.8  │ ... │  │
  │       │     │ │ Hope  │ Hope   │ 85.2  │ ... │  │
  │       │     │ └─────────────────────────────┘  │
  │       │     └──────────────────────────────────┘
  │       │           │
  │       │           ├─> [Select Property]
  │       │                 │
  │       │                 ├─> [Property Detail]
  │       │                       ┌────────────────────────────┐
  │       │                       │ PROPERTY INFO              │
  │       │                       │ - Address, lot size, etc   │
  │       │                       ├────────────────────────────┤
  │       │                       │ ENRICHMENT STATUS          │
  │       │                       │ ✓ Census (complete)        │
  │       │                       │ ✓ HUD (complete)           │
  │       │                       │ ✓ FEMA (complete)          │
  │       │                       │ ✓ LA County (complete)     │
  │       │                       │ ⏳ Assessment (pending)     │
  │       │                       ├────────────────────────────┤
  │       │                       │ ACTIONS                    │
  │       │                       │ [Re-enrich] [Process]      │
  │       │                       │ [Edit] [Delete]            │
  │       │                       └────────────────────────────┘
  │       │                             │
  │       │                             ├─> [Process Assessment]
  │       │                                   • AI analysis runs
  │       │                                   • Grading computed
  │       │                                   │
  │       │                                   ├─> [Review Results]
  │       │                                         │
  │       │                                         ├─> Deal Breaker?
  │       │                                         │     YES
  │       │                                         │     │
  │       │                                         │     ├─> [Mark Not Viable]
  │       │                                         │           • Add notes
  │       │                                         │           • Notify church
  │       │                                         │           • Archive
  │       │                                         │
  │       │                                         │     NO
  │       │                                         │     │
  │       │                                         │     ├─> [Generate Report]
  │       │                                         │           • PDF created
  │       │                                         │           • Email to church
  │       │                                         │           • Mark complete
  │       │
  │       ├─> [Analytics Dashboard]
  │             ┌────────────────────────────────┐
  │             │ PORTFOLIO OVERVIEW             │
  │             │ - Total properties: 156        │
  │             │ - Average score: 68.5          │
  │             │ - Deal breaker rate: 32%       │
  │             ├────────────────────────────────┤
  │             │ GEOGRAPHIC DISTRIBUTION        │
  │             │ [Interactive Map]              │
  │             │ • Heatmap by score             │
  │             │ • Cluster markers              │
  │             ├────────────────────────────────┤
  │             │ TREND CHARTS                   │
  │             │ • Assessments per month        │
  │             │ • Score distribution           │
  │             │ • Top performing regions       │
  │             └────────────────────────────────┘
  │
  └─> [Reports Archive]
        • All generated PDFs
        • Filter by date/church
        • Bulk download

END
```

### **Key Screens**

1. **Analyst Dashboard** - Queue management
2. **Properties List** - Bulk operations
3. **Property Detail** - Deep dive view
4. **Analytics Dashboard** - Portfolio insights

---

## 👔 Flow 3: Executive/Decision Maker

### **Goal:** High-level overview and approvals

```
┌─────────────────────────────────────────────────────────────────┐
│                      EXECUTIVE JOURNEY                           │
└─────────────────────────────────────────────────────────────────┘

START
  │
  ├─> [Login] (Clerk - Executive role)
  │
  ├─> [Executive Dashboard] ⭐ Strategic View
  │     ┌──────────────────────────────────────────────┐
  │     │ KEY METRICS (Current Month)                  │
  │     │ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐         │
  │     │ │  23  │ │  8   │ │ 68.5 │ │ 32%  │         │
  │     │ │Props │ │Apprv │ │ Avg  │ │Deal  │         │
  │     │ │Assess│ │ ed   │ │Score │ │Break │         │
  │     │ └──────┘ └──────┘ └──────┘ └──────┘         │
  │     ├──────────────────────────────────────────────┤
  │     │ TOP OPPORTUNITIES (Awaiting Approval)        │
  │     │ ┌────────────────────────────────────────┐   │
  │     │ │ 1. Hope Church - Score: 85.2 🟢        │   │
  │     │ │    40 units, $12.5M budget, Grade A-   │   │
  │     │ │    [View Details] [Approve] [Reject]   │   │
  │     │ ├────────────────────────────────────────┤   │
  │     │ │ 2. Grace Church - Score: 82.1 🟢       │   │
  │     │ │    55 units, $16.2M budget, Grade B+   │   │
  │     │ │    [View Details] [Approve] [Reject]   │   │
  │     │ └────────────────────────────────────────┘   │
  │     ├──────────────────────────────────────────────┤
  │     │ PIPELINE STATUS                              │
  │     │ [Progress Bar]                               │
  │     │ Submitted: 40 → Enriched: 30 → Assessed: 23 │
  │     │                                              │
  │     ├──────────────────────────────────────────────┤
  │     │ GEOGRAPHIC HEATMAP                           │
  │     │ [Map showing property clusters by score]     │
  │     └──────────────────────────────────────────────┘
  │           │
  │           ├─> [View Top Opportunity]
  │                 │
  │                 ├─> [Property Summary View]
  │                       ┌──────────────────────────┐
  │                       │ EXECUTIVE SUMMARY        │
  │                       │ - Grade: A- (85.2/100)   │
  │                       │ - Recommendation: ✓ YES  │
  │                       │ - Units: 40              │
  │                       │ - Budget: $12.5M         │
  │                       │ - ROI: 8.5%              │
  │                       ├──────────────────────────┤
  │                       │ KEY HIGHLIGHTS           │
  │                       │ ✓ Strong market demand   │
  │                       │ ✓ Excellent partnership  │
  │                       │ ⚠️ Moderate flood risk   │
  │                       ├──────────────────────────┤
  │                       │ ATTACHMENTS              │
  │                       │ [📄 Full PDF Report]     │
  │                       │ [📊 Financial Model]     │
  │                       ├──────────────────────────┤
  │                       │ DECISION                 │
  │                       │ [✓ Approve]              │
  │                       │ [✗ Reject]               │
  │                       │ [💬 Request More Info]   │
  │                       └──────────────────────────┘
  │                             │
  │                             ├─> [Approve]
  │                             │     • Status → "Approved"
  │                             │     • Notify team
  │                             │     • Move to pipeline
  │                             │
  │                             ├─> [Reject]
  │                             │     • Add rejection reason
  │                             │     • Notify church
  │                             │     • Archive
  │                             │
  │                             └─> [Request Info]
  │                                   • Add comment
  │                                   • Assign to analyst
  │                                   • Set reminder
  │
  ├─> [Portfolio Analytics]
  │     • ROI projections
  │     • Risk distribution
  │     • Market trends
  │     • Church partnerships
  │
  └─> [Reports Center]
        • Monthly summaries
        • Board presentations
        • Custom exports

END
```

### **Key Screens**

1. **Executive Dashboard** - KPIs and alerts
2. **Approval Queue** - Quick decisions
3. **Property Summary** - One-page overview
4. **Portfolio Analytics** - Strategic insights

---

## 📱 Page Wireframes

### **1. Landing Page** (Public)

```
┌────────────────────────────────────────────────────────┐
│ [Logo]              Home  About  Pricing  [Login] [→]  │
├────────────────────────────────────────────────────────┤
│                                                        │
│           Transform Church Land into                   │
│           Affordable Housing                           │
│                                                        │
│     Get AI-powered property assessments in minutes     │
│                                                        │
│              [Get Started Free →]                      │
│                                                        │
│           [🏠 Property Analysis Demo ▶]                │
│                                                        │
├────────────────────────────────────────────────────────┤
│  HOW IT WORKS                                          │
│  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐              │
│  │  1   │  │  2   │  │  3   │  │  4   │              │
│  │Submit│→ │Enrich│→ │Assess│→ │Report│              │
│  └──────┘  └──────┘  └──────┘  └──────┘              │
│                                                        │
├────────────────────────────────────────────────────────┤
│  TRUSTED BY                                            │
│  [Church Logo] [Church Logo] [Church Logo]             │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### **2. Dashboard** (Authenticated)

```
┌────────────────────────────────────────────────────────┐
│ [Logo]  Dashboard  Properties  Assessments    [User ▾] │
├─────┬──────────────────────────────────────────────────┤
│     │  DASHBOARD                                       │
│ 🏠  │  ┌────────────────────────────────────────┐     │
│Props│  │ Welcome back, Adam! 👋                 │     │
│     │  │ You have 3 properties pending review   │     │
│ 🏛️  │  └────────────────────────────────────────┘     │
│Chur │                                                  │
│ches │  QUICK STATS                                     │
│     │  ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐       │
│ 📊  │  │   5   │ │   3   │ │  2    │ │ 85.2  │       │
│Asmts│  │ Props │ │Comple │ │Pendin │ │  Avg  │       │
│     │  │       │ │  ted  │ │  g    │ │ Score │       │
│ 📄  │  └───────┘ └───────┘ └───────┘ └───────┘       │
│Rpts │                                                  │
│     │  RECENT ACTIVITY                                 │
│ ⚙️  │  ┌────────────────────────────────────────┐     │
│Set  │  │ ✓ Hope Church assessed - 85.2/100      │     │
│tings│  │ ⏳ Grace Church enrichment in progress │     │
│     │  │ 📄 Oasis Church report downloaded      │     │
│ ❓  │  └────────────────────────────────────────┘     │
│Help │                                                  │
│     │  [+ Add Property]                                │
│     │                                                  │
└─────┴──────────────────────────────────────────────────┘
```

### **3. Property Detail Page**

```
┌────────────────────────────────────────────────────────┐
│ [Logo]  Dashboard  Properties  Assessments    [User ▾] │
├────────────────────────────────────────────────────────┤
│ ← Back to Properties                                   │
│                                                        │
│ Oasis Church Property                                  │
│ 634 Normandie Ave, Los Angeles, CA 90005              │
│                                                        │
│ [Edit] [Delete] [Request Assessment]                   │
│                                                        │
├────────────────────────────────────────────────────────┤
│ TABS: [Overview] [Enrichment] [Assessment] [History]   │
├────────────────────────────────────────────────────────┤
│ PROPERTY DETAILS                                       │
│ ┌──────────────────────────────────────────────┐       │
│ │ Address:     634 Normandie Ave               │       │
│ │ City:        Los Angeles, CA 90005           │       │
│ │ Lot Size:    25,045 sq ft (0.57 acres)      │       │
│ │ Zoning:      UNKNOWN                         │       │
│ │ Church:      Oasis Church                    │       │
│ │ Created:     Jan 5, 2025                     │       │
│ └──────────────────────────────────────────────┘       │
│                                                        │
│ ENRICHMENT STATUS                                      │
│ ┌──────────────────────────────────────────────┐       │
│ │ ✅ Census Bureau        Complete             │       │
│ │ ✅ HUD Fair Market Rent Complete             │       │
│ │ ✅ FEMA Flood Data      Complete             │       │
│ │ ✅ LA County Assessor   Complete             │       │
│ │ ⏳ AI Assessment        In Progress...       │       │
│ └──────────────────────────────────────────────┘       │
│                                                        │
│ [View Full Enrichment Data →]                          │
│                                                        │
└────────────────────────────────────────────────────────┘
```

### **4. Assessment Results Page** ⭐ MOST IMPORTANT

```
┌────────────────────────────────────────────────────────┐
│ [Logo]  Dashboard  Properties  Assessments    [User ▾] │
├────────────────────────────────────────────────────────┤
│ ← Back to Properties                                   │
│                                                        │
│ ASSESSMENT RESULTS                                     │
│ Oasis Church Property - 634 Normandie Ave              │
│                                                        │
│ ┌────────────────────────────────────────────────┐     │
│ │         OVERALL GRADE: B (73.8/100)            │     │
│ │                                                │     │
│ │  ✗ NOT RECOMMENDED - DEAL BREAKER PRESENT      │     │
│ │                                                │     │
│ │  Only 4 units feasible (requires 40+)          │     │
│ └────────────────────────────────────────────────┘     │
│                                                        │
│ SCORE BREAKDOWN                                        │
│ ┌──────────────────────────────────────────────┐       │
│ │ Financial Viability    50/100  ✗ FAIL        │       │
│ │ [━━━━━━━━━━░░░░░░░░░░]                       │       │
│ │                                              │       │
│ │ Market Demand          97/100  ✓ PASS        │       │
│ │ [━━━━━━━━━━━━━━━━━━━░]                       │       │
│ │                                              │       │
│ │ Location Quality       75/100  ✓ PASS        │       │
│ │ [━━━━━━━━━━━━━━░░░░░░]                       │       │
│ │                                              │       │
│ │ Partnership Alignment  100/100 ✓ PASS        │       │
│ │ [━━━━━━━━━━━━━━━━━━━━]                       │       │
│ │                                              │       │
│ │ Risk Assessment        39/100  ✗ FAIL        │       │
│ │ [━━━━━━░░░░░░░░░░░░░░]                       │       │
│ └──────────────────────────────────────────────┘       │
│                                                        │
│ KEY DATA                                               │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│ │ 💰 FINANCIAL │ │ 📈 MARKET    │ │ 📍 LOCATION  │    │
│ │ 4 units      │ │ $2,601 FMR   │ │ 0.57 acres   │    │
│ │ $425K/unit   │ │ High demand  │ │ Zone A flood │    │
│ │ 5.2% ROI     │ │ 21% poverty  │ │ Urban core   │    │
│ └──────────────┘ └──────────────┘ └──────────────┘    │
│                                                        │
│ [📄 Download Full Report] [📧 Share] [💬 Get Help]     │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## 🏗️ Component Hierarchy

### **Dashboard Page Structure**

```
<DashboardPage>
  ├─ <Header>
  │    ├─ <Logo />
  │    ├─ <Navigation />
  │    └─ <UserMenu />
  │
  ├─ <Sidebar>
  │    ├─ <NavItem icon="home">Dashboard</NavItem>
  │    ├─ <NavItem icon="building">Churches</NavItem>
  │    ├─ <NavItem icon="map">Properties</NavItem>
  │    └─ <NavItem icon="chart">Assessments</NavItem>
  │
  └─ <MainContent>
       ├─ <WelcomeCard user={user} />
       │
       ├─ <StatsGrid>
       │    ├─ <StatCard title="Properties" value={5} />
       │    ├─ <StatCard title="Completed" value={3} />
       │    ├─ <StatCard title="Pending" value={2} />
       │    └─ <StatCard title="Avg Score" value={85.2} />
       │
       ├─ <RecentActivity>
       │    ├─ <ActivityItem />
       │    ├─ <ActivityItem />
       │    └─ <ActivityItem />
       │
       └─ <QuickActions>
            └─ <Button>Add Property</Button>
```

### **Assessment Page Structure**

```
<AssessmentPage id={assessmentId}>
  ├─ <Header />
  │
  ├─ <Breadcrumbs>
  │    └─ Properties > Oasis Church > Assessment
  │
  ├─ <GradeCard>
  │    ├─ <GradeBadge grade="B" score={73.8} />
  │    └─ <RecommendationAlert type="deal-breaker" />
  │
  ├─ <ScoreBreakdown>
  │    ├─ <ScoreBar category="financial" score={50} />
  │    ├─ <ScoreBar category="market" score={97} />
  │    ├─ <ScoreBar category="location" score={75} />
  │    ├─ <ScoreBar category="partnership" score={100} />
  │    └─ <ScoreBar category="risk" score={39} />
  │
  ├─ <KeyDataGrid>
  │    ├─ <DataCard type="financial" />
  │    ├─ <DataCard type="market" />
  │    └─ <DataCard type="location" />
  │
  └─ <ActionBar>
       ├─ <Button>Download PDF</Button>
       ├─ <Button>Share</Button>
       └─ <Button>Get Help</Button>
```

---

## 🎨 Design Tokens

```typescript
// Design system values used across all pages

const theme = {
  colors: {
    primary: '#2c5aa0',
    success: '#4caf50',
    warning: '#fbc02d',
    error: '#f44336',
    neutral: '#757575',
  },

  spacing: {
    xs: '0.5rem', // 8px
    sm: '1rem', // 16px
    md: '1.5rem', // 24px
    lg: '2rem', // 32px
    xl: '3rem', // 48px
  },

  borderRadius: {
    sm: '0.25rem', // 4px
    md: '0.5rem', // 8px
    lg: '1rem', // 16px
  },

  shadows: {
    sm: '0 1px 2px rgba(0,0,0,0.05)',
    md: '0 4px 6px rgba(0,0,0,0.1)',
    lg: '0 10px 15px rgba(0,0,0,0.15)',
  },
};
```

---

## ✅ Next Steps

1. **Review these flows** with your team
2. **Create high-fidelity mockups** in Figma
3. **Start with MVP pages**:
   - Landing page
   - Dashboard
   - Property form
   - Assessment results
4. **Build incrementally** following the roadmap

---

**Ready to design?** Share this with your designer/team! 🎨
