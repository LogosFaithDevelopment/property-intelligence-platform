# Property Intelligence Platform

> AI-powered platform connecting churches with affordable housing developers through intelligent property evaluation and investment-grade reporting.

**Production Site:** [logos.lotspecs.com](https://logos.lotspecs.com)  
**Status:** Production Ready - November 13th 2025  
**Client:** Logos Faith Development

---

## Overview

The Property Intelligence Platform automates the evaluation of faith-based properties for affordable housing development, reducing analysis time from weeks to minutes and costs from $10,000+ to under $100 per property.

### Key Features

- **AI-Powered Property Assessment** - Analyzes API's + data sources in under 5 minutes
- **Investment-Grade Reports** - Professional PDF reports with IRR projections
- **3/4/5-Story Scenario Analysis** - Financial modeling for different development options
- **HUD Fair Market Rent Integration** - Location-based rent projections
- **Admin Portal** - Property Applications management and approval workflow
- **Clerk Authentication** - Secure user management with role-based access

### Business Impact

- **Time Savings:** 95% reduction (2 weeks → 5 minutes)
- **Cost Reduction:** 99% savings ($10,000 → $100 per assessment)
- **Accuracy:** 85-90% with premium data sources
- **Scale:** Process 1,000+ properties/month

---

## Production Architecture

### Deployment Stack

- **Infrastructure:** AWS ECS Fargate (us-east-1)
- **Frontend:** Next.js 15.5.4 standalone server (ECS task on port 3000)
- **Backend:** FastAPI + Gunicorn/Uvicorn (ECS task on port 8000)
- **Database:** PostgreSQL 15 + PostGIS (AWS RDS)
- **Load Balancer:** Application Load Balancer with health checks
- **DNS/CDN:** CloudFlare (logos.lotspecs.com)
- **Secrets:** AWS Secrets Manager
- **Container Registry:** Amazon ECR

### Application Stack

#### Backend

- **FastAPI** - Async Python framework with Pydantic V2
- **SQLAlchemy 2.0 + Alembic** - Database ORM with migrations
- **PostgreSQL + PostGIS** - Geospatial database on AWS RDS
- **ReportLab** - PDF report generation
- **NumPy Financial** - IRR and financial calculations

#### Frontend

- **Next.js 15** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS + shadcn/ui** - Modern component library
- **TanStack Query** - Server state management
- **Clerk** - Production authentication

### Third-Party APIs

- **Clerk** - Production authentication with user locking
- **OpenAI GPT-4** - Advanced report generation and property analysis
- **ATTOM Data API** - Comprehensive property intelligence
- **SmartyStreets** - Address validation and property data
- **US Census API** - Demographics and housing statistics
- **HUD Exchange API** - Fair Market Rent data by county

---

## Quick Start (Local Development)

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ with PostGIS extension
- Docker & Docker Compose (recommended)

### Option 1: Docker Compose (Recommended)

```bash
# Clone repository
git clone https://github.com/siliconbeachdevelopers/property-intelligence-platform.git
cd property-intelligence-platform

# Copy environment files
cp .env.example .env

# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head
```

**Services will be available at:**

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option 2: Manual Setup

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Environment Variables

See `.env.example` and `.env.production.local.example` for required variables:

**Backend** (`.env`):

```env
DATABASE_URL=postgresql://user:password@localhost:5432/property_intel
OPENAI_API_KEY=sk-...
CLERK_SECRET_KEY=sk_live_...
ATTOM_API_KEY=...
SMARTY_AUTH_ID=...
SMARTY_AUTH_TOKEN=...
```

**Frontend** (`.env.local`):

```env
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Project Structure

```
property-intelligence-platform/
├── backend/                           # FastAPI Backend
│   ├── app/
│   │   ├── main.py                   # FastAPI application entry point
│   │   ├── config.py                 # Pydantic settings management
│   │   ├── database.py               # SQLAlchemy async engine
│   │   ├── models/                   # Database models
│   │   │   ├── church.py            # Church entity
│   │   │   ├── property.py          # Property entity
│   │   │   └── assessment.py        # AI assessment results
│   │   ├── schemas/                  # Pydantic validation schemas
│   │   ├── routers/                  # API endpoints
│   │   │   ├── admin.py             # Admin portal endpoints
│   │   │   ├── churches.py          # Church CRUD
│   │   │   ├── properties.py        # Property management
│   │   │   └── assessments.py       # Assessment triggers
│   │   ├── services/                 # Business logic
│   │   │   ├── ai_assessment.py     # Core financial calculations
│   │   │   ├── report_generator_v3.py # PDF generation (active)
│   │   │   └── address_validator.py  # SmartyStreets integration
│   │   ├── api_providers/            # External API clients
│   │   │   ├── attom_client.py      # ATTOM Data API
│   │   │   ├── hud_client.py        # HUD Fair Market Rent
│   │   │   └── census_client.py     # US Census data
│   │   └── middleware/               # Request/response middleware
│   ├── alembic/                      # Database migrations
│   ├── scripts/                      # Utility scripts
│   │   ├── admin/                   # Admin operations
│   │   └── utilities/               # One-off utilities
│   ├── static/                       # Static assets (logos)
│   ├── Dockerfile                    # Production container
│   └── requirements.txt              # Python dependencies
│
├── frontend/                          # Next.js Frontend
│   ├── src/
│   │   ├── app/                      # Next.js App Router
│   │   │   ├── (public)/            # Public pages
│   │   │   │   ├── page.tsx         # Landing page
│   │   │   │   └── about/           # About page
│   │   │   ├── (auth)/              # Auth pages
│   │   │   │   ├── sign-in/         # Clerk sign in
│   │   │   │   └── sign-up/         # Clerk sign up
│   │   │   ├── onboarding/          # Church onboarding flow
│   │   │   ├── assessment/          # Property assessment
│   │   │   ├── dashboard/           # User dashboard
│   │   │   ├── properties/          # Property list/detail
│   │   │   └── admin/               # Admin portal (5 pages)
│   │   │       ├── page.tsx         # Admin dashboard
│   │   │       ├── churches/        # Church management
│   │   │       ├── properties/      # Property approval
│   │   │       ├── assessments/     # Assessment visualization
│   │   │       └── users/           # User management
│   │   ├── components/               # Reusable React components
│   │   │   ├── ui/                  # shadcn/ui components
│   │   │   └── features/            # Feature-specific components
│   │   └── lib/                      # Utilities and helpers
│   ├── public/                       # Static assets
│   ├── Dockerfile                    # Production container
│   ├── next.config.ts               # Next.js configuration
│   ├── package.json                 # Node dependencies
│   └── tsconfig.json                # TypeScript config
│
├── docs/                              # Documentation
│   ├── guides/                       # Operational guides (62 files)
│   │   ├── DEPLOYMENT_GUIDE.md      # AWS deployment
│   │   ├── IRR_CALCULATION_METHODOLOGY_2025.md # Financial model
│   │   └── AI_ASSESSMENT_EXPLAINED.md # Assessment logic
│   ├── completed/                    # Development history (51 files)
│   └── architecture/                 # Architecture docs
│
├── docker-compose.yml                # Local development
├── docker-compose.prod.yml           # Production testing
├── .env.example                      # Environment template
└── README.md                         # This file
```

---

## Core Features Explained

### AI Assessment Engine

The platform's core is a sophisticated financial modeling system that evaluates properties across multiple development scenarios:

**Financial Calculations:**

- **3/4/5-Story Analysis** - Evaluates low-rise, mid-rise, and high-rise development options
- **IRR Projections** - 7-year Internal Rate of Return calculations
- **Unit Mix Optimization** - 10% studios, 80% 1-bedroom, 10% 2-bedroom - optional to change for different score
- **Tiered Construction Costs** - $275K (3-story), $325K (4-story), $415K (5-story) per unit
- **HUD FMR Integration** - Location-specific rent projections by county
- **Operating Expense Modeling** - 40% OpEx ratio with detailed breakdowns

**Data Sources (15+ APIs):**

- ATTOM Data: Property characteristics, zoning, lot size, market value
- SmartyStreets: Address validation, geocoding, property metadata
- US Census: Demographics, income levels, population density
- HUD Exchange: Fair Market Rent, housing assistance programs
- OpenAI GPT-4: Natural language report generation, insights

**Scoring Algorithm:**

- Lot size, zoning compatibility, location quality
- Financial viability (IRR > 8% threshold)
- Community impact metrics
- Risk factors (seismic, flood, environmental)

### Report Generation (V3)

Professional PDF reports generated in under 5 minutes:

- Executive summary with development recommendation
- 3/4/5-story financial comparison tables
- Detailed IRR and cash flow projections
- Market analysis with Census demographics
- Zoning and regulatory compliance
- High-resolution satellite imagery
- Custom branding with Logos Faith Development logo

### Admin Portal

Comprehensive property management interface:

- **Churches:** View all registered organizations
- **Properties:** Approve/reject submissions with notes
- **Assessments:** Visualize AI scores with interactive charts
- **Users:** Manage access via Clerk integration
- **Bulk Operations:** Export data, trigger reassessments

---

## Production Deployment

The platform is deployed on AWS ECS Fargate with the following architecture:

### Infrastructure Components

```
CloudFlare (logos.lotspecs.com)
    ↓
Application Load Balancer (ALB)
    ↓
    ├── Frontend ECS Service (port 3000)
    │   └── Task: Next.js standalone (309MB image)
    │
    ├── Backend ECS Service (port 8000)
    │   └── Task: FastAPI + Gunicorn (1.11GB image)
    │
    └── Health Checks
        ├── Frontend: GET /
        ├── Backend: GET /health
        └── Target Group: Healthy thresholds

RDS PostgreSQL 15 (PostGIS enabled)
AWS Secrets Manager (API keys, database credentials)
Amazon ECR (Docker image registry)
```

### Deployment Process

**See:** `README.prod.md` for complete deployment guide

**Quick Deploy:**

```bash
# 1. Build and push Docker images
docker build -t frontend:latest ./frontend
docker build -t backend:latest ./backend
docker tag frontend:latest <ECR_URI>/frontend:latest
docker tag backend:latest <ECR_URI>/backend:latest
docker push <ECR_URI>/frontend:latest
docker push <ECR_URI>/backend:latest

# 2. Update ECS services
aws ecs update-service --cluster property-platform-cluster \
  --service frontend-service --force-new-deployment

aws ecs update-service --cluster property-platform-cluster \
  --service backend-service --force-new-deployment

# 3. Verify health
aws elbv2 describe-target-health --target-group-arn <TG_ARN>
```

### Environment Management

**Production Secrets (AWS Secrets Manager):**

- `prod/property-platform/database` - RDS credentials
- `prod/property-platform/clerk` - Auth keys
- `prod/property-platform/apis` - ATTOM, OpenAI, SmartyStreets keys

**ECS Task Definitions:**

- Reference secrets via `secretsmanager:` ARN
- Environment variables injected at runtime
- No secrets in source code or Docker images

---

## API Documentation

**Production API:** [https://logos.lotspecs.com/api](https://logos.lotspecs.com/api)

**Interactive Docs:**

- **Swagger UI:** https://logos.lotspecs.com/api/docs
- **ReDoc:** https://logos.lotspecs.com/api/redoc

**Local Development:**

- http://localhost:8000/docs
- http://localhost:8000/redoc

### Key Endpoints

```
POST   /api/churches                  # Create church
GET    /api/churches/{id}             # Get church details
POST   /api/properties                # Submit property
GET    /api/properties/{id}           # Get property
POST   /api/assessments               # Trigger AI assessment
GET    /api/assessments/{id}          # Get assessment results
GET    /api/assessments/{id}/pdf      # Download PDF report

# Admin endpoints (requires admin role)
GET    /api/admin/churches            # List all churches
GET    /api/admin/properties          # List all properties
PUT    /api/admin/properties/{id}     # Approve/reject property
GET    /api/admin/assessments         # Assessment dashboard data
```

---

## 🔧 Database Schema

**Core Tables:**

- `churches` - Faith-based organizations
- `properties` - Submitted properties for evaluation
- `assessments` - AI-generated analysis results
- `users` - Clerk-synced user accounts (via webhooks)

**PostGIS Extensions:**

- Geospatial indexing for location-based queries
- Distance calculations for market analysis
- Polygon storage for lot boundaries

**Migrations:**

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one version
alembic downgrade -1
```

---

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests

```bash
cd frontend
npm run test
npm run test:e2e  # Playwright E2E tests
```

### Local Production Testing

Test production Docker builds locally:

```bash
docker-compose -f docker-compose.prod.yml up
```

This uses the same Dockerfiles as production deployment.

---

## Security

### Authentication

- **Clerk** - Production-grade auth with MFA support
- **JWT Tokens** - Secure session management
- **Role-Based Access** - Admin vs standard user permissions

### API Security

- **CORS** - Configured for logos.lotspecs.com origin
- **Rate Limiting** - Prevent API abuse
- **Input Validation** - Pydantic schemas on all endpoints
- **SQL Injection Protection** - SQLAlchemy ORM parameterization

### Data Privacy

- **AWS Secrets Manager** - Encrypted credential storage
- **Environment Isolation** - No secrets in code/images
- **HTTPS Only** - CloudFlare SSL termination
- **Database Encryption** - RDS encryption at rest

---

## Monitoring & Operations

### Health Checks

**Frontend Health:**

```bash
curl https://logos.lotspecs.com/
# Should return: 200 OK with HTML
```

**Backend Health:**

```bash
curl https://logos.lotspecs.com/api/health
# Should return: {"status": "healthy", "database": "connected"}
```

### ECS Operations

**Pause Site (Maintenance Mode):**

```bash
aws ecs update-service --cluster property-platform-cluster \
  --service frontend-service --desired-count 0

aws ecs update-service --cluster property-platform-cluster \
  --service backend-service --desired-count 0
```

**Resume Site:**

```bash
aws ecs update-service --cluster property-platform-cluster \
  --service frontend-service --desired-count 1

aws ecs update-service --cluster property-platform-cluster \
  --service backend-service --desired-count 1
```

**View Logs:**

```bash
aws logs tail /ecs/frontend-task --follow
aws logs tail /ecs/backend-task --follow
```

### User Management

**Lock User (Prevent Access):**

1. Go to Clerk Dashboard: https://dashboard.clerk.com
2. Navigate to Users → [Select User]
3. Click "Lock User" button
4. User will be immediately signed out across all sessions

---

## Performance & Scale

### Current Production Metrics

- **Processing Speed:** 3-5 minutes per complete property analysis
- **Data Accuracy:** 85-90% with premium API integrations
- **System Uptime:** 99.9% availability (AWS ECS + RDS)
- **Response Time:** <500ms average API response
- **Concurrent Users:** Supports 100+ simultaneous assessments

### Business Impact

- **Cost Reduction:** 99% vs manual analysis ($10,000 → $100 per property)
- **Time Savings:** 95% reduction (2 weeks → 5 minutes)
- **Scale Capacity:** Process 1,000+ properties/month
- **ROI:** Immediate value for affordable housing developers

---

## Maintenance & Troubleshooting

### Common Issues

**Backend won't start:**

```bash
# Check database connection
docker-compose exec backend python -c "from app.database import engine; print(engine)"

# Verify migrations
docker-compose exec backend alembic current
```

**Frontend build errors:**

```bash
# Clear Next.js cache
rm -rf frontend/.next
cd frontend && npm run build
```

**Database migration conflicts:**

```bash
# Reset to specific revision
alembic downgrade <revision_id>
alembic upgrade head
```

**API key issues:**

```bash
# Verify environment variables are loaded
docker-compose exec backend python -c "from app.config import settings; print(settings.OPENAI_API_KEY[:10])"
```

### Useful Scripts

**Check assessment status:**

```bash
cd backend
python scripts/utilities/check_assessment_status.py <assessment_id>
```

**Generate PDF manually:**

```bash
cd backend
python scripts/utilities/generate_assessment_pdf.py <assessment_id>
```

**Database backup:**

```bash
# Local
docker-compose exec postgres pg_dump -U user property_intel > backup.sql

# Production (RDS)
pg_dump -h <rds-endpoint> -U <user> property_intel > prod_backup.sql
```

---

## � Documentation

### Key Documentation Files

- **`README.prod.md`** - Complete AWS deployment guide (1,124 lines)
- **`docs/guides/DEPLOYMENT_GUIDE.md`** - Step-by-step deployment
- **`docs/guides/IRR_CALCULATION_METHODOLOGY_2025.md`** - Financial model explanation
- **`docs/guides/AI_ASSESSMENT_EXPLAINED.md`** - Assessment algorithm details
- **`docs/AWS_RDS_SETUP.md`** - Database configuration
- **`docs/CLERK_PRODUCTION_SETUP.md`** - Authentication setup

### For Developers

- **`/docs/guides/`** - 62 operational guides
- **`/docs/architecture/`** - System architecture documentation
- **`backend/app/`** - Well-commented source code
- **API Docs:** https://logos.lotspecs.com/api/docs

---

## Future Enhancements (V2 Roadmap)

### Machine Learning Integration

- **Supervised Learning** - Train on historical approval decisions
- **XGBoost/LightGBM** - Improve scoring accuracy to 95%+
- **SHAP Explainability** - Transparent feature importance
- **Automated Retraining** - Monthly model updates

### Platform Expansion

- **Mobile App** - iOS/Android native applications
- **API Webhooks** - Real-time notifications for status changes
- **Bulk Upload** - CSV import for multiple properties
- **Integration APIs** - Connect with CRM systems

### Advanced Analytics

- **Historical Trend Analysis** - Market appreciation projections
- **Comparative Market Analysis** - Similar properties benchmarking
- **Risk Scoring** - Enhanced environmental and regulatory risk models
- **Investment Portfolio Management** - Multi-property tracking

---

## Contributing

This is proprietary software owned by Logos Faith Development.  
Developed by Silicon Beach Developers.

**For authorized developers:**

1. Create feature branch from `main`

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make changes and test thoroughly

   ```bash
   # Backend tests
   cd backend && pytest tests/ -v

   # Frontend tests
   cd frontend && npm run test
   ```

3. Commit with descriptive messages

   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

4. Push and create Pull Request
   ```bash
   git push origin feature/your-feature-name
   ```

**Coding Standards:**

- Python: Follow PEP 8, use type hints
- TypeScript: Use strict mode, proper interfaces
- Commits: Follow conventional commits (feat, fix, docs, etc.)
- Documentation: Update README and relevant docs

---

## License

This project is proprietary software owned by Logos Faith Development.  
All rights reserved. Unauthorized copying, modification, or distribution is prohibited.

**Copyright © 2025 Logos Faith Development**  
**Developed by Silicon Beach Developers**

---

## Support & Contact

### Technical Support

**For deployment issues:**

- Check `README.prod.md` deployment guide
- Review AWS CloudWatch logs
- Verify AWS Secrets Manager configuration

**For development questions:**

- Reference `/docs/guides/` documentation
- Check API docs at `/api/docs`
- Review code comments in `backend/app/`

**For emergency production issues:**

- ECS health check failures → Check CloudWatch logs
- Database connectivity → Verify RDS security groups
- API errors → Check AWS Secrets Manager keys
- User access issues → Manage via Clerk Dashboard

### Key Resources

- **Production Site:** https://logos.lotspecs.com
- **API Documentation:** https://logos.lotspecs.com/api/docs
- **Clerk Dashboard:** https://dashboard.clerk.com
- **AWS Console:** https://console.aws.amazon.com/ecs

---


