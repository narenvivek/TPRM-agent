# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TPRM-agent is a Third-Party Risk Management (TPRM) system that helps organizations assess and manage vendor risks. The application consists of a FastAPI backend and a Next.js frontend, with Airtable as the data store and Google Gemini AI for document analysis.

## Architecture

### Backend (FastAPI)
- **Location**: `./backend/`
- **Entry point**: `backend/app/main.py`
- **Framework**: FastAPI with async/await support
- **Dependencies**: FastAPI, uvicorn, pyairtable, pydantic, google-generativeai, python-dotenv, httpx

**Key Components**:
- `app/main.py` - FastAPI application with CORS middleware, dependency injection for services, and API endpoints
- `app/models.py` - Pydantic models for request/response validation (Vendor, VendorCreate, AnalysisRequest, AnalysisResult)
- `app/services/airtable_service.py` - Airtable integration with fallback to mock data when credentials are unavailable
- `app/services/ai_service.py` - Google Gemini AI integration for risk analysis with mock fallback

**API Endpoints**:
- `GET /` - Health check
- `GET /health` - Detailed health status
- `GET /vendors` - List all vendors
- `POST /vendors` - Create new vendor
- `POST /analysis` - Analyze vendor documents using AI

### Frontend (Next.js)
- **Location**: `./frontend/`
- **Framework**: Next.js 16 with App Router and React 19
- **Styling**: Tailwind CSS v4 with custom dark theme
- **UI Components**: Custom components in `src/components/ui/` using Radix UI primitives

**Key Pages**:
- `src/app/page.tsx` - Dashboard showing vendor list, risk metrics, and search
- `src/app/vendors/new/page.tsx` - Vendor onboarding form
- `src/app/vendors/[id]/page.tsx` - Vendor details with AI analysis capabilities

**Styling Pattern**: Dark theme with gradient accents, using Tailwind classes and custom colors (`bg-[#0f172a]`, blue-violet gradients)

## Development Commands

### Backend
```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run development server (default port 8000)
uvicorn app.main:app --reload --host 0.0.0.0

# Run tests
pytest test_api.py
```

### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Run development server (default port 3000)
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linter
npm run lint
```

## Environment Configuration

### Backend (.env in backend/)
Required environment variables:
- `AIRTABLE_API_KEY` - Personal Access Token from Airtable (requires scopes: data.records:read, data.records:write, schema.bases:read)
- `AIRTABLE_BASE_ID` - Airtable Base ID (starts with 'app')
- `GEMINI_API_KEY` - Google Gemini API key from AI Studio

**Note**: Services gracefully degrade to mock mode if credentials are missing.

### Frontend
- `NEXT_PUBLIC_API_URL` - Backend API URL (defaults to `http://100.64.185.83:8000` if not set)

## Data Models

### Vendor Fields
- `name` (str, required) - Vendor name
- `website` (str, optional) - Vendor website URL
- `description` (str, optional) - Service description
- `criticality` (str) - Low | Medium | High | Critical
- `spend` (float) - Annual spend in dollars
- `data_sensitivity` (str) - Public | Internal | Confidential | Restricted
- `risk_score` (int, optional) - Calculated risk score (0-100)
- `risk_level` (str, optional) - Low | Medium | High
- `last_assessed` (str, optional) - ISO date string

### Analysis Result
- `risk_score` (int) - 0-100 risk score
- `risk_level` (str) - Low | Medium | High
- `findings` (list[str]) - Security findings
- `recommendations` (list[str]) - Remediation recommendations

## Airtable Integration

The backend maps between Pydantic models and Airtable field names:
- Model uses snake_case (e.g., `data_sensitivity`)
- Airtable uses Title Case with spaces (e.g., "Data Sensitivity")

Mapping is handled in `AirtableService._map_record_to_vendor()` and `create_vendor()`.

## AI Analysis Flow

1. Frontend sends `POST /analysis` with vendor_id, text_content, and document_type
2. Backend calls `AIService.analyze_text()` to process with Gemini
3. Returns structured `AnalysisResult` with risk score, level, findings, and recommendations
4. Frontend displays results in vendor detail page

**Current State**: AI analysis returns mock data pending structured output implementation.

## UI Component Library

Custom components in `src/components/ui/`:
- `Button` - Radix UI slot-based button with variants
- `Card`, `CardHeader`, `CardTitle`, `CardContent` - Composable card components
- `Input` - Styled form input

All components follow dark theme with slate colors and blue/violet accents.

## Testing

Backend tests use FastAPI TestClient (pytest):
- `test_read_main()` - Root endpoint
- `test_get_vendors()` - Vendor listing with mock data
- `test_create_vendor()` - Vendor creation
- `test_analyze_document()` - AI analysis endpoint

Run with: `pytest test_api.py` from backend directory.
