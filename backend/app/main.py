from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List
from pathlib import Path
from app.models import Vendor, VendorCreate, AnalysisRequest, AnalysisResult, Document, ComprehensiveAnalysisResult
from app.services.airtable_service import AirtableService
from app.services.ai_service import AIService
from app.services.document_service import DocumentService
from app.services.storage_service import get_storage_service
from app.services.document_airtable_service import DocumentAirtableService
from app.security.file_validation import FileValidator
from app.middleware.rate_limit import limiter, rate_limit_exceeded_handler
from app.middleware.security_headers import SecurityHeadersMiddleware
from app.middleware.audit_logging import AuditLoggingMiddleware, log_security_event
from app.config import settings
from slowapi.errors import RateLimitExceeded
import os

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs" if not settings.is_production else None,  # Disable docs in production
    redoc_url="/redoc" if not settings.is_production else None
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Add audit logging middleware (first, to log all requests)
if settings.AUDIT_LOG_ENABLED:
    app.add_middleware(AuditLoggingMiddleware)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# HTTPS redirect in production
if settings.is_production:
    app.add_middleware(HTTPSRedirectMiddleware)

# Configure CORS with restricted origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Use configured origins, not "*"
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if not settings.is_production else settings.cors_origins
)

# Create uploads directory
UPLOAD_DIR = Path(settings.STORAGE_PATH)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Dependency Injection
def get_airtable_service():
    return AirtableService()

def get_ai_service():
    return AIService()

def get_document_service():
    return DocumentAirtableService()

@app.get("/")
async def root():
    return {"message": "TPRM Agent API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/vendors", response_model=List[Vendor])
async def get_vendors(service: AirtableService = Depends(get_airtable_service)):
    return service.get_vendors()

@app.post("/vendors", response_model=Vendor)
async def create_vendor(vendor: VendorCreate, service: AirtableService = Depends(get_airtable_service)):
    return service.create_vendor(vendor.dict())

@app.post("/analysis", response_model=AnalysisResult)
async def analyze_document(
    request: AnalysisRequest,
    ai_service: AIService = Depends(get_ai_service),
    db_service: AirtableService = Depends(get_airtable_service)
):
    # 1. Perform AI Analysis
    analysis = await ai_service.analyze_text(request.text_content)

    # 2. Update Vendor Record (Mock update for now)
    # In a real scenario, we'd parse the AI result and update the Airtable record
    # db_service.update_vendor_risk(request.vendor_id, analysis)

    return analysis

@app.post("/vendors/{vendor_id}/documents/upload")
@limiter.limit("10/hour")  # Max 10 uploads per hour per IP
async def upload_documents(
    request: Request,
    vendor_id: str,
    files: List[UploadFile] = File(...),
    document_type: str = Form("General"),
    doc_service: DocumentAirtableService = Depends(get_document_service)
):
    """
    Upload one or more documents for a vendor (stores files, creates metadata records)
    Analysis is performed separately via /documents/{document_id}/analyze
    Includes security: MIME type validation, file size limits, malware protection
    Rate limit: 10 uploads per hour
    """
    # Validate vendor_id
    if not vendor_id.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid vendor ID")

    # Limit number of simultaneous uploads
    if len(files) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 files per upload request"
        )

    storage = get_storage_service()
    uploaded_documents = []
    validator = FileValidator()

    for file in files:
        # Comprehensive file validation (MIME type, size, extension matching)
        contents, file_ext = await validator.validate_upload(file)

        # Sanitize filename
        safe_filename = validator.sanitize_filename(file.filename)

        # Save file to storage
        file_path, file_url = await storage.save_file(file, vendor_id)

        # Create document record in Airtable
        document_data = {
            "vendor_id": vendor_id,
            "filename": safe_filename,
            "file_type": file_ext[1:],  # Remove the dot
            "document_type": document_type,
            "file_size": len(contents),
            "file_url": file_url
        }

        document_record = doc_service.create_document(document_data)
        uploaded_documents.append(document_record)

    # Log security event
    log_security_event(
        "file_upload",
        {
            "vendor_id": vendor_id,
            "file_count": len(uploaded_documents),
            "client_ip": request.client.host if request.client else "unknown",
            "document_types": list(set([doc.get("file_type") for doc in uploaded_documents]))
        }
    )

    return {
        "message": f"Successfully uploaded {len(uploaded_documents)} document(s)",
        "documents": uploaded_documents
    }

@app.get("/vendors/{vendor_id}/documents", response_model=List[Document])
async def get_vendor_documents(
    vendor_id: str,
    doc_service: DocumentAirtableService = Depends(get_document_service)
):
    """
    Get all documents for a specific vendor
    """
    documents = doc_service.get_vendor_documents(vendor_id)
    return documents

