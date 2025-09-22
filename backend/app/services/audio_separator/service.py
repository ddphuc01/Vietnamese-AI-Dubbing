"""
Audio Separator Service
Xử lý việc tách audio thành vocals và background music
"""

import os
import logging
from typing import Dict, Any, Tuple, Optional
from pathlib import Path
import subprocess
import asyncio

from app.core.config import settings
from app.core.exceptions import VideoProcessingException

logger = logging.getLogger(__name__)


class AudioSeparatorService:
    """Service xử lý việc tách audio thành vocals và background music"""

    def __init__(self):
        self.temp_dir = Path(settings.TEMP_DIR)
        self.temp_dir.mkdir(exist_ok=True)
        self.models_dir = Path(settings.MODELS_DIR) / "audio_separator"
        self.models_dir.mkdir(parents=True, exist_ok=True)

    async def extract_vocals(
        self,
        audio_path: str,
        output_dir: Optional[str] = None,
        model: str = "htdemucs_ft"
    ) -> Tuple[str, str]:
        """
        Tách audio thành vocals và background music

        Args:
            audio_path: Đường dẫn đến file audio
            output_dir: Thư mục output (nếu None thì dùng temp_dir)
            model: Model sử dụng cho việc tách

        Returns:
            Tuple[str, str]: (vocals_path, background_path)
        """
        try:
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file không tồn tại: {audio_path}")

            output_dir = Path(output_dir) if output_dir else self.temp_dir
            output_dir.mkdir(exist_ok=True)

            # Tạo tên file output
            audio_filename = Path(audio_path).stem
            vocals_path = str(output_dir / f"{audio_filename}_vocals.wav")
            background_path = str(output_dir / f"{audio_filename}_background.wav")

            logger.info(f"Bắt đầu tách audio: {audio_path} với model {model}")

            # Sử dụng API Python của Demucs
            from demucs import separate

            # Tham số cho demucs
            args = [
                "-n", model,
                "--two-stems=vocals",
                "-o", str(output_dir),
                "--filename", "{stem}_{track}.{ext}",
                str(audio_path)
            ]

            # Chạy demucs
            separate.main(args)

            # Xác định đường dẫn file output
            vocals_path = str(output_dir / f"{audio_filename}_vocals.wav")
            background_path = str(output_dir / f"{audio_filename}_no_vocals.wav")

            if not os.path.exists(vocals_path) or not os.path.exists(background_path):
                # Kiểm tra xem có file output nào không, nếu không thì báo lỗi
                raise VideoProcessingException(
                    f"Tách audio thất bại. Không tìm thấy file output. "
                    f"Kiểm tra log của demucs để biết chi tiết."
                )

            logger.info(f"Đã tách audio thành công: vocals={vocals_path}, background={background_path}")
            return vocals_path, background_path

        except Exception as e:
            logger.error(f"Lỗi khi tách audio: {str(e)}")
            raise VideoProcessingException(f"Không thể tách audio: {str(e)}")

    async def _create_mock_audio_file(self, file_path: str, duration: int = 10):
        """Tạo mock audio file để test (KHÔNG DÙNG TRONG PRODUCTION)"""
        logger.warning(f"Đang tạo mock audio file: {file_path}. Chỉ dành cho mục đích test.")
        try:
            # Tạo file WAV đơn giản với silence
            import wave
            import struct

            with wave.open(file_path, 'wb') as wav_file:
                # Cấu hình WAV
                wav_file.setnchannels(2)  # Stereo
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(44100)  # 44.1kHz

                # Tạo silence data
                frames = int(44100 * duration)  # Số frames
                silence_data = struct.pack('<' + 'h' * frames * 2, *[0] * frames * 2)

                wav_file.writeframes(silence_data)
                wav_file.setnframes(frames)

            logger.info(f"Đã tạo mock audio file: {file_path}")

        except Exception as e:
            logger.error(f"Lỗi khi tạo mock audio file: {str(e)}")
            # Tạo file rỗng
            with open(file_path, 'wb') as f:
                f.write(b'')

    def get_audio_info(self, audio_path: str) -> Dict[str, Any]:
        """
        Lấy thông tin audio file

        Args:
            audio_path: Đường dẫn đến file audio

        Returns:
            Dict chứa thông tin audio
        """
        try:
            if not os.path.exists(audio_path):
                return {'error': 'File không tồn tại'}

            # Sử dụng ffprobe để lấy thông tin
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                audio_path
            ]

            process = subprocess.run(cmd, capture_output=True, text=True)
            if process.returncode != 0:
                return {'error': 'Không thể đọc thông tin audio'}

            import json
            info = json.loads(process.stdout)

            # Lấy thông tin cơ bản
            audio_info = {
                'duration': float(info['format'].get('duration', 0)),
                'size': int(info['format'].get('size', 0)),
                'bitrate': int(info['format'].get('bit_rate', 0)),
                'format': info['format'].get('format_name', 'Unknown')
            }

            # Lấy thông tin stream
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'audio':
                    audio_info.update({
                        'codec': stream.get('codec_name', 'Unknown'),
                        'sample_rate': int(stream.get('sample_rate', 0)),
                        'channels': int(stream.get('channels', 0)),
                        'channel_layout': stream.get('channel_layout', 'Unknown')
                    })
                    break

            return audio_info

        except Exception as e:
            logger.error(f"Lỗi khi lấy thông tin audio: {str(e)}")
            return {
                'error': str(e),
                'duration': 0,
                'size': os.path.getsize(audio_path) if os.path.exists(audio_path) else 0
            }

    def validate_audio_file(self, audio_path: str) -> bool:
        """
        Validate audio file

        Args:
            audio_path: Đường dẫn đến file audio

        Returns:
            True nếu file hợp lệ
        """
        if not os.path.exists(audio_path):
            return False

        valid_extensions = ['.wav', '.mp3', '.flac', '.aac', '.ogg', '.m4a']
        ext = Path(audio_path).suffix.lower()

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

            # Dọn dẹp trong temp_dir
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > (older_than_hours * 3600):
                        file_path.unlink()
                        logger.info(f"Đã xóa file tạm audio: {file_path}")

            # Dọn dẹp trong models_dir
            for file_path in self.models_dir.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > (older_than_hours * 3600):
                        file_path.unlink()
                        logger.info(f"Đã xóa model file cũ: {file_path}")

        except Exception as e:
            logger.error(f"Lỗi khi dọn dẹp file tạm: {str(e)}")

    async def check_model_availability(self, model: str = "htdemucs_ft") -> bool:
        """
        Kiểm tra model có sẵn không

        Args:
            model: Tên model cần kiểm tra

        Returns:
            True nếu model có sẵn
        """
        try:
            # Kiểm tra xem demucs có cài đặt không
            process = await asyncio.create_subprocess_exec(
                "demucs", "--help",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            return process.returncode == 0

        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra model: {str(e)}")
            return False

    def get_supported_models(self) -> list:
        """Lấy danh sách models được hỗ trợ"""
        return [
            "htdemucs_ft",
            "htdemucs",
            "htdemucs_6s",
            "mdx_extra",
            "mdx_extra_q"
        ]

    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Lấy thông tin về model"""
        model_info = {
            "htdemucs_ft": {
                "name": "HTDemucs FT",
                "description": "Fine-tuned version of HTDemucs",
                "quality": "High",
                "speed": "Medium"
            },
            "htdemucs": {
                "name": "HTDemucs",
                "description": "Hybrid Transformer Demucs",
                "quality": "High",
                "speed": "Medium"
            },
            "htdemucs_6s": {
                "name": "HTDemucs 6s",
                "description": "HTDemucs trained on 6 second clips",
                "quality": "Medium",
                "speed": "Fast"
            }
        }

        return model_info.get(model, {
            "name": model,
            "description": "Unknown model",
            "quality": "Unknown",
            "speed": "Unknown"
        })