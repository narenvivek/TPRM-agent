import os
import uuid
from abc import ABC, abstractmethod
from fastapi import UploadFile
from typing import Tuple
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class StorageService(ABC):
    """Abstract base class for storage services"""

    @abstractmethod
    async def save_file(self, file: UploadFile, vendor_id: str) -> Tuple[str, str]:
        """
        Save uploaded file and return (file_path, file_url)
        """
        pass

    @abstractmethod
    async def get_file_path(self, file_url: str) -> str:
        """
        Get local file path from URL for reading
        """
        pass

    @abstractmethod
    async def delete_file(self, file_url: str) -> bool:
        """
        Delete file from storage
        """
        pass


class LocalStorageService(StorageService):
    """Local filesystem storage implementation"""

    def __init__(self):
        self.storage_path = os.getenv("STORAGE_PATH", "./uploads")
        self.base_url = os.getenv("BASE_URL", "http://localhost:8000")

        # Create uploads directory if it doesn't exist
        Path(self.storage_path).mkdir(parents=True, exist_ok=True)

    async def save_file(self, file: UploadFile, vendor_id: str) -> Tuple[str, str]:
        """Save file locally and return (file_path, file_url)"""
        # Generate unique filename
        file_ext = Path(file.filename).suffix
        unique_filename = f"{vendor_id}_{uuid.uuid4()}{file_ext}"

        # Create vendor subdirectory
        vendor_dir = Path(self.storage_path) / vendor_id
        vendor_dir.mkdir(parents=True, exist_ok=True)

        # Save file
        file_path = vendor_dir / unique_filename
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)

        # Generate URL
        file_url = f"{self.base_url}/files/{vendor_id}/{unique_filename}"

        return (str(file_path), file_url)

    async def get_file_path(self, file_url: str) -> str:
        """Extract file path from URL"""
        # URL format: http://localhost:8000/files/{vendor_id}/{filename}
        url_parts = file_url.split("/files/")
        if len(url_parts) != 2:
            raise ValueError(f"Invalid file URL: {file_url}")

        relative_path = url_parts[1]
        file_path = Path(self.storage_path) / relative_path

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        return str(file_path)

    async def delete_file(self, file_url: str) -> bool:
        """Delete file from local storage"""
        try:
            file_path = await self.get_file_path(file_url)
            Path(file_path).unlink()
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False


class GCSStorageService(StorageService):
    """Google Cloud Storage implementation (placeholder)"""

    def __init__(self):
        self.bucket_name = os.getenv("GCS_BUCKET_NAME")
        # In a real implementation, initialize GCS client here
        # from google.cloud import storage
        # self.client = storage.Client()
        # self.bucket = self.client.bucket(self.bucket_name)
        raise NotImplementedError("GCS storage not yet implemented")

    async def save_file(self, file: UploadFile, vendor_id: str) -> Tuple[str, str]:
        # Implementation for GCS upload
        pass

    async def get_file_path(self, file_url: str) -> str:
        # For GCS, might download temporarily or return signed URL
        pass

    async def delete_file(self, file_url: str) -> bool:
        # Implementation for GCS deletion
        pass


def get_storage_service() -> StorageService:
    """Factory function to get the appropriate storage service"""
    storage_type = os.getenv("STORAGE_TYPE", "local")

    if storage_type == "local":
        return LocalStorageService()
    elif storage_type == "gcs":
        return GCSStorageService()
    else:
        raise ValueError(f"Unknown storage type: {storage_type}")
