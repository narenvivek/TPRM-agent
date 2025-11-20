from fastapi import UploadFile, HTTPException
from pypdf import PdfReader
from docx import Document
import io

class DocumentService:
    """Service for parsing different document types"""

    @staticmethod
    async def extract_text(file: UploadFile) -> str:
        """Extract text from uploaded document"""
        try:
            content = await file.read()

            if file.filename.endswith('.pdf'):
                return DocumentService._extract_from_pdf(content)
            elif file.filename.endswith('.docx'):
                return DocumentService._extract_from_docx(content)
            elif file.filename.endswith('.txt'):
                return content.decode('utf-8')
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type. Supported: .pdf, .docx, .txt"
                )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error processing document: {str(e)}"
            )

    @staticmethod
    def _extract_from_pdf(content: bytes) -> str:
        """Extract text from PDF"""
        pdf_file = io.BytesIO(content)
        reader = PdfReader(pdf_file)

        text_parts = []
        for page in reader.pages:
            text_parts.append(page.extract_text())

        return "\n".join(text_parts)

    @staticmethod
    def _extract_from_docx(content: bytes) -> str:
        """Extract text from DOCX"""
        docx_file = io.BytesIO(content)
        doc = Document(docx_file)

        text_parts = []
        for paragraph in doc.paragraphs:
            text_parts.append(paragraph.text)

        return "\n".join(text_parts)
