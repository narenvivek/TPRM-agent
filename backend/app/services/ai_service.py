import os
import json
from typing import List, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv
from app.models import AnalysisResult, ComprehensiveAnalysisResult, DecisionType, RiskLevel
from app.security.prompt_injection import PromptInjectionDetector
from datetime import datetime

load_dotenv()

class AIService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
        else:
            print("Warning: Gemini API key not found. AI features will be mocked.")
            self.model = None

    async def analyze_text(self, text: str) -> AnalysisResult:
        # Sanitize input to prevent prompt injection
        text = PromptInjectionDetector.sanitize_text(text)
        if not self.model:
            # Mock Analysis Result
            return AnalysisResult(
                risk_score=75,
                risk_level="High",
                findings=[
                    "Missing SOC2 Type II report",
                    "No penetration test results found for the last 12 months",
                    "Data encryption at rest is not explicitly mentioned"
                ],
                recommendations=[
                    "Request latest SOC2 report",
                    "Schedule a third-party penetration test",
                    "Clarify encryption standards"
                ]
            )

        try:
            prompt = f"""You are a Third-Party Risk Management (TPRM) security analyst. Analyze the following vendor document/text for security and compliance risks.

Document Content:
{text}

Provide a comprehensive risk assessment in the following JSON format:
{{
    "risk_score": <number between 0-100, where 100 is highest risk>,
    "risk_level": "<Low|Medium|High>",
    "findings": [<list of specific security concerns or gaps found>],
    "recommendations": [<list of actionable recommendations to mitigate risks>]
}}

Consider:
- Security certifications (SOC2, ISO 27001, etc.)
- Data protection and encryption practices
- Incident response capabilities
- Compliance with regulations
- Third-party audits and penetration testing
- Access controls and authentication

Respond ONLY with valid JSON, no additional text."""

            response = self.model.generate_content(prompt)
            result_text = response.text.strip()

            # Remove markdown code blocks if present
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()

            # Parse JSON response
            parsed = json.loads(result_text)

            # Validate findings for prompt injection
            findings = PromptInjectionDetector.validate_findings(parsed.get("findings", []))
            recommendations = PromptInjectionDetector.validate_findings(parsed.get("recommendations", []))

            # Validate and construct result
            return AnalysisResult(
                risk_score=min(100, max(0, int(parsed.get("risk_score", 50)))),
                risk_level=parsed.get("risk_level", "Medium"),
                findings=findings,
                recommendations=recommendations
            )

        except Exception as e:
            print(f"Error during AI analysis: {e}")
            # Fallback to mock data on error
            return AnalysisResult(
                risk_score=50,
                risk_level="Medium",
                findings=[f"AI analysis error: {str(e)}"],
                recommendations=["Retry analysis or review document manually"]
            )

    async def analyze_all_documents(
        self,
        vendor_id: str,
        vendor_name: str,
        individual_analyses: List[Dict[str, Any]],
        full_document_texts: List[Dict[str, str]]
    ) -> ComprehensiveAnalysisResult:
        """
        Perform comprehensive cross-document analysis

        Args:
            vendor_id: Vendor identifier
            vendor_name: Vendor name
            individual_analyses: List of individual document analyses
            full_document_texts: List of {filename, text} dicts

        Returns:
            ComprehensiveAnalysisResult with cross-document insights
        """
        import time
        start_time = time.time()

        if not self.model:
            # Mock comprehensive analysis
            return ComprehensiveAnalysisResult(
                vendor_id=vendor_id,
                vendor_name=vendor_name,
                overall_risk_score=65,
                overall_risk_level=RiskLevel.MEDIUM,
                decision=DecisionType.CONDITIONAL,
                decision_justification="Mock analysis pending real AI configuration. Review required for production use.",
                documents_analyzed=len(individual_analyses),
                individual_analyses=individual_analyses,
                consolidated_findings=[
                    "Multiple documents uploaded for review",
                    "Manual review recommended"
                ],
                cross_document_insights=[
                    "Configure Gemini API to enable real analysis"
                ],
                contradictions=[],
                recommendations=[
                    "Add GEMINI_API_KEY to .env file",
                    "Perform manual cross-document review"
                ],
                analysis_date=datetime.now().isoformat(),
                processing_time_seconds=time.time() - start_time
            )

        try:
            # Prepare document summaries for AI
            doc_summaries = []
            for i, analysis in enumerate(individual_analyses):
                doc_summaries.append(f"""
Document {i+1}: {analysis.get('filename', 'Unknown')} (Type: {analysis.get('document_type', 'Unknown')})
- Risk Score: {analysis.get('risk_score', 'N/A')}/100
- Risk Level: {analysis.get('risk_level', 'N/A')}
- Findings: {', '.join(analysis.get('findings', [])[:5])}
- Recommendations: {', '.join(analysis.get('recommendations', [])[:5])}
""")

            # Truncate full texts to avoid token limits (first 2000 chars per document)
            truncated_texts = []
            for doc in full_document_texts:
                truncated_texts.append(f"""
{doc['filename']}:
{doc['text'][:2000]}{'...' if len(doc['text']) > 2000 else ''}
""")

            prompt = f"""You are a senior Third-Party Risk Management (TPRM) analyst performing a comprehensive vendor risk assessment for {vendor_name}.

You have analyzed {len(individual_analyses)} documents individually. Now perform a cross-document synthesis.

# INDIVIDUAL DOCUMENT ANALYSES
{''.join(doc_summaries)}

# SAMPLE DOCUMENT CONTENTS
{''.join(truncated_texts)}

# YOUR TASK
Provide a comprehensive risk assessment that:
1. Identifies contradictions between documents (e.g., SOC2 cert claims vs. pentest findings)
2. Synthesizes findings across all documents
3. Provides cross-document insights
4. Makes a Go/No-Go/Conditional decision with clear justification

# DECISION FRAMEWORK
- Go: Risk score < 40 OR (score < 60 AND all critical risks mitigated)
- Conditional: Score 40-70 with specific remediations required
- No-Go: Score > 70 OR critical unmitigated risks found

Respond ONLY with valid JSON in this exact format:
{{
    "overall_risk_score": <0-100>,
    "overall_risk_level": "<Low|Medium|High>",
    "decision": "<Go|Conditional|No-Go>",
    "decision_justification": "<2-3 sentence justification>",
    "consolidated_findings": [<unique findings across all documents>],
    "cross_document_insights": [<insights from comparing documents>],
    "contradictions": [<any contradictions found between documents>],
    "recommendations": [<prioritized recommendations>]
}}"""

            response = self.model.generate_content(prompt)
            result_text = response.text.strip()

            # Clean markdown
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()

            parsed = json.loads(result_text)

            # Validate and sanitize outputs
            consolidated_findings = PromptInjectionDetector.validate_findings(
                parsed.get("consolidated_findings", [])
            )
            cross_document_insights = PromptInjectionDetector.validate_findings(
                parsed.get("cross_document_insights", [])
            )
            contradictions = PromptInjectionDetector.validate_findings(
                parsed.get("contradictions", [])
            )
            recommendations = PromptInjectionDetector.validate_findings(
                parsed.get("recommendations", [])
            )

            return ComprehensiveAnalysisResult(
                vendor_id=vendor_id,
                vendor_name=vendor_name,
                overall_risk_score=min(100, max(0, int(parsed.get("overall_risk_score", 50)))),
                overall_risk_level=RiskLevel(parsed.get("overall_risk_level", "Medium")),
                decision=DecisionType(parsed.get("decision", "Conditional")),
                decision_justification=parsed.get("decision_justification", "Analysis completed")[:2000],
                documents_analyzed=len(individual_analyses),
                individual_analyses=individual_analyses,
                consolidated_findings=consolidated_findings,
                cross_document_insights=cross_document_insights,
                contradictions=contradictions,
                recommendations=recommendations,
                analysis_date=datetime.now().isoformat(),
                processing_time_seconds=time.time() - start_time
            )

        except Exception as e:
            print(f"Error during comprehensive analysis: {e}")
            # Fallback to aggregated analysis
            avg_risk_score = sum(a.get('risk_score', 50) for a in individual_analyses) // len(individual_analyses) if individual_analyses else 50

            return ComprehensiveAnalysisResult(
                vendor_id=vendor_id,
                vendor_name=vendor_name,
                overall_risk_score=avg_risk_score,
                overall_risk_level=RiskLevel.MEDIUM if avg_risk_score < 70 else RiskLevel.HIGH,
                decision=DecisionType.CONDITIONAL,
                decision_justification=f"AI analysis encountered an error. Aggregated risk score: {avg_risk_score}/100. Manual review recommended.",
                documents_analyzed=len(individual_analyses),
                individual_analyses=individual_analyses,
                consolidated_findings=[f"AI synthesis error: {str(e)}"],
                cross_document_insights=["Manual cross-document review required"],
                contradictions=[],
                recommendations=["Retry comprehensive analysis", "Perform manual document comparison"],
                analysis_date=datetime.now().isoformat(),
                processing_time_seconds=time.time() - start_time
            )
