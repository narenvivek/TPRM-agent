# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Combined multi-document analysis
- Risk matrix visualization
- EntraID authentication
- AI agent system with MCP tools
- CASB integration (Microsoft Defender, Netskope)

## [1.0.0] - 2024-11-20

### Added
- **FastAPI backend** with async support and dependency injection
- **Next.js frontend** with App Router and dark theme
- **Multi-file document upload** with support for PDF, DOCX, TXT
- **Real Gemini AI analysis** using gemini-2.5-flash model
- **Airtable integration** with Vendors and Documents tables
- **Document storage** with accessible URLs and vendor-based organization
- **Individual document analysis** with risk scoring and findings
- **Comprehensive error handling** with graceful degradation

### Backend Services
- `AirtableService` - Vendor and document data management
- `AIService` - Gemini AI integration with structured JSON output
- `StorageService` - Abstracted storage (local with cloud-ready architecture)
- `DocumentService` - Text extraction from PDF, DOCX, TXT files
- `DocumentAirtableService` - Document metadata and analysis tracking

### API Endpoints
- `GET /` - Health check
- `GET /health` - Detailed health status with service availability
- `GET /vendors` - List all vendors with risk scores
- `POST /vendors` - Create new vendor
- `POST /vendors/{vendor_id}/documents/upload` - Upload multiple documents
- `GET /vendors/{vendor_id}/documents` - Get all documents for vendor
- `POST /documents/{document_id}/analyze` - Analyze document with AI
- `GET /files/{vendor_id}/{filename}` - Serve uploaded files

### Frontend Features
- Dashboard with vendor list and risk metrics
- Vendor onboarding form with criticality and spend tracking
- Vendor detail page with document management
- Multi-file upload with drag-and-drop
- Real-time analysis status tracking
- Inline display of AI analysis results
- Document download capability

### Infrastructure
- Docker support for containerized deployment
- Kubernetes manifests with auto-scaling and monitoring
- Environment-based configuration with .env files
- Virtual environment setup with `uv` package manager
- Git version control with comprehensive .gitignore

### Documentation
- `README.md` - Complete setup and usage guide
- `CLAUDE.md` - AI-assisted development guide with session history
- `AI_AGENT_ARCHITECTURE.md` - Proposed autonomous agent system
- `NO_CODE_AGENT_PLATFORMS.md` - n8n integration guide
- `KUBERNETES.md` - Production deployment guide
- `VERSION_MANAGEMENT.md` - Release process documentation

### Data Models

**Vendor Fields**:
- Name, Website, Description
- Criticality (Low/Medium/High/Critical)
- Spend (annual dollars)
- Data Sensitivity (Public/Internal/Confidential/Restricted)
- Risk Score (0-100), Risk Level (Low/Medium/High)
- Last Assessed date

**Document Fields**:
- Filename, File Type, Document Type
- File Size, File URL
- Upload Date, Analysis Status
- Risk Score, Risk Level
- Findings (JSON array)
- Recommendations (JSON array)

### Fixed
- API URL hardcoded from Windows environment (now uses .env.local)
- Gemini model compatibility (updated to gemini-2.5-flash)
- Airtable document query with linked records (Python-side filtering)
- Upload count showing 0 after successful upload
- Cross-platform virtual environment paths

### Security
- Environment variable management for API keys
- Secure file storage with unique filenames (UUID)
- CORS middleware configuration
- Input validation with Pydantic models

### Performance
- Async/await throughout backend for non-blocking I/O
- Efficient document text extraction
- Optimized Airtable queries
- Frontend loading states and error handling

### Developer Experience
- Clean separation of concerns (services architecture)
- Type hints throughout Python code
- TypeScript for type-safe frontend
- Comprehensive error messages
- Development server auto-reload

---

[Unreleased]: https://github.com/your-org/tprm-agent/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/your-org/tprm-agent/releases/tag/v1.0.0
