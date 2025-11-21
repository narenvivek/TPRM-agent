"""
AI Prompt Injection Protection
Detects and prevents prompt injection attacks in user-provided content
"""
from fastapi import HTTPException
from typing import List
import re


class PromptInjectionDetector:
    """
    Detects potential prompt injection attacks in user input
    """

    # Dangerous patterns that indicate prompt injection attempts
    DANGEROUS_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions?",
        r"ignore\s+(all\s+)?above",
        r"disregard\s+(all\s+)?previous",
        r"forget\s+(all\s+)?previous",
        r"you\s+are\s+now",
        r"new\s+instructions?",
        r"system\s*:\s*",
        r"<\|im_start\|>",
        r"<\|im_end\|>",
        r"###\s*instruction",
        r"ENDOFINPUT",
        r"roleplay\s+as",
        r"pretend\s+(you\s+are|to\s+be)",
        r"act\s+as\s+(if|though)",
    ]

    # Maximum allowed text length
    MAX_TEXT_LENGTH = 100000  # 100KB

    @classmethod
    def sanitize_text(cls, text: str) -> str:
        """
        Sanitize text for use in AI prompts

        Args:
            text: User-provided text

        Returns:
            Sanitized text

        Raises:
            HTTPException: If dangerous patterns detected or text too long
        """
        if not text:
            raise HTTPException(
                status_code=400,
                detail="Text content cannot be empty"
            )

        # Check length
        if len(text) > cls.MAX_TEXT_LENGTH:
            raise HTTPException(
                status_code=413,
                detail=f"Text too long. Maximum {cls.MAX_TEXT_LENGTH} characters allowed"
            )

        # Check for dangerous patterns (case-insensitive)
        text_lower = text.lower()
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, text_lower):
                raise HTTPException(
                    status_code=400,
                    detail="Document contains suspicious content that may indicate a prompt injection attack"
                )

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    @classmethod
    def validate_findings(cls, findings: List[str]) -> List[str]:
        """
        Validate AI-generated findings for prompt injection

        Args:
            findings: List of findings from AI

        Returns:
            Validated findings

        Raises:
            HTTPException: If suspicious content detected
        """
        # Limit number of findings
        if len(findings) > 50:
            findings = findings[:50]

        # Check each finding for suspicious content
        for finding in findings:
            if any(re.search(pattern, finding.lower()) for pattern in cls.DANGEROUS_PATTERNS):
                raise HTTPException(
                    status_code=500,
                    detail="AI response contained suspicious content. Analysis rejected."
                )

        return findings
