"""
File handling utilities for Vietnamese AI Dubbing API
"""

import os
import shutil
import uuid
from pathlib import Path
from typing import Optional, Tuple
import logging

from app.core.config import settings
from app.core.exceptions import FileUploadException

logger = logging.getLogger(__name__)


class FileHandler:
    """Utility class for handling file operations"""

    def __init__(self):
        """Initialize file handler"""
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.temp_dir = Path(settings.TEMP_DIR)
        self.output_dir = Path(settings.OUTPUT_DIR)

        # Create directories if they don't exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_upload_file(self, file_content: bytes, filename: str) -> str:
        """Save uploaded file to upload directory"""
        try:
            # Generate unique filename
            file_extension = Path(filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = self.upload_dir / unique_filename

            # Save file
            with open(file_path, "wb") as f:
                f.write(file_content)

            logger.info(f"File saved: {file_path}")
            return str(file_path)

        except Exception as e:
            logger.error(f"Failed to save upload file: {e}")
            raise FileUploadException(f"Failed to save file: {str(e)}")

    def move_to_temp(self, file_path: str) -> str:
        """Move file to temp directory for processing"""
        try:
            source_path = Path(file_path)
            temp_filename = f"{uuid.uuid4()}{source_path.suffix}"
            temp_path = self.temp_dir / temp_filename

            shutil.move(str(source_path), str(temp_path))
            logger.info(f"File moved to temp: {temp_path}")
            return str(temp_path)

        except Exception as e:
            logger.error(f"Failed to move file to temp: {e}")
            raise FileUploadException(f"Failed to move file to temp: {str(e)}")

    def move_to_output(self, file_path: str, job_id: str) -> str:
        """Move processed file to output directory"""
        try:
            source_path = Path(file_path)
            output_filename = f"processed_{job_id}{source_path.suffix}"
            output_path = self.output_dir / output_filename

            shutil.move(str(source_path), str(output_path))
            logger.info(f"File moved to output: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to move file to output: {e}")
            raise FileUploadException(f"Failed to move file to output: {str(e)}")

    def cleanup_temp_files(self, job_id: str) -> None:
        """Clean up temporary files for a job"""
        try:
            # Clean up temp directory
            for file_path in self.temp_dir.glob(f"*{job_id}*"):
                if file_path.is_file():
                    file_path.unlink()
                    logger.info(f"Cleaned up temp file: {file_path}")

            # Clean up upload directory
            for file_path in self.upload_dir.glob(f"*{job_id}*"):
                if file_path.is_file():
                    file_path.unlink()
                    logger.info(f"Cleaned up upload file: {file_path}")

        except Exception as e:
            logger.error(f"Failed to cleanup temp files: {e}")

    def get_file_size(self, file_path: str) -> int:
        """Get file size in bytes"""
        try:
            return Path(file_path).stat().st_size
        except Exception as e:
            logger.error(f"Failed to get file size: {e}")
            return 0

    def validate_video_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """Validate video file format and integrity"""
        try:
            path = Path(file_path)

            # Check if file exists
            if not path.exists():
                return False, "File does not exist"

            # Check file extension
            file_extension = path.suffix.lower()
            if file_extension not in settings.SUPPORTED_VIDEO_FORMATS:
                return False, f"Unsupported format. Supported: {', '.join(settings.SUPPORTED_VIDEO_FORMATS)}"

            # Check file size
            file_size = self.get_file_size(file_path)
            max_size_bytes = settings.MAX_FILE_SIZE

            if file_size > max_size_bytes:
                return False, f"File too large. Max size: {max_size_bytes / (1024*1024)".0f"}MB"

            # Additional validation could include:
            # - Check video duration
            # - Check video resolution
            # - Check if file is actually a video (using ffprobe)

            return True, None

        except Exception as e:
            logger.error(f"Failed to validate video file: {e}")
            return False, f"Validation failed: {str(e)}"

    def get_mime_type(self, file_path: str) -> str:
        """Get MIME type of file"""
        try:
            import mimetypes
            mime_type, _ = mimetypes.guess_type(file_path)
            return mime_type or "application/octet-stream"
        except Exception as e:
            logger.error(f"Failed to get MIME type: {e}")
            return "application/octet-stream"