"""
Video Downloader Service
Xử lý việc tải video từ các nguồn khác nhau (YouTube, URL trực tiếp, file upload)
"""

import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import yt_dlp
from urllib.parse import urlparse

from app.core.config import settings
from app.core.exceptions import VideoProcessingException

logger = logging.getLogger(__name__)


class VideoDownloaderService:
    """Service xử lý việc tải video từ các nguồn khác nhau"""

    def __init__(self):
        self.temp_dir = Path(settings.TEMP_DIR)
        self.temp_dir.mkdir(exist_ok=True)

    async def download_from_youtube(
        self,
        url: str,
        quality: str = "720p",
        output_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Tải video từ YouTube

        Args:
            url: URL của video YouTube
            quality: Chất lượng video (720p, 1080p, etc.)
            output_filename: Tên file tùy chỉnh

        Returns:
            Dict chứa thông tin video đã tải
        """
        try:
            # Cấu hình yt-dlp cho YouTube
            ydl_opts = {
                'outtmpl': str(self.temp_dir / '%(title)s.%(ext)s'),
                'format': f'best[height<={quality.replace("p", "")}]',
                'quiet': False,
                'no_warnings': False,
                'extract_flat': False,
            }

            if output_filename:
                ydl_opts['outtmpl'] = str(self.temp_dir / f"{output_filename}.%(ext)s")

            logger.info(f"Đang tải video từ YouTube: {url}")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            # Lấy thông tin video
            video_info = {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'uploader': info.get('uploader', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'file_path': filename,
                'file_size': os.path.getsize(filename) if os.path.exists(filename) else 0,
                'thumbnail': info.get('thumbnail'),
                'description': info.get('description', '')
            }

            logger.info(f"Đã tải video thành công: {filename}")
            return video_info

        except Exception as e:
            logger.error(f"Lỗi khi tải video từ YouTube: {str(e)}")
            raise VideoProcessingException(f"Không thể tải video từ YouTube: {str(e)}")

    async def download_from_url(
        self,
        url: str,
        output_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Tải video từ URL trực tiếp

        Args:
            url: URL của video
            output_filename: Tên file tùy chỉnh

        Returns:
            Dict chứa thông tin video đã tải
        """
        try:
            # Cấu hình yt-dlp cho URL trực tiếp
            ydl_opts = {
                'outtmpl': str(self.temp_dir / '%(title)s.%(ext)s'),
                'quiet': False,
                'no_warnings': False,
            }

            if output_filename:
                ydl_opts['outtmpl'] = str(self.temp_dir / f"{output_filename}.%(ext)s")

            logger.info(f"Đang tải video từ URL: {url}")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            # Lấy thông tin video
            video_info = {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'file_path': filename,
                'file_size': os.path.getsize(filename) if os.path.exists(filename) else 0,
                'url': url
            }

            logger.info(f"Đã tải video thành công: {filename}")
            return video_info

        except Exception as e:
            logger.error(f"Lỗi khi tải video từ URL: {str(e)}")
            raise VideoProcessingException(f"Không thể tải video từ URL: {str(e)}")

    async def save_uploaded_file(
        self,
        file_content: bytes,
        filename: str,
        original_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Lưu file video đã upload

        Args:
            file_content: Nội dung file
            filename: Tên file để lưu
            original_filename: Tên file gốc

        Returns:
            Dict chứa thông tin file đã lưu
        """
        try:
            file_path = self.temp_dir / filename

            # Lưu file
            with open(file_path, 'wb') as f:
                f.write(file_content)

            # Lấy thông tin file
            file_info = {
                'title': original_filename or filename,
                'file_path': str(file_path),
                'file_size': len(file_content),
                'filename': filename,
                'original_filename': original_filename
            }

            logger.info(f"Đã lưu file upload: {file_path}")
            return file_info

        except Exception as e:
            logger.error(f"Lỗi khi lưu file upload: {str(e)}")
            raise VideoProcessingException(f"Không thể lưu file upload: {str(e)}")

    def get_video_info(self, file_path: str) -> Dict[str, Any]:
        """
        Lấy thông tin video từ file

        Args:
            file_path: Đường dẫn đến file video

        Returns:
            Dict chứa thông tin video
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File không tồn tại: {file_path}")

            # Sử dụng yt-dlp để lấy thông tin
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(file_path, download=False)

            video_info = {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'file_path': file_path,
                'file_size': os.path.getsize(file_path),
                'format': info.get('format', 'Unknown'),
                'resolution': f"{info.get('width', 0)}x{info.get('height', 0)}"
            }

            return video_info

        except Exception as e:
            logger.warning(f"Không thể lấy thông tin video: {str(e)}")
            # Trả về thông tin cơ bản
            return {
                'title': os.path.basename(file_path),
                'duration': 0,
                'file_path': file_path,
                'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                'format': 'Unknown',
                'resolution': 'Unknown'
            }

    def validate_video_file(self, file_path: str) -> bool:
        """
        Validate file video

        Args:
            file_path: Đường dẫn đến file

        Returns:
            True nếu file hợp lệ
        """
        if not os.path.exists(file_path):
            return False

        valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv', '.wmv']
        ext = Path(file_path).suffix.lower()

        return ext in valid_extensions

    def cleanup_temp_files(self, older_than_hours: int = 24):
        """
        Dọn dẹp các file tạm thời cũ

        Args:
            older_than_hours: Xóa file cũ hơn số giờ này
        """
        try:
            import time
            current_time = time.time()

            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > (older_than_hours * 3600):
                        file_path.unlink()
                        logger.info(f"Đã xóa file tạm: {file_path}")

        except Exception as e:
            logger.error(f"Lỗi khi dọn dẹp file tạm: {str(e)}")

    def is_youtube_url(self, url: str) -> bool:
        """Kiểm tra xem URL có phải YouTube không"""
        parsed = urlparse(url)
        return parsed.netloc in ['www.youtube.com', 'youtube.com', 'youtu.be']

    def is_video_url(self, url: str) -> bool:
        """Kiểm tra xem URL có phải video không"""
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(url, download=False)
                return info is not None
        except:
            return False