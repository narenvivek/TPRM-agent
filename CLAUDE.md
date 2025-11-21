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

---

## Development Session Summary (2024-11-20)

### Session Overview
This session evolved the TPRM application from initial concept to a working v1.0.0 baseline with document upload, AI-powered analysis, and comprehensive Airtable integration.

### Key Accomplishments

#### 1. Environment Migration (Windows → Linux)
- Migrated development from Windows to Linux (WSL2)
- Used `uv` package manager for clean Python virtual environment setup
- Fixed cross-platform path issues (`.venv/Scripts/activate` → `.venv/bin/activate`)
- Created proper `.env.local` for frontend to fix hardcoded Windows IP

#### 2. Real AI Integration (Gemini 2.5 Flash)
**Previous State**: Mock AI responses
**New State**: Full Google Gemini AI integration with structured JSON output

Key implementation in `backend/app/services/ai_service.py`:
```python
class AIService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')

    async def analyze_text(self, text: str) -> AnalysisResult:
        prompt = """You are a Third-Party Risk Management (TPRM) security analyst.
        Analyze the following vendor document and provide a comprehensive risk assessment.

        Document Content:
        {text}

        Provide assessment in JSON format:
        {{
            "risk_score": <0-100>,
            "risk_level": "<Low|Medium|High>",
            "findings": ["finding1", "finding2", ...],
            "recommendations": ["rec1", "rec2", ...]
        }}"""

        response = self.model.generate_content(prompt)
        # JSON parsing with error handling
        parsed = json.loads(cleaned_text)
        return AnalysisResult(**parsed)
```

**Model Evolution**: `gemini-pro` → `gemini-1.5-flash` → `gemini-2.5-flash` (final working version)

#### 3. Document Storage Architecture
Implemented flexible storage system supporting local and cloud storage:

**New Services**:
- `backend/app/services/storage_service.py` - Abstract storage interface
- `backend/app/services/document_service.py` - Text extraction (PDF, DOCX, TXT)
- `backend/app/services/document_airtable_service.py` - Document metadata tracking

**Storage Features**:
- Unique filename generation with UUID
- Vendor-based directory organization
- Accessible file URLs: `http://localhost:8000/files/{vendor_id}/{filename}`
- Support for multi-file uploads
- Cloud storage ready (GCS placeholder implemented)

#### 4. Airtable Documents Table
Created comprehensive schema in Airtable:

**Documents Table Fields**:
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
- Findings (Long text - JSON array)
- Recommendations (Long text - JSON array)

#### 5. API Architecture Redesign
**Previous**: Upload and analyze in one step
**New**: Separated concerns with dedicated endpoints

**New Endpoints**:
```python
POST /vendors/{vendor_id}/documents/upload
  - Upload multiple documents simultaneously
  - Stores files locally with unique URLs
  - Creates Airtable records with "Not Analyzed" status
  - Returns: List of uploaded document records

GET /vendors/{vendor_id}/documents
  - Retrieve all documents for a vendor
  - Includes analysis status and results
  - Returns: List of Document objects

POST /documents/{document_id}/analyze
  - Analyze a previously uploaded document
  - Extracts text from stored file
  - Sends to Gemini AI for analysis
  - Updates Airtable with results
  - Returns: AnalysisResult

GET /files/{vendor_id}/{filename}
  - Serve uploaded documents
  - Returns: FileResponse for download/viewing
```

#### 6. Frontend Enhancements
**File**: `frontend/src/app/vendors/[id]/page.tsx`

**New Features**:
- Multi-file upload with file input
- Real-time document list with analysis status badges
- Individual "Analyze with AI" buttons for each document
- Inline display of analysis results with risk scoring
- Document download links
- Loading states for upload and analysis operations

**Key UI Patterns**:
```typescript
// Multi-file selection
<input type="file" multiple accept=".pdf,.docx,.txt" />

// Document list with status
{documents.map(doc => (
  <div key={doc.id}>
    <span className={doc.analysis_status === 'Completed'
      ? 'bg-green-500/10 text-green-400'
      : 'bg-yellow-500/10 text-yellow-400'}>
      {doc.analysis_status}
    </span>
    {doc.analysis_status !== 'Completed' && (
      <Button onClick={() => handleAnalyzeDocument(doc.id)}>
        Analyze with AI
      </Button>
    )}
  </div>
))}
```

### Critical Bugs Fixed

