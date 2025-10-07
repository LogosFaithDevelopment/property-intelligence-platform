# Property Intelligence Platform

> AI-powered platform connecting churches with affordable housing developers through intelligent property evaluation and investment-grade reporting.

## 🚀 Overview

The Property Intelligence Platform automates the evaluation of faith-based properties for affordable housing development, reducing analysis time from weeks to minutes and costs from $10,000+ to under $100 per property.

### Key Features

- **30-minute Church Onboarding** - Simple property assessment flow
- **AI-Powered Analysis** - Intelligent scoring using 15+ data sources
- **Investment-Grade Reports** - Professional PDF reports in 2-5 minutes
- **Progressive API Integration** - Start free, upgrade to premium data sources
- **Real-time Dashboard** - Unified interface for all stakeholders

## 🏗 Architecture

### Backend Stack

- **FastAPI** - Async-first Python framework
- **SQLAlchemy 2.0 + Alembic** - Async ORM with migrations
- **PostgreSQL + PostGIS** - Geospatial database
- **Redis** - Caching and session storage
- **Arq** - Async task queue
- **Pydantic V2** - Data validation and serialization

### Frontend Stack

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS + shadcn/ui** - Modern UI components
- **TanStack Query** - Server state management
- **Clerk** - Authentication and user management

### Third-Party Services

- **Clerk** - Authentication ($25/month)
- **Retool** - Admin dashboard ($300/month)
- **Railway** - Backend hosting ($20/month)
- **Vercel** - Frontend hosting (free tier)
- **Neon** - Managed PostgreSQL ($29/month)

## 📊 API Strategy

### Phase 1: Free Tier (MVP)

- **US Census API** - Demographics and housing data
- **HUD Exchange** - Affordable housing programs
- **FEMA API** - Flood risk assessment
- **OpenStreetMap** - Geocoding and mapping
- **OpenAI GPT-3.5** - Basic report generation

**Monthly Cost: $50-100**

### Phase 2: Professional Tier

- **ATTOM Data API** - Comprehensive property intelligence ($1,500/month)
- **Google Maps Platform** - Advanced mapping and places ($200/month)
- **Rentberry API** - Rental market analysis ($49/month)
- **OpenAI GPT-4** - Advanced report generation ($200/month)

**Monthly Cost: $2,500**

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### 1. Clone and Setup

```bash
git clone <repository-url>
cd property-intelligence-platform
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Database setup
alembic upgrade head

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Backend
DATABASE_URL=postgresql://user:password@localhost/property_intel
REDIS_URL=redis://localhost:6379
OPENAI_API_KEY=your_openai_key
CLERK_SECRET_KEY=your_clerk_secret

# Frontend
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=your_clerk_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🏢 Project Structure

```
property-intelligence-platform/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── main.py            # FastAPI app initialization
│   │   ├── config.py          # Pydantic settings
│   │   ├── database.py        # SQLAlchemy setup
│   │   ├── models/            # Database models (10-15 tables)
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── routers/           # API endpoints
│   │   ├── services/          # Business logic
│   │   ├── api_providers/     # External API integrations
│   │   └── tasks/             # Background tasks
│   └── requirements.txt
│
├── frontend/                   # Next.js Frontend
│   ├── app/
│   │   ├── onboarding/        # Church signup flow
│   │   ├── assessment/        # Property assessment
│   │   ├── dashboard/         # Unified dashboard
│   │   └── reports/           # Report viewing
│   └── components/            # React components
│
└── infrastructure/
    ├── docker-compose.yml     # Local development
    └── railway.toml           # Production deployment
```

## 📈 Development Phases

### Phase 1: MVP Foundation (Weeks 1-4)

- [ ] FastAPI backend with core models
- [ ] Clerk authentication integration
- [ ] Free API integrations (Census, HUD, FEMA)
- [ ] Basic church onboarding
- [ ] Simple property assessment form
- [ ] Rule-based scoring algorithm

### Phase 2: Professional Features (Weeks 5-8)

- [ ] Next.js frontend with shadcn/ui
- [ ] Unified dashboard for all users
- [ ] AI report generation with GPT-3.5
- [ ] PDF report viewer and download
- [ ] ATTOM Data trial integration
- [ ] Production deployment

### Phase 3: Scale & Intelligence (Weeks 9-12)

- [ ] Advanced AI scoring with historical data
- [ ] Premium API integrations (ATTOM, Google Maps)
- [ ] Retool admin dashboard
- [ ] Performance optimization
- [ ] Multi-market support

## 🔧 API Documentation

Once the backend is running, visit:

- **Interactive Docs:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

FastAPI automatically generates OpenAPI documentation for all endpoints.

## 🚀 Deployment

### Development

```bash
docker-compose up -d
```

### Production

The platform is configured for easy deployment on:

- **Backend:** Railway.app (connects to GitHub, auto-deploys)
- **Frontend:** Vercel (automatic Next.js deployment)
- **Database:** Neon PostgreSQL (managed service)

## 📊 Performance Metrics

### Target KPIs

- **Processing Speed:** 2-5 minutes per property analysis
- **Data Accuracy:** 60-70% (free APIs) → 85-90% (premium APIs)
- **System Uptime:** 99.9% availability
- **Scale Capacity:** 5,000+ properties/month

### Business Impact

- **Cost Reduction:** 95% vs manual analysis ($10,000 → $50-100)
- **Time Savings:** 95% vs traditional methods (2 weeks → 2 minutes)
- **ROI:** Break-even at 5-10 successful partnerships/quarter

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is proprietary software. All rights reserved.

## 🆘 Support

For technical support or questions:

- **Documentation:** Check the `/docs` folder
- **API Issues:** Check FastAPI logs and `/docs` endpoint
- **Frontend Issues:** Check browser console and Next.js logs

## 🎯 Roadmap

### Q4 2025

- ✅ MVP launch with free APIs
- ✅ 20+ churches onboarded
- ✅ 5+ qualified investment opportunities

### Q1 2026

- 📈 Professional API tier activation
- 📈 200+ churches active
- 📈 Investment-grade reporting
- 📈 Mobile-responsive optimization

### Q2 2026

- 🚀 Multi-market expansion
- 🚀 Advanced ML scoring models
- 🚀 Enterprise partnerships
- 🚀 1,000+ churches across multiple states

---

**Built with ❤️ for affordable housing development**
