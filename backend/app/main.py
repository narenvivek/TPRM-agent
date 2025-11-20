from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from typing import List
from pathlib import Path
from app.models import Vendor, VendorCreate, AnalysisRequest, AnalysisResult, Document
from app.services.airtable_service import AirtableService
from app.services.ai_service import AIService
from app.services.document_service import DocumentService
from app.services.storage_service import get_storage_service
from app.services.document_airtable_service import DocumentAirtableService
import os

app = FastAPI(title="TPRM Agent API", version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory
UPLOAD_DIR = Path(os.getenv("STORAGE_PATH", "./uploads"))
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
async def upload_documents(
    vendor_id: str,
    files: List[UploadFile] = File(...),
    document_type: str = Form("General"),
    doc_service: DocumentAirtableService = Depends(get_document_service)
):
    """
    Upload one or more documents for a vendor (stores files, creates metadata records)
    Analysis is performed separately via /documents/{document_id}/analyze
    """
    storage = get_storage_service()
    uploaded_documents = []

    for file in files:
        # Validate file type
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.pdf', '.docx', '.txt']:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}. Supported: .pdf, .docx, .txt"
            )

        # Save file to storage
        file_path, file_url = await storage.save_file(file, vendor_id)

        # Get file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset

        # Create document record in Airtable
        document_data = {
            "vendor_id": vendor_id,
            "filename": file.filename,
            "file_type": file_ext[1:],  # Remove the dot
            "document_type": document_type,
            "file_size": file_size,
            "file_url": file_url
        }

        document_record = doc_service.create_document(document_data)
        uploaded_documents.append(document_record)

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
async def analyze_document(
    document_id: str,
    doc_service: DocumentAirtableService = Depends(get_document_service),
    ai_service: AIService = Depends(get_ai_service)
):
    """
    Analyze a previously uploaded document using AI
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
    Serve uploaded files
    """
    file_path = UPLOAD_DIR / vendor_id / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(file_path)
