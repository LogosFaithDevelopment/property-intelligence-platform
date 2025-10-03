#!/bin/bash

# Property Intelligence Platform - Quick Start Script
# This script helps you get the backend running quickly

echo "🚀 Property Intelligence Platform - Backend Setup"
echo "=================================================="
echo ""

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not activated!"
    echo "Run: source venv/bin/activate"
    exit 1
fi

echo "✅ Virtual environment: Active"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    cp ../.env.example .env
    echo "✅ .env created - Please edit with your API keys"
    exit 1
fi

echo "✅ Environment file: Found"
echo ""

# Check database connection
echo "🔍 Checking dependencies..."
python -c "import fastapi, sqlalchemy, pydantic" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Core dependencies: Installed"
else
    echo "⚠️  Dependencies missing!"
    echo "Run: pip install -r requirements.txt"
    exit 1
fi

echo ""
echo "📊 Configuration Status:"
python -c "
from app.config import get_settings
s = get_settings()
print(f'  Environment: {s.environment}')
print(f'  Has Professional APIs: {s.has_professional_apis}')
print(f'  OpenAI Configured: {bool(s.openai_api_key and len(s.openai_api_key) > 10)}')
"

echo ""
echo "🎯 Next Steps:"
echo ""
echo "1. Make sure PostgreSQL is running:"
echo "   docker-compose up -d postgres"
echo ""
echo "2. Make sure Redis is running:"
echo "   docker-compose up -d redis"
echo ""
echo "3. Start the FastAPI server:"
echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "4. Open API docs:"
echo "   http://localhost:8000/docs"
echo ""
echo "=================================================="
