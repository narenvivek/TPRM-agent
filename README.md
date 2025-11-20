# TPRM Agent - Third-Party Risk Management System

AI-powered vendor risk assessment platform with document analysis, Airtable integration, and comprehensive compliance tracking.

## Features

- **Vendor Management**: Track vendors with criticality levels, spend data, and data sensitivity
- **Document Upload & Storage**: Multi-file upload support (PDF, DOCX, TXT)
- **AI Risk Analysis**: Gemini 2.5 Flash powered document analysis
- **Airtable Integration**: Centralized data storage with Documents and Vendors tables
- **Risk Scoring**: Automated risk assessment with findings and recommendations
- **Modern UI**: Next.js frontend with dark theme and smooth animations

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   Next.js   │────────▶│   FastAPI    │────────▶│  Airtable   │
│   Frontend  │         │   Backend    │         │   Database  │
│  (Port 3000)│         │  (Port 8000) │         └─────────────┘
└─────────────┘         └──────┬───────┘
                               │
                               ├─────▶ Gemini AI (Risk Analysis)
                               │
                               └─────▶ Local Storage (Documents)
```

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Pydantic** - Data validation
- **pyairtable** - Airtable Python SDK
- **Google Generative AI** - Gemini 2.5 Flash
- **pypdf, python-docx** - Document parsing
- **uvicorn** - ASGI server

### Frontend
- **Next.js 16** - React framework with App Router
- **React 19** - UI library
- **Tailwind CSS v4** - Styling
- **Framer Motion** - Animations
- **Radix UI** - Accessible components
- **Lucide React** - Icons

## Setup

### Prerequisites
- Python 3.12+
- Node.js 18+
- Airtable account with API access
- Google AI API key (Gemini)

### Backend Setup

```bash
cd backend

# Create virtual environment with uv
uv venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
uv pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials:
# - AIRTABLE_API_KEY
# - AIRTABLE_BASE_ID
# - GEMINI_API_KEY
# - STORAGE_PATH (default: ./uploads)

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
# Create .env.local with:
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run development server
npm run dev
```

### Airtable Setup

Create two tables in your Airtable base:

**Vendors Table:**
- Name (Single line text)
- Website (URL)
- Description (Long text)
- Criticality (Single select: Low, Medium, High, Critical)
- Spend (Number)
- Data Sensitivity (Single select: Public, Internal, Confidential, Restricted)
- Risk Score (Number)
- Risk Level (Single select: Low, Medium, High)
- Last Assessed (Date)

**Documents Table:**
- Filename (Single line text)
- Vendor (Link to Vendors table)
- File Type (Single select: pdf, docx, txt)
- Document Type (Single line text)
- File Size (Number)
- File URL (URL)
- Upload Date (Date)
- Analysis Status (Single select: Not Analyzed, Analyzing, Completed)
- Risk Score (Number)
- Risk Level (Single select: Low, Medium, High)
- Findings (Long text)
- Recommendations (Long text)

## Usage

1. **Access the app**: Navigate to `http://localhost:3000`

2. **Add a vendor**: Click "Add Vendor" and fill in vendor details

3. **Upload documents**:
   - Click on a vendor
   - Select one or more compliance documents
   - Click "Upload Documents"

4. **Analyze documents**:
   - Click "Analyze with AI" on any uploaded document
   - Gemini AI will extract findings and recommendations
   - Results are stored in Airtable

5. **View risk assessment**: Analysis results appear inline with risk scores and findings

## API Endpoints

### Vendors
- `GET /vendors` - List all vendors
- `POST /vendors` - Create new vendor
- `GET /health` - Health check

### Documents
- `POST /vendors/{vendor_id}/documents/upload` - Upload multiple documents
- `GET /vendors/{vendor_id}/documents` - Get all documents for a vendor
- `POST /documents/{document_id}/analyze` - Analyze a document with AI
- `GET /files/{vendor_id}/{filename}` - Serve uploaded file

### Legacy
- `POST /analysis` - Direct text analysis (deprecated)

## Development

### Backend Testing
```bash
cd backend
pytest test_api.py
```

### Frontend Build
```bash
cd frontend
npm run build
npm start
```

## Future Enhancements

See `AI_AGENT_ARCHITECTURE.md` for the planned autonomous AI agent system with:
- Multi-agent orchestration (LangGraph/CrewAI)
- Microsoft Defender for Cloud Apps integration
- OSINT (breach databases, certification verification)
- Continuous monitoring
- Automated risk assessment workflows

See `NO_CODE_AGENT_PLATFORMS.md` for no-code/low-code agent building options (n8n, Vertex AI).

## License

Proprietary - Internal Use Only

## Version

**v1.0.0** - Initial release with document upload, AI analysis, and Airtable integration
