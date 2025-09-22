"""
Core configuration for Vietnamese AI Dubbing API
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    """Application settings"""

    # API Configuration
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Server Configuration
    SERVER_NAME: str = "Vietnamese AI Dubbing API"
    SERVER_HOST: str = "http://localhost"
    DEBUG: bool = True

    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        """Parse CORS origins from environment variable"""
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    # Database Configuration
    DATABASE_URL: str = "sqlite:///./vietnamese_ai_dubbing.db"

    # AI Service Configuration
    FUNASR_MODEL_PATH: str = "./models/funasr"
    EDGETTS_VOICE: str = "vi-VN-NamMinhNeural"
    TRANSLATION_API_KEY: Optional[str] = None
    TRANSLATION_API_URL: str = "https://api.cognitive.microsofttranslator.com"

    # Video Processing Configuration
    MAX_VIDEO_SIZE_MB: int = 500
    SUPPORTED_VIDEO_FORMATS: List[str] = [".mp4", ".avi", ".mov", ".mkv", ".webm"]
    TEMP_DIR: str = "./temp"
    OUTPUT_DIR: str = "./output"

    # File Upload Configuration
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 500 * 1024 * 1024  # 500MB

    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # External Service URLs
    YOUTUBE_DL_URL: str = "https://www.youtube.com/watch?v="

    class Config:
        """Pydantic configuration"""
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()