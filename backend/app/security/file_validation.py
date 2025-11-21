"""
File upload validation and security
"""
import magic
from fastapi import UploadFile, HTTPException
from pathlib import Path
from typing import Tuple

# Security configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_FILENAME_LENGTH = 255

ALLOWED_MIME_TYPES = {
    'application/pdf': '.pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    'text/plain': '.txt'
}

ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}


class FileValidator:
    """Validates uploaded files for security"""

    @staticmethod
    async def validate_upload(file: UploadFile) -> Tuple[bytes, str]:
        """
        Validate uploaded file for security issues

        Returns:
            Tuple of (file_contents, validated_extension)

        Raises:
            HTTPException if validation fails
        """
        # Validate filename
        if not file.filename or len(file.filename) > MAX_FILENAME_LENGTH:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid filename or filename too long (max {MAX_FILENAME_LENGTH} chars)"
            )

        # Check for path traversal in filename
        if ".." in file.filename or "/" in file.filename or "\\" in file.filename:
            raise HTTPException(
                status_code=400,
                detail="Filename contains invalid characters"
            )

        # Get file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Read file contents
        contents = await file.read()

        # Check file size
        if len(contents) == 0:
            raise HTTPException(status_code=400, detail="File is empty")

        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / 1024 / 1024}MB"
            )

        # Verify MIME type
        try:
            mime = magic.from_buffer(contents, mime=True)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to determine file type: {str(e)}"
            )

        # Validate MIME type is allowed
        if mime not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type detected: {mime}. Allowed types: PDF, DOCX, TXT"
            )

        # Verify extension matches MIME type
        expected_ext = ALLOWED_MIME_TYPES[mime]
        if file_ext != expected_ext:
            raise HTTPException(
                status_code=400,
                detail=f"File extension '{file_ext}' does not match file type '{mime}'"
            )

        # Reset file pointer for subsequent reads
        await file.seek(0)

        return contents, file_ext

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent security issues

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        # Remove path components
        filename = Path(filename).name

        # Remove dangerous characters
        dangerous_chars = ['..', '/', '\\', '<', '>', ':', '"', '|', '?', '*']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')

        # Limit length
        if len(filename) > MAX_FILENAME_LENGTH:
            # Preserve extension
            ext = Path(filename).suffix
            name = Path(filename).stem
            max_name_length = MAX_FILENAME_LENGTH - len(ext)
            filename = name[:max_name_length] + ext

        return filename
