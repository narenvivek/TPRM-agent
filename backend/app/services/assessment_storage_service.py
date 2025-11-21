"""
Service for storing and retrieving comprehensive assessment results as JSON files
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models import ComprehensiveAnalysisResult


class AssessmentStorageService:
    """Store comprehensive assessments as JSON files organized by vendor"""

    def __init__(self, storage_path: str = "./assessments"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _get_vendor_dir(self, vendor_id: str) -> Path:
        """Get or create directory for vendor's assessments"""
        vendor_dir = self.storage_path / vendor_id
        vendor_dir.mkdir(parents=True, exist_ok=True)
        return vendor_dir

    def _generate_filename(self, analysis_date: str) -> str:
        """Generate filename from analysis date (ISO format -> filesystem safe)"""
        # Convert ISO timestamp to filename: 2025-11-21T12:30:00.123 -> 2025-11-21_12-30-00
        try:
            dt = datetime.fromisoformat(analysis_date)
            return dt.strftime("%Y-%m-%d_%H-%M-%S.json")
        except:
            # Fallback to timestamp
            return f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"

    def save_assessment(self, assessment: ComprehensiveAnalysisResult) -> str:
        """
        Save comprehensive assessment as JSON file

        Returns:
            Full path to saved file
        """
        vendor_dir = self._get_vendor_dir(assessment.vendor_id)
        filename = self._generate_filename(assessment.analysis_date)
        file_path = vendor_dir / filename

        # Convert Pydantic model to dict for JSON serialization
        assessment_dict = assessment.dict()

        # Convert enums to strings
        assessment_dict['overall_risk_level'] = assessment.overall_risk_level.value
        assessment_dict['decision'] = assessment.decision.value

        # Write to file with pretty formatting
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(assessment_dict, f, indent=2, ensure_ascii=False)

        print(f"✓ Saved comprehensive assessment to: {file_path}")
        return str(file_path)

    def get_latest_assessment(self, vendor_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the most recent assessment for a vendor

        Returns:
            Assessment dict or None if no assessments found
        """
        vendor_dir = self._get_vendor_dir(vendor_id)

        # Get all JSON files sorted by modification time (newest first)
        json_files = sorted(
            vendor_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        if not json_files:
            return None

        # Read the most recent file
        with open(json_files[0], 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_all_assessments(self, vendor_id: str) -> List[Dict[str, Any]]:
        """
        Get all assessments for a vendor, sorted by date (newest first)

        Returns:
            List of assessment dicts
        """
        vendor_dir = self._get_vendor_dir(vendor_id)

        # Get all JSON files sorted by modification time (newest first)
        json_files = sorted(
            vendor_dir.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        assessments = []
        for file_path in json_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    assessment = json.load(f)
                    assessment['file_path'] = str(file_path)
                    assessments.append(assessment)
            except Exception as e:
                print(f"Error reading assessment file {file_path}: {e}")
                continue

        return assessments

    def delete_assessment(self, vendor_id: str, filename: str) -> bool:
        """
        Delete a specific assessment file

        Returns:
            True if deleted successfully, False otherwise
        """
        vendor_dir = self._get_vendor_dir(vendor_id)
        file_path = vendor_dir / filename

        try:
            if file_path.exists():
                file_path.unlink()
                print(f"✓ Deleted assessment: {file_path}")
                return True
            return False
        except Exception as e:
            print(f"Error deleting assessment {file_path}: {e}")
            return False

    def get_assessment_summary(self, vendor_id: str) -> Dict[str, Any]:
        """
        Get summary of all assessments for a vendor

        Returns:
            Summary dict with count, latest decision, risk trend, etc.
        """
        assessments = self.get_all_assessments(vendor_id)

        if not assessments:
            return {
                "vendor_id": vendor_id,
                "total_assessments": 0,
                "latest_assessment": None,
                "risk_trend": None
            }

        # Calculate risk trend (compare latest to oldest)
        latest = assessments[0]
        oldest = assessments[-1]

        risk_trend = None
        if len(assessments) > 1:
            risk_diff = latest['overall_risk_score'] - oldest['overall_risk_score']
            if risk_diff > 10:
                risk_trend = "increasing"
            elif risk_diff < -10:
                risk_trend = "decreasing"
            else:
                risk_trend = "stable"

        return {
            "vendor_id": vendor_id,
            "total_assessments": len(assessments),
            "latest_assessment": {
                "date": latest['analysis_date'],
                "risk_score": latest['overall_risk_score'],
                "risk_level": latest['overall_risk_level'],
                "decision": latest['decision']
            },
            "risk_trend": risk_trend,
            "assessment_dates": [a['analysis_date'] for a in assessments]
        }
