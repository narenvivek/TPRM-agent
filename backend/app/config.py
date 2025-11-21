"""
Application configuration with environment-based settings
"""
import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    """

    # Application
    APP_NAME: str = "TPRM Agent API"
    APP_VERSION: str = "1.1.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")

    # Security
    SECRET_KEY: str = Field(default="change-me-in-production", env="SECRET_KEY")
    ALLOWED_ORIGINS: str = Field(
        default="http://localhost:3000",
        env="ALLOWED_ORIGINS",
        description="Comma-separated list of allowed CORS origins"
    )

    # Storage
    STORAGE_PATH: str = Field(default="./uploads", env="STORAGE_PATH")
    STORAGE_TYPE: str = Field(default="local", env="STORAGE_TYPE")
    MAX_FILE_SIZE: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB

    # Airtable
    AIRTABLE_API_KEY: str = Field(default="", env="AIRTABLE_API_KEY")
    AIRTABLE_BASE_ID: str = Field(default="", env="AIRTABLE_BASE_ID")

    # Google Gemini AI
    GEMINI_API_KEY: str = Field(default="", env="GEMINI_API_KEY")

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")

    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    AUDIT_LOG_ENABLED: bool = Field(default=True, env="AUDIT_LOG_ENABLED")

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT == "production"

    @property
    def cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