@app.post("/documents/{document_id}/analyze", response_model=AnalysisResult)
@limiter.limit("5/minute")  # Max 5 AI analyses per minute per IP
async def analyze_document(
    request: Request,
    document_id: str,
    doc_service: DocumentAirtableService = Depends(get_document_service),
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Analyze a previously uploaded document using AI
    Rate limit: 5 analyses per minute to prevent API abuse
    """
    # Get document metadata
    document = doc_service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get file from storage
    storage = get_storage_service()
    file_path = await storage.get_file_path(document["file_url"])

    # Extract text from document
    # Read file and create a mock UploadFile for DocumentService
    with open(file_path, 'rb') as f:
        content = f.read()

    # Create a simple file-like object
    class MockUploadFile:
        def __init__(self, filename, content):
            self.filename = filename
            self.content = content

        async def read(self):
            return self.content

    mock_file = MockUploadFile(document["filename"], content)
    text_content = await DocumentService.extract_text(mock_file)

    if not text_content or len(text_content.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Document appears to be empty or too short for analysis"
        )

    # Perform AI analysis
    analysis = await ai_service.analyze_text(text_content)

    # Update document with analysis results
    doc_service.update_document_analysis(document_id, {
        "risk_score": analysis.risk_score,
        "risk_level": analysis.risk_level,
        "findings": analysis.findings,
        "recommendations": analysis.recommendations
    })

    return analysis

# Serve uploaded files
@app.get("/files/{vendor_id}/{filename}")
async def serve_file(vendor_id: str, filename: str):
    """
    Serve uploaded files with path traversal protection
    """
    # Validate vendor_id (alphanumeric only)
    if not vendor_id.replace("-", "").replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid vendor ID")

    # Validate filename (no path separators or parent directory references)
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    # Construct path safely
    file_path = (UPLOAD_DIR / vendor_id / filename).resolve()

    # Ensure file is within upload directory (prevent path traversal)
    try:
        file_path.relative_to(UPLOAD_DIR.resolve())
    except ValueError:
        raise HTTPException(status_code=403, detail="Access denied")

    # Check file exists and is a file (not a directory)
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)

@app.post("/vendors/{vendor_id}/analyze-all", response_model=ComprehensiveAnalysisResult)
@limiter.limit("3/hour")  # Max 3 comprehensive analyses per hour (expensive operation)
async def analyze_all_vendor_documents(
    request: Request,
    vendor_id: str,
    airtable_service: AirtableService = Depends(get_airtable_service),
    doc_service: DocumentAirtableService = Depends(get_document_service),
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Perform comprehensive cross-document analysis for all vendor documents

    This endpoint:
    1. Retrieves all documents for the vendor
    2. Extracts text from each document
    3. Uses individual analyses if available
    4. Performs cross-document synthesis with AI
    5. Provides Go/No-Go decision recommendation

    Rate limit: 3 analyses per hour (computationally expensive)
    Performance target: <30s for 5 documents
    """
    # Get vendor information
    vendors = airtable_service.get_vendors()
    vendor = next((v for v in vendors if v.get('id') == vendor_id), None)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Get all documents for vendor
    documents = doc_service.get_vendor_documents(vendor_id)

    if not documents:
        raise HTTPException(
            status_code=400,
            detail="No documents found for this vendor. Please upload documents first."
        )

    if len(documents) > 20:
        raise HTTPException(
            status_code=400,
            detail="Too many documents (max 20 for comprehensive analysis)"
        )

    storage = get_storage_service()
    individual_analyses = []
    full_document_texts = []

    # Process each document
    for document in documents:
        try:
            # Get file from storage
            file_path = await storage.get_file_path(document.get("file_url"))

            # Extract text
            with open(file_path, 'rb') as f:
                content = f.read()

            class MockUploadFile:
                def __init__(self, filename, content):
                    self.filename = filename
                    self.content = content
                async def read(self):
                    return self.content

            mock_file = MockUploadFile(document.get("filename"), content)
            text_content = await DocumentService.extract_text(mock_file)

            # Store full text for AI analysis
            full_document_texts.append({
                'filename': document.get("filename"),
                'text': text_content
            })

            # Use existing analysis if available, otherwise create summary
            if document.get("analysis_status") == "Completed" and document.get("risk_score"):
                individual_analyses.append({
                    'filename': document.get("filename"),
                    'document_type': document.get("document_type"),
                    'risk_score': document.get("risk_score"),
                    'risk_level': document.get("risk_level"),
                    'findings': document.get("findings", []),
                    'recommendations': document.get("recommendations", [])
                })
            else:
                # Quick analysis for unanalyzed documents
                quick_analysis = await ai_service.analyze_text(text_content[:5000])
                individual_analyses.append({
                    'filename': document.get("filename"),
                    'document_type': document.get("document_type"),
                    'risk_score': quick_analysis.risk_score,
                    'risk_level': quick_analysis.risk_level.value,
                    'findings': quick_analysis.findings,
                    'recommendations': quick_analysis.recommendations
                })

        except Exception as e:
            print(f"Error processing document {document.get('filename')}: {e}")
            # Add placeholder for failed document
            individual_analyses.append({
                'filename': document.get("filename"),
                'document_type': document.get("document_type", "Unknown"),
                'risk_score': 50,
                'risk_level': "Medium",
                'findings': [f"Error extracting document: {str(e)}"],
                'recommendations': ["Manual review required"]
            })

    # Perform comprehensive analysis
    comprehensive_result = await ai_service.analyze_all_documents(
        vendor_id=vendor_id,
        vendor_name=vendor.get('name', 'Unknown'),
        individual_analyses=individual_analyses,
        full_document_texts=full_document_texts
    )

    # Update vendor's risk score in Airtable
    airtable_service.update_vendor_risk(
        vendor_id=vendor_id,
        risk_score=comprehensive_result.overall_risk_score,
        risk_level=comprehensive_result.overall_risk_level.value
    )

    # Log security event
    log_security_event(
        "comprehensive_analysis",
        {
            "vendor_id": vendor_id,
            "vendor_name": vendor.get('name', 'Unknown'),
            "documents_analyzed": len(documents),
            "overall_risk_score": comprehensive_result.overall_risk_score,
            "decision": comprehensive_result.decision.value,
            "processing_time": comprehensive_result.processing_time_seconds,
            "client_ip": request.client.host if request.client else "unknown"
        }
    )

    return comprehensive_result