#### Bug 1: API URL Hardcoded from Windows
- **Issue**: Frontend had `http://100.64.185.83:8000` hardcoded
- **Fix**: Created `frontend/.env.local` with `NEXT_PUBLIC_API_URL=http://localhost:8000`
- **Impact**: Frontend could connect to backend on Linux

#### Bug 2: Gemini Model Not Found
- **Issue**: `404 models/gemini-pro is not found`
- **Fix**: Updated to `gemini-2.5-flash` (current model name)
- **Tool Used**: `genai.list_models()` to discover available models

#### Bug 3: Airtable Document Query Returns Empty
- **Issue**: Airtable formula queries failed to retrieve documents
- **Initial Approach**: Used `FIND('{vendor_id}', ARRAYJOIN({Vendor}))`
- **Fix**: Switched to Python-side filtering (more reliable with linked records)
```python
all_records = self.table.all()
filtered = [r for r in all_records
           if vendor_id in r.get('fields', {}).get('Vendor', [])]
```

#### Bug 4: Upload Count Shows 0
- **Issue**: Alert showed "Successfully uploaded 0 document(s)" after successful upload
- **Root Cause**: Accessing `selectedFiles.length` after state was cleared
- **Fix**: Parse response count before clearing state
```typescript
const result = await res.json();
const uploadCount = result.documents?.length || selectedFiles.length;
// ... clear selectedFiles ...
alert(`Successfully uploaded ${uploadCount} document(s)!`);
```

### Git Repository Initialization
Created baseline v1.0.0 with comprehensive `.gitignore`:
- Initial commit: `d87b018`
- 37 files committed
- 9,733 lines of code
- Excluded: `.env`, `.venv/`, `node_modules/`, `uploads/`, `__pycache__/`

### Architecture Documentation
Created extensive documentation:
- `README.md` - User-facing setup and usage guide
- `AI_AGENT_ARCHITECTURE.md` - Proposed autonomous multi-agent system with LangGraph/CrewAI
- `NO_CODE_AGENT_PLATFORMS.md` - n8n and no-code agent builder comparison

### Current Application State (v1.0.0)
- ✅ Multi-file document upload with unique URLs
- ✅ Real Gemini AI analysis with structured output
- ✅ Airtable integration (Vendors + Documents tables)
- ✅ Separate upload/analyze workflow
- ✅ Frontend with real-time status updates
- ✅ Document download capability
- ✅ Risk scoring and findings display
- ✅ Comprehensive error handling

---

## Feature Roadmap (v2.0.0+)

### Feature 1: Combined Multi-Document Analysis
**Goal**: Analyze all vendor documents together for holistic risk assessment

**Implementation Plan**:
1. Create new endpoint: `POST /vendors/{vendor_id}/analyze-all`
2. Retrieve all documents for vendor
3. Extract text from all files
4. Feed individual analysis results + full document corpus to AI
5. AI synthesizes findings across all documents
6. Detect contradictions (e.g., SOC2 cert but pentest shows critical vulns)
7. Generate comprehensive vendor risk report

**AI Prompt Strategy**:
```python
prompt = f"""You are analyzing multiple documents for vendor {vendor_name}.

Individual Document Analyses:
{json.dumps(individual_analyses)}

Full Document Contents:
{combined_text}

Provide a comprehensive risk assessment considering:
1. Consistency across documents
2. Contradictions or red flags
3. Completeness of compliance evidence
4. Overall vendor security posture

Output JSON with:
- overall_risk_score (0-100)
- overall_risk_level (Low/Medium/High)
- consolidated_findings
- cross_document_insights
- recommendations
- decision_recommendation (Go/No-Go with justification)
"""
```

### Feature 2: Risk Matrix Configuration
**Goal**: Visual risk matrix based on spend and criticality with configurable thresholds

**Data Model Enhancement**:
```python
class RiskMatrixConfig(BaseModel):
    spend_ranges: List[SpendRange] = [
        SpendRange(min=10000, max=100000, label="$10k-$100k"),
        SpendRange(min=100000, max=500000, label="$100k-$500k"),
        SpendRange(min=500000, max=1000000, label="$500k-$1M"),
        SpendRange(min=1000000, max=3000000, label="$1M-$3M"),
    ]
    criticality_factors: Dict[str, int] = {
        "data_sensitivity": 40,  # weight percentage
        "business_criticality": 30,
        "regulatory_impact": 30
    }

class Vendor(BaseModel):
    # ... existing fields ...
    business_criticality: str  # Low, Medium, High, Critical
    regulatory_impact: str     # None, Low, Medium, High
    calculated_criticality_score: Optional[int]  # 0-100
    risk_matrix_position: Optional[Dict[str, Any]]  # {x: spend_bucket, y: criticality_score}
```

