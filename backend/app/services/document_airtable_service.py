import os
import json
from pyairtable import Api
from dotenv import load_dotenv
from typing import List, Dict, Any
from datetime import datetime

load_dotenv()

class DocumentAirtableService:
    """Service for managing documents in Airtable"""

    def __init__(self):
        self.api_key = os.getenv("AIRTABLE_API_KEY")
        self.base_id = os.getenv("AIRTABLE_BASE_ID")

        if self.api_key and self.base_id:
            self.api = Api(self.api_key)
            try:
                self.table = self.api.table(self.base_id, "Documents")
            except Exception as e:
                print(f"Warning: Documents table not found in Airtable: {e}")
                print("Using mock mode for documents. Create a 'Documents' table in Airtable with fields:")
                print("  - Filename (Single line text)")
                print("  - Vendor (Link to Vendors table)")
                print("  - File Type (Single select: pdf, docx, txt)")
                print("  - Document Type (Single line text)")
                print("  - File Size (Number)")
                print("  - File URL (URL)")
                print("  - Upload Date (Date)")
                print("  - Analysis Status (Single select: Not Analyzed, Analyzing, Completed)")
                print("  - Risk Score (Number)")
                print("  - Risk Level (Single select: Low, Medium, High)")
                print("  - Findings (Long text)")
                print("  - Recommendations (Long text)")
                self.table = None
        else:
            print("Warning: Airtable credentials not found. Running in mock mode.")
            self.api = None
            self.table = None

    def _map_record_to_document(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Map Airtable record to Document model"""
        fields = record.get("fields", {})

        # Parse JSON fields if they exist
        findings = None
        recommendations = None
        if fields.get("Findings"):
            try:
                findings = json.loads(fields["Findings"])
            except:
                findings = [fields["Findings"]]  # Treat as single finding

        if fields.get("Recommendations"):
            try:
                recommendations = json.loads(fields["Recommendations"])
            except:
                recommendations = [fields["Recommendations"]]  # Treat as single recommendation

        # Extract vendor ID from linked record
        vendor_id = None
        if fields.get("Vendor"):
            vendor_id = fields["Vendor"][0] if isinstance(fields["Vendor"], list) else fields["Vendor"]

        return {
            "id": record.get("id"),
            "vendor_id": vendor_id,
            "filename": fields.get("Filename", "Unknown"),
            "file_type": fields.get("File Type", "unknown"),
            "document_type": fields.get("Document Type", "General"),
            "file_size": fields.get("File Size", 0),
            "file_url": fields.get("File URL", ""),
            "upload_date": fields.get("Upload Date", datetime.now().isoformat()),
            "analysis_status": fields.get("Analysis Status", "Not Analyzed"),
            "risk_score": fields.get("Risk Score"),
            "risk_level": fields.get("Risk Level"),
            "findings": findings,
            "recommendations": recommendations
        }

    def create_document(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new document record in Airtable"""
        if not self.table:
            # Return mock data
            return {
                "id": f"recMockDoc{hash(document_data['filename']) % 10000}",
                **document_data,
                "upload_date": datetime.now().isoformat(),
                "analysis_status": "Not Analyzed"
            }

        # Map to Airtable field names
        airtable_fields = {
            "Filename": document_data.get("filename"),
            "Vendor": [document_data.get("vendor_id")],  # Link to vendor
            "File Type": document_data.get("file_type"),
            "Document Type": document_data.get("document_type"),
            "File Size": document_data.get("file_size"),
            "File URL": document_data.get("file_url"),
            "Upload Date": datetime.now().strftime("%Y-%m-%d"),
            "Analysis Status": "Not Analyzed"
        }

        try:
            record = self.table.create(airtable_fields, typecast=True)
            return self._map_record_to_document(record)
        except Exception as e:
            print(f"Error creating document record: {e}")
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=f"Airtable Error: {str(e)}")

    def get_vendor_documents(self, vendor_id: str) -> List[Dict[str, Any]]:
        """Get all documents for a vendor"""
        if not self.table:
            # Return mock data
            return []

        try:
            # Fallback approach: get all and filter in Python (most reliable)
            all_records = self.table.all()
            filtered = []
            for r in all_records:
                vendor_links = r.get('fields', {}).get('Vendor', [])
                # vendor_links is a list of vendor IDs
                if isinstance(vendor_links, list) and vendor_id in vendor_links:
                    filtered.append(self._map_record_to_document(r))
            print(f"Found {len(filtered)} documents for vendor {vendor_id}")
            return filtered
        except Exception as e:
            print(f"Error fetching documents: {e}")
            import traceback
            traceback.print_exc()
            return []

    def get_document(self, document_id: str) -> Dict[str, Any]:
        """Get a single document by ID"""
        if not self.table:
            return None

        try:
            record = self.table.get(document_id)
            return self._map_record_to_document(record)
        except Exception as e:
            print(f"Error fetching document: {e}")
            return None

    def update_document_analysis(self, document_id: str, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """Update document with analysis results"""
        if not self.table:
            # Return mock update
            return {
                "id": document_id,
                "analysis_status": "Completed",
                **analysis_result
            }

        try:
            update_fields = {
                "Analysis Status": "Completed",
                "Risk Score": analysis_result.get("risk_score"),
                "Risk Level": analysis_result.get("risk_level"),
                "Findings": json.dumps(analysis_result.get("findings", [])),
                "Recommendations": json.dumps(analysis_result.get("recommendations", []))
            }

            record = self.table.update(document_id, update_fields)
            return self._map_record_to_document(record)
        except Exception as e:
            print(f"Error updating document: {e}")
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=f"Airtable Error: {str(e)}")
