from pydantic import BaseModel, Field, HttpUrl, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import re

# Security enums for controlled vocabularies
class Criticality(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"

class DataSensitivity(str, Enum):
    PUBLIC = "Public"
    INTERNAL = "Internal"
    CONFIDENTIAL = "Confidential"
    RESTRICTED = "Restricted"

class RiskLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class VendorBase(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Vendor name (alphanumeric, spaces, hyphens, dots, ampersands only)"
    )
    website: Optional[HttpUrl] = Field(
        None,
        description="Vendor website URL"
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Vendor description"
    )
    criticality: Criticality = Field(
        default=Criticality.LOW,
        description="Business criticality of the vendor"
    )
    spend: float = Field(
        default=0.0,
        ge=0,
        le=1000000000,  # Max $1B
        description="Annual spend in USD"
    )
    data_sensitivity: DataSensitivity = Field(
        default=DataSensitivity.PUBLIC,
        description="Sensitivity of data shared with vendor"
    )

    @field_validator('name')
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        """Sanitize vendor name to prevent XSS and injection attacks"""
        if not v or not v.strip():
            raise ValueError("Vendor name cannot be empty")

        # Remove dangerous characters
        v = v.strip()

        # Only allow alphanumeric, spaces, hyphens, dots, ampersands
        if not re.match(r'^[a-zA-Z0-9\s\-\.&,]+$', v):
            raise ValueError(
                "Vendor name can only contain letters, numbers, spaces, hyphens, dots, commas, and ampersands"
            )

        return v

    @field_validator('description')
    @classmethod
    def sanitize_description(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize description to prevent XSS"""
        if v is None:
            return v

        v = v.strip()

        # Remove potential XSS characters
        dangerous_chars = ['<', '>', '"', "'", '`']
        for char in dangerous_chars:
            v = v.replace(char, '')

        return v if v else None

class VendorCreate(VendorBase):
    pass

class Vendor(VendorBase):
    id: str
    risk_score: Optional[int] = Field(None, ge=0, le=100)
    risk_level: Optional[RiskLevel] = None
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
    vendor_id: str = Field(..., min_length=1, max_length=100)
    text_content: str = Field(..., min_length=10, max_length=100000)
    document_type: str = Field(..., min_length=1, max_length=50)

class AnalysisResult(BaseModel):
    risk_score: int = Field(..., ge=0, le=100)
    risk_level: RiskLevel
    findings: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)

    @field_validator('findings', 'recommendations')
    @classmethod
    def validate_list_length(cls, v: List[str]) -> List[str]:
        """Limit findings and recommendations to prevent abuse"""
        if len(v) > 50:
            raise ValueError("Too many items in list (max 50)")
        return v
