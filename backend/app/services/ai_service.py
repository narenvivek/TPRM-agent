import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
from app.models import AnalysisResult
from app.security.prompt_injection import PromptInjectionDetector

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
