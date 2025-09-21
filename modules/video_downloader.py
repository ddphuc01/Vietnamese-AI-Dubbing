import os
import yt_dlp
import shutil
from pathlib import Path
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class VideoDownloader:
    """Module tải video từ URL hoặc xử lý file upload"""

    def __init__(self):
        self.temp_dir = Path(settings.TEMP_DIR)

    def download_from_url(self, url: str, output_filename: str = None) -> str:
        """Tải video từ URL sử dụng yt-dlp

        Args:
            url: URL của video (YouTube, TikTok, etc.)
            output_filename: Tên file output tùy chỉnh

        Returns:
            str: Đường dẫn đến file video đã tải
        """
        try:
            # Cấu hình yt-dlp
            ydl_opts = {
                'outtmpl': str(self.temp_dir / '%(title)s.%(ext)s'),
                'format': 'best[height<=720]',  # Giới hạn chất lượng để nhanh hơn
                'quiet': True,
                'no_warnings': True,
            }

            if output_filename:
                ydl_opts['outtmpl'] = str(self.temp_dir / f"{output_filename}.%(ext)s")

            logger.info(f"Đang tải video từ: {url}")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            logger.info(f"Đã tải video thành công: {filename}")
            return filename

        except Exception as e:
            logger.error(f"Lỗi khi tải video: {str(e)}")
            raise Exception(f"Không thể tải video từ URL: {str(e)}")

    def handle_uploaded_file(self, uploaded_file) -> str:
        """Xử lý file video đã upload

        Args:
            uploaded_file: File object từ Gradio hoặc path

        Returns:
            str: Đường dẫn đến file video
        """
        try:
            # Nếu là file object (từ Gradio)
            if hasattr(uploaded_file, 'name'):
                filename = os.path.basename(uploaded_file.name)
                dest_path = self.temp_dir / filename

                # Copy file
                shutil.copy2(uploaded_file.name, dest_path)
                logger.info(f"Đã xử lý file upload: {dest_path}")
                return str(dest_path)

            # Nếu là string path
            elif isinstance(uploaded_file, str):
                if os.path.exists(uploaded_file):
                    filename = os.path.basename(uploaded_file)
                    dest_path = self.temp_dir / filename
                    shutil.copy2(uploaded_file, dest_path)
                    logger.info(f"Đã copy file: {dest_path}")
                    return str(dest_path)
                else:
                    raise FileNotFoundError(f"File không tồn tại: {uploaded_file}")

            else:
                raise ValueError("Uploaded file phải là path string hoặc file object")

        except Exception as e:
            logger.error(f"Lỗi khi xử lý file upload: {str(e)}")
            raise Exception(f"Không thể xử lý file upload: {str(e)}")

    def get_video_info(self, video_path: str) -> dict:
        """Lấy thông tin cơ bản của video

        Args:
            video_path: Đường dẫn đến file video

        Returns:
            dict: Thông tin video (duration, size, etc.)
        """
        try:
            probe = ffmpeg.probe(video_path)
            video_info = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')
            audio_info = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)

            return {
                'duration': float(probe['format']['duration']),
                'size': int(probe['format']['size']),
                'video_codec': video_info['codec_name'],
                'width': int(video_info['width']),
                'height': int(video_info['height']),
                'audio_codec': audio_info['codec_name'] if audio_info else None
            }

        except Exception as e:
            logger.warning(f"Không thể probe video info: {str(e)}")
            return {'duration': 0, 'size': 0}

    def validate_video(self, video_path: str) -> bool:
        """Validate xem file có phải video hợp lệ không

        Args:
            video_path: Đường dẫn file

        Returns:
            bool: True nếu hợp lệ
        """
        if not os.path.exists(video_path):
            return False

        valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv']
        ext = Path(video_path).suffix.lower()

        return ext in valid_extensions

# Global instance
video_downloader = VideoDownloader()