**Frontend Component**:
- Interactive risk matrix heatmap (D3.js or Recharts)
- X-axis: Spend ranges
- Y-axis: Criticality score (0-100)
- Color coding: Green (Low), Yellow (Medium), Red (High)
- Vendor bubbles positioned on matrix
- Click to view vendor details

**API Endpoints**:
```python
GET /risk-matrix/config - Get current matrix configuration
PUT /risk-matrix/config - Update matrix settings (admin only)
GET /risk-matrix/vendors - Get all vendors with matrix positions
POST /vendors/{id}/calculate-position - Recalculate vendor risk position
```

### Feature 3: EntraID (Azure AD) Authentication
**Goal**: Enterprise SSO with Microsoft Entra ID (formerly Azure AD)

**Backend Dependencies**:
```bash
pip install msal python-jose[cryptography] fastapi-azure-auth
```

**Implementation**:
```python
# backend/app/auth/entra_auth.py
from fastapi_azure_auth import SingleTenantAzureAuthorizationCodeBearer

azure_scheme = SingleTenantAzureAuthorizationCodeBearer(
    app_client_id=os.getenv("AZURE_CLIENT_ID"),
    tenant_id=os.getenv("AZURE_TENANT_ID"),
    scopes={
        'api://tprm-agent/user.read': 'Read user profile',
    }
)

# Protected endpoint example
@app.get("/vendors")
async def get_vendors(user: dict = Depends(azure_scheme)):
    user_email = user.get("preferred_username")
    # ... vendor logic with user context ...
```

**Frontend (Next.js)**:
```bash
npm install @azure/msal-browser @azure/msal-react
```

```typescript
// frontend/src/lib/authConfig.ts
import { PublicClientApplication } from "@azure/msal-browser";

export const msalConfig = {
  auth: {
    clientId: process.env.NEXT_PUBLIC_AZURE_CLIENT_ID!,
    authority: `https://login.microsoftonline.com/${process.env.NEXT_PUBLIC_AZURE_TENANT_ID}`,
    redirectUri: "http://localhost:3000",
  },
};

export const msalInstance = new PublicClientApplication(msalConfig);
```

**Environment Variables**:
```bash
# Backend
AZURE_TENANT_ID=your-tenant-id
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret

# Frontend
NEXT_PUBLIC_AZURE_TENANT_ID=your-tenant-id
NEXT_PUBLIC_AZURE_CLIENT_ID=your-client-id
```

### Feature 4: Specialized AI Agent with MCP Tools
**Goal**: Autonomous AI agent with memory, tool access, and decision-making capabilities

**Architecture**:
```python
# backend/app/agents/tprm_agent.py
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import Tool

class TPRMAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        self.memory = VectorStoreMemory()  # Document embeddings
        self.tools = [
            document_analysis_tool,
            defender_cloud_apps_tool,
            netskope_cci_tool,
            breach_database_tool,
            certification_verification_tool
        ]
        self.agent = create_react_agent(self.llm, self.tools)

    async def assess_vendor(self, vendor_id: str) -> ComprehensiveAssessment:
        # Agent plans and executes multi-step analysis
        plan = await self.agent.plan(f"""
        Perform comprehensive risk assessment for vendor {vendor_id}:
        1. Retrieve all uploaded documents from memory
        2. Query CASB (Microsoft Defender) for SaaS risk score
        3. Check breach databases for security incidents
        4. Verify compliance certifications
        5. Analyze all findings and provide Go/No-Go recommendation
        """)

        result = await self.agent.execute(plan)
        return self.format_assessment(result)
