from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class VendorBase(BaseModel):
    name: str
    website: Optional[str] = None
    description: Optional[str] = None
    criticality: Optional[str] = "Low"  # Low, Medium, High, Critical
    spend: Optional[float] = 0.0
    data_sensitivity: Optional[str] = "Public" # Public, Internal, Confidential, Restricted

class VendorCreate(VendorBase):
    pass

class Vendor(VendorBase):
    id: str
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    last_assessed: Optional[str] = None

class DocumentBase(BaseModel):
    filename: str
    file_type: str  # pdf, docx, txt
    document_type: str  # SOC2, Pentest, Compliance, etc.
    file_size: int  # in bytes

class DocumentCreate(DocumentBase):
    vendor_id: str
    file_url: str

class Document(DocumentBase):
    id: str
    vendor_id: str
    file_url: str
    upload_date: str
    analysis_status: Optional[str] = "Not Analyzed"  # Not Analyzed, Analyzing, Completed
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    findings: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None

class AnalysisRequest(BaseModel):
    vendor_id: str
    text_content: str
    document_type: str # e.g., "SOC2", "Pentest", "Compliance"

class AnalysisResult(BaseModel):
    risk_score: int
    risk_level: str
    findings: List[str]
    recommendations: List[str]
