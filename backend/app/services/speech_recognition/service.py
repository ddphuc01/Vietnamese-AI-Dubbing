"""
Speech Recognition Service
Xử lý việc nhận dạng giọng nói từ audio files
"""

import os
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import asyncio

from app.core.config import settings
from app.core.exceptions import VideoProcessingException
from funasr import AutoModel

logger = logging.getLogger(__name__)


class SpeechRecognitionService:
    """Service xử lý việc nhận dạng giọng nói từ audio"""

    def __init__(self):
        self.temp_dir = Path(settings.TEMP_DIR)
        self.temp_dir.mkdir(exist_ok=True)
        self.models_dir = Path(settings.MODELS_DIR) / "speech_recognition"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        # Khởi tạo model FunASR
        # Sử dụng model hỗ trợ nhận dạng dấu câu, và nhận dạng nhiều người nói (diarization)
        try:
            self.model = AutoModel(
                model="paraformer-zh-streaming-vad-punc-spk",
                model_revision="v2.0.4",
                vad_model="fsmn-vad",
                vad_model_revision="v2.0.4",
                punc_model="ct-punc-c",
                punc_model_revision="v2.0.4",
                spk_model="cam++",
                spk_model_revision="v2.0.2",
                # device="cuda:0" # Uncomment nếu có GPU
            )
            logger.info("FunASR model đã được khởi tạo.")
        except Exception as e:
            logger.error(f"Không thể khởi tạo FunASR model: {e}")
            self.model = None

    async def transcribe_audio(
        self,
        audio_path: str,
        is_multi_speaker: bool = True,
        language: Optional[str] = "auto"
    ) -> Dict[str, Any]:
        """
        Transcribe audio thành text sử dụng FunASR.

        Args:
            audio_path: Đường dẫn đến file audio.
            is_multi_speaker: Bật/tắt nhận dạng nhiều người nói.
            language: Ngôn ngữ (FunASR hỗ trợ auto-detection).

        Returns:
            Dict chứa kết quả transcription.
        """
        try:
            if not self.model:
                raise VideoProcessingException("FunASR model không được khởi tạo thành công.")
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file không tồn tại: {audio_path}")

            logger.info(f"Bắt đầu transcribe audio: {audio_path} với FunASR")

            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None, self.model.generate, audio_path, {"hotword": "AI, Gemini"}
            )

            return self._format_funasr_result(result, audio_path)

        except Exception as e:
            logger.error(f"Lỗi khi transcribe audio với FunASR: {str(e)}")
            raise VideoProcessingException(f"Không thể transcribe audio: {str(e)}")

    def _format_funasr_result(self, funasr_result: list, audio_path: str) -> Dict[str, Any]:
        """
        Chuyển đổi kết quả từ FunASR sang format chuẩn.
        """
        if not funasr_result or not funasr_result[0].get('value'):
            logger.warning("FunASR không trả về kết quả hoặc kết quả rỗng.")
            return {
                "text": "", "segments": [], "language": "unknown",
                "model": "funasr", "success": True
            }

        # FunASR trả về kết quả trong list, phần tử đầu tiên chứa thông tin chính
        data = funasr_result[0]
        full_text = data.get('value', '')
        segments_raw = data.get('sentence_info', [])

        segments = []
        all_speakers = set()

        for i, seg in enumerate(segments_raw):
            speaker_id = seg.get('spk', 1)
            speaker_tag = f"SPEAKER_{speaker_id:02d}"
            all_speakers.add(speaker_tag)

            segments.append({
                "id": i,
                "start": seg['start'] / 1000.0,
                "end": seg['end'] / 1000.0,
                "text": seg['text'].strip(),
                "speaker": speaker_tag
            })

        formatted_result = {
            "text": full_text.strip(),
            "segments": segments,
            "language": "multi",
            "model": "funasr/paraformer-zh-streaming-vad-punc-spk",
            "speakers": sorted(list(all_speakers)) if all_speakers else ["SPEAKER_01"],
            "success": True
        }
        
        logger.info(f"Đã transcribe thành công: {len(segments)} segments, {len(all_speakers)} speakers.")
        return formatted_result




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
            import subprocess
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

        valid_extensions = ['.wav', '.mp3', '.flac', '.aac', '.ogg', '.m4a', '.wma']
        ext = Path(audio_path).suffix.lower()

        return ext in valid_extensions

    def get_supported_models(self) -> Dict[str, List[str]]:
        """Lấy danh sách models được hỗ trợ."""
        return {
            "funasr": ["paraformer-zh-streaming-vad-punc-spk"]
        }

    def get_supported_languages(self) -> List[str]:
        """Lấy danh sách ngôn ngữ được hỗ trợ. FunASR hỗ trợ auto-detection."""
        # Danh sách này chỉ là ví dụ, FunASR hỗ trợ nhiều ngôn ngữ hơn.
        return ["auto", "en", "zh", "ja", "ko", "vi", "ru", "de", "fr"]

    async def check_model_availability(self, model_name: str = "funasr") -> bool:
        """Kiểm tra model có sẵn không."""
        return self.model is not None

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
                        logger.info(f"Đã xóa file tạm speech recognition: {file_path}")

            # Dọn dẹp trong models_dir
            for file_path in self.models_dir.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > (older_than_hours * 3600):
                        file_path.unlink()
                        logger.info(f"Đã xóa model file cũ: {file_path}")

        except Exception as e:
            logger.error(f"Lỗi khi dọn dẹp file tạm: {str(e)}")