```

**Specialized Prompts**:
```python
TPRM_AGENT_PROMPT = """You are an expert Third-Party Risk Management analyst.

Your responsibilities:
1. Analyze vendor security documentation with deep scrutiny
2. Query external risk intelligence sources (CASB, breach DBs)
3. Identify compliance gaps and security weaknesses
4. Provide actionable recommendations with business context
5. Make data-driven Go/No-Go decisions for vendor approval

When analyzing documents:
- Focus on security controls (access management, encryption, incident response)
- Look for evidence vs. claims (certifications vs. actual practices)
- Consider vendor's security maturity and track record
- Assess alignment with organization's risk appetite

Decision Framework:
- GO: Risk score < 40 OR (score < 60 AND mitigations acceptable)
- CONDITIONAL: Score 40-70 with specific remediation required
- NO-GO: Score > 70 OR critical unmitigated risks

Always provide:
1. Executive summary (2-3 sentences)
2. Risk score with breakdown by category
3. Key findings (prioritized by severity)
4. Recommendations (specific, actionable)
5. Decision with clear justification
"""
```

**Memory System** (RAG for uploaded documents):
```python
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

class AgentMemory:
    def __init__(self):
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.vectorstore = Chroma(embedding_function=self.embeddings)

    async def store_document(self, vendor_id: str, document: Document):
        # Chunk document and create embeddings
        chunks = self.chunk_document(document.content)
        self.vectorstore.add_texts(
            texts=chunks,
            metadatas=[{"vendor_id": vendor_id, "doc_id": document.id}] * len(chunks)
        )

    async def retrieve_context(self, vendor_id: str, query: str) -> List[str]:
        # Semantic search across vendor's documents
        results = self.vectorstore.similarity_search(
            query,
            filter={"vendor_id": vendor_id},
            k=5
        )
        return [r.page_content for r in results]
```

### Feature 5: MCP Tools for CASB Integration
**Goal**: Out-of-box integrations with Microsoft Defender for Cloud Apps and Netskope CCI

**MCP Server for Microsoft Defender**:
```python
# backend/app/mcp/defender_server.py
from mcp.server import Server
from mcp.types import Tool, TextContent

class DefenderMCPServer:
    def __init__(self):
        self.server = Server("defender-cloud-apps")
        self.base_url = "https://portal.cloudappsecurity.com/api/v1"
        self.api_token = os.getenv("DEFENDER_API_TOKEN")

    @self.server.list_tools()
    async def list_tools(self) -> list[Tool]:
        return [
            Tool(
                name="get_app_risk_score",
                description="Retrieve SaaS app risk score from Microsoft Defender",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "app_name": {"type": "string", "description": "Vendor/app name"}
                    },
                    "required": ["app_name"]
                }
            ),
            Tool(
                name="get_oauth_permissions",
                description="Get OAuth permissions requested by app",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "app_id": {"type": "string"}
                    }
                }
            ),
            Tool(
                name="check_security_alerts",
                description="Check for security alerts related to app",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "app_id": {"type": "string"},
                        "severity": {"type": "string", "enum": ["low", "medium", "high"]}
                    }
                }
            )
        ]

    @self.server.call_tool()
    async def call_tool(self, name: str, arguments: dict) -> list[TextContent]:
        if name == "get_app_risk_score":
            return await self.get_app_risk_score(arguments["app_name"])
        # ... other tool handlers ...

    async def get_app_risk_score(self, app_name: str) -> list[TextContent]:
        response = await self.http_client.get(
            f"{self.base_url}/apps/",
            params={"filter": f"name:eq:{app_name}"},
            headers={"Authorization": f"Token {self.api_token}"}
        )
        data = response.json()

        if data.get("data"):
            app = data["data"][0]
            risk_info = {
                "app_name": app["name"],
                "risk_score": app["riskScore"],  # 0-10 scale
                "category": app["category"],
                "certifications": app.get("certifications", []),
                "compliance": app.get("compliance", {}),
                "last_modified": app["lastModified"]
            }
            return [TextContent(
                type="text",
                text=json.dumps(risk_info, indent=2)
            )]
        else:
            return [TextContent(type="text", text=f"App '{app_name}' not found in Defender")]
```

**MCP Server for Netskope CCI**:
```python
# backend/app/mcp/netskope_server.py
class NetskopeMCPServer:
    def __init__(self):
        self.server = Server("netskope-cci")
        self.base_url = "https://api.netskope.com/api/v2"
        self.api_token = os.getenv("NETSKOPE_API_TOKEN")

    @self.server.list_tools()
    async def list_tools(self) -> list[Tool]:
        return [
            Tool(
                name="get_cci_score",
                description="Get Cloud Confidence Index (CCI) score for SaaS app",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "app_name": {"type": "string"}
                    }
                }
            ),
            Tool(
                name="get_risk_assessment",
                description="Get detailed risk assessment from Netskope",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "app_name": {"type": "string"}
                    }
                }
            )
        ]

    async def get_cci_score(self, app_name: str) -> list[TextContent]:
        response = await self.http_client.get(
            f"{self.base_url}/cloud_apps",
            params={"app_name": app_name},
            headers={"Netskope-Api-Token": self.api_token}
        )
        data = response.json()

        cci_info = {
            "app_name": data["app_name"],
            "cci_score": data["cci_score"],  # 0-100
            "risk_level": data["risk_level"],
            "categories": data["categories"],
            "certifications": data["certifications"],
            "data_sovereignty": data.get("data_sovereignty", [])
        }
        return [TextContent(type="text", text=json.dumps(cci_info, indent=2))]
```

**Agent Integration with MCP Tools**:
```python
from langchain_core.tools import StructuredTool

# Convert MCP tools to LangChain tools
defender_tool = StructuredTool.from_function(
    func=defender_server.get_app_risk_score,
    name="defender_risk_score",
    description="Get Microsoft Defender Cloud Apps risk score for vendor"
)

netskope_tool = StructuredTool.from_function(
    func=netskope_server.get_cci_score,
    name="netskope_cci",
    description="Get Netskope Cloud Confidence Index for vendor"
)

# Agent uses tools automatically
agent = create_react_agent(
    llm=llm,
    tools=[defender_tool, netskope_tool, document_tool, breach_tool]
)
```

**Environment Variables for CASB Integration**:
```bash
# Microsoft Defender for Cloud Apps
DEFENDER_API_TOKEN=your-defender-token
DEFENDER_TENANT_ID=your-tenant-id

# Netskope
NETSKOPE_API_TOKEN=your-netskope-token
NETSKOPE_TENANT=your-tenant-name
```

---

## Implementation Priority

### Phase 1 (Weeks 1-2): Authentication & Risk Matrix
1. Implement EntraID authentication
2. Add risk matrix configuration to Airtable
3. Build risk matrix visualization component
4. Update vendor model with criticality factors

### Phase 2 (Weeks 3-4): Combined Analysis
1. Implement multi-document analysis endpoint
2. Enhance AI prompts for cross-document synthesis
3. Create comprehensive report UI
4. Add decision recommendation display

### Phase 3 (Weeks 5-6): MCP Tools & CASB Integration
1. Set up MCP servers for Defender and Netskope
2. Implement API clients for CASB platforms
3. Create tool registration system
4. Test with real CASB data

### Phase 4 (Weeks 7-8): AI Agent System
1. Implement LangGraph agent with memory
2. Integrate MCP tools with agent
3. Create specialized TPRM prompts
4. Build agent execution UI with progress tracking
5. Add Go/No-Go decision framework

---

## Technical Notes

### MCP (Model Context Protocol)
- MCP servers expose tools that AI models can call
- Each tool has JSON schema defining inputs/outputs
- Agent runtime translates LLM tool calls to MCP requests
- Enables modular, reusable tool integrations

### LangGraph Agent Architecture
- **Nodes**: Agent steps (plan, execute tool, synthesize)
- **Edges**: Conditional routing based on agent decisions
- **State**: Shared context across execution graph
- **Memory**: Vector store for document retrieval (RAG)

### CASB Integration Challenges
- **Rate Limiting**: Implement caching for frequently accessed data
- **Data Mapping**: Normalize risk scores across platforms (Defender 0-10, Netskope 0-100)
- **Authentication**: Support multiple auth methods (API tokens, OAuth)
- **Error Handling**: Graceful degradation if CASB unavailable

---

## Dependencies to Add

### Backend
```bash
# Agent framework
pip install langgraph langchain langchain-google-genai langchain-community

# MCP server
pip install mcp

# Vector store for memory
pip install chromadb

# Azure AD auth
pip install msal fastapi-azure-auth python-jose[cryptography]

# CASB clients
pip install httpx  # already installed
```

### Frontend
```bash
# Azure AD
npm install @azure/msal-browser @azure/msal-react

# Risk matrix visualization
npm install recharts d3

# Advanced UI components
npm install @radix-ui/react-dialog @radix-ui/react-tabs
```

---

This roadmap transforms the TPRM application from a document analysis tool into a comprehensive, AI-powered vendor risk management platform with autonomous decision-making capabilities.
- remember to create a version update and a release notes for each feature update