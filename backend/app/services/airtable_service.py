import os
from pyairtable import Api
from dotenv import load_dotenv
from typing import List, Dict, Any

load_dotenv()

class AirtableService:
    def __init__(self):
        self.api_key = os.getenv("AIRTABLE_API_KEY")
        self.base_id = os.getenv("AIRTABLE_BASE_ID")
        if self.api_key and self.base_id:
            self.api = Api(self.api_key)
            self.table = self.api.table(self.base_id, "Vendors")
        else:
            print("Warning: Airtable credentials not found. Running in mock mode.")
            self.api = None
            self.table = None

    def _map_record_to_vendor(self, record: Dict[str, Any]) -> Dict[str, Any]:
        fields = record.get("fields", {})
        return {
            "id": record.get("id"),
            "name": fields.get("Name", "Unknown Vendor"),
            "website": fields.get("Website"),
            "description": fields.get("Description"),
            "criticality": fields.get("Criticality", "Low"),
            "spend": fields.get("Spend", 0.0),
            "data_sensitivity": fields.get("Data Sensitivity", "Public"),
            "risk_score": fields.get("Risk Score"),
            "risk_level": fields.get("Risk Level"),
            "last_assessed": fields.get("Last Assessed")
        }

    def get_vendors(self) -> List[Dict[str, Any]]:
        if not self.table:
            # Mock Data
            return [
                {
                    "id": "recMock1",
                    "name": "Cloudflare",
                    "website": "https://cloudflare.com",
                    "description": "CDN and Security services",
                    "criticality": "High",
                    "spend": 12000.0,
                    "data_sensitivity": "Confidential",
                    "risk_score": 15,
                    "risk_level": "Low",
                    "last_assessed": "2023-10-01"
                },
                {
                    "id": "recMock2",
                    "name": "Unknown SaaS",
                    "website": "https://unknown-saas.com",
                    "description": "Marketing tool",
                    "criticality": "Medium",
                    "spend": 5000.0,
                    "data_sensitivity": "Internal",
                    "risk_score": 85,
                    "risk_level": "High",
                    "last_assessed": "2023-11-15"
                }
            ]
        
        records = self.table.all()
        return [self._map_record_to_vendor(r) for r in records]

    def create_vendor(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Map model fields back to Airtable fields
        airtable_fields = {
            "Name": data.get("name"),
            "Website": data.get("website"),
            "Description": data.get("description"),
            "Criticality": data.get("criticality"),
            "Spend": data.get("spend"),
            "Data Sensitivity": data.get("data_sensitivity")
        }
        
        if not self.table:
            return {
                "id": "recNewMock",
                **data,
                "risk_score": None,
                "risk_level": None,
                "last_assessed": None
            }
            
        try:
            # typecast=True allows creating new options if permissions allow, 
            # but we catch errors if they don't.
            record = self.table.create(airtable_fields, typecast=True)
            return self._map_record_to_vendor(record)
        except Exception as e:
            print(f"Error creating record: {e}")
            # Raise HTTP 400 so the frontend receives a proper error response
            # and CORS headers are preserved.
            from fastapi import HTTPException
            raise HTTPException(status_code=400, detail=f"Airtable Error: {str(e)}")
