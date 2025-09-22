"""
Custom exceptions for Vietnamese AI Dubbing API
"""

from typing import Any, Dict, Optional


class BaseAPIException(Exception):
    """Base exception for API errors"""

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        detail: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
        self.headers = headers
        super().__init__(self.message)


class ValidationException(BaseAPIException):
    """Exception raised for validation errors"""

    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(message, status_code=422, detail=detail)


class NotFoundException(BaseAPIException):
    """Exception raised when resource is not found"""

    def __init__(self, message: str = "Resource not found", detail: Optional[str] = None):
        super().__init__(message, status_code=404, detail=detail)


class ConflictException(BaseAPIException):
    """Exception raised for conflict errors"""

    def __init__(self, message: str = "Resource conflict", detail: Optional[str] = None):
        super().__init__(message, status_code=409, detail=detail)


class UnauthorizedException(BaseAPIException):
    """Exception raised for unauthorized access"""

    def __init__(self, message: str = "Unauthorized", detail: Optional[str] = None):
        super().__init__(message, status_code=401, detail=detail)


class ForbiddenException(BaseAPIException):
    """Exception raised for forbidden access"""

    def __init__(self, message: str = "Forbidden", detail: Optional[str] = None):
        super().__init__(message, status_code=403, detail=detail)


class VideoProcessingException(BaseAPIException):
    """Exception raised for video processing errors"""

    def __init__(self, message: str = "Video processing failed", detail: Optional[str] = None):
        super().__init__(message, status_code=500, detail=detail)


class AudioProcessingException(BaseAPIException):
    """Exception raised for audio processing errors"""

    def __init__(self, message: str = "Audio processing failed", detail: Optional[str] = None):
        super().__init__(message, status_code=500, detail=detail)


class TranslationException(BaseAPIException):
    """Exception raised for translation service errors"""

    def __init__(self, message: str = "Translation service error", detail: Optional[str] = None):
        super().__init__(message, status_code=500, detail=detail)


class SpeechRecognitionException(BaseAPIException):
    """Exception raised for speech recognition errors"""

    def __init__(self, message: str = "Speech recognition failed", detail: Optional[str] = None):
        super().__init__(message, status_code=500, detail=detail)


class TextToSpeechException(BaseAPIException):
    """Exception raised for text-to-speech errors"""

    def __init__(self, message: str = "Text-to-speech conversion failed", detail: Optional[str] = None):
        super().__init__(message, status_code=500, detail=detail)


class FileUploadException(BaseAPIException):
    """Exception raised for file upload errors"""

    def __init__(self, message: str = "File upload failed", detail: Optional[str] = None):
        super().__init__(message, status_code=400, detail=detail)


class VideoDownloadException(BaseAPIException):
    """Exception raised for video download errors"""

    def __init__(self, message: str = "Video download failed", detail: Optional[str] = None):
        super().__init__(message, status_code=500, detail=detail)