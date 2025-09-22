"""
Main Service - Orchestrator
Kết nối và điều phối tất cả các service modules
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import asyncio
import json
from datetime import datetime

from app.core.config import settings
from app.core.exceptions import VideoProcessingException

# Import tất cả các services
from .video_downloader import VideoDownloaderService
from .audio_separator import AudioSeparatorService
from .speech_recognition import SpeechRecognitionService
from .translation import TranslationService
from .text_to_speech import TextToSpeechService
from .video_synthesis import VideoSynthesisService

logger = logging.getLogger(__name__)


class MainService:
    """
    Main Service - Orchestrator chính cho Vietnamese AI Dubbing
    Điều phối tất cả các service modules để thực hiện quy trình dubbing hoàn chỉnh
    """

    def __init__(self):
        """Khởi tạo MainService với tất cả các service con"""
        self.temp_dir = Path(settings.TEMP_DIR)
        self.output_dir = Path(settings.OUTPUT_DIR)
        self.models_dir = Path(settings.MODELS_DIR)

        # Khởi tạo tất cả services
        self.video_downloader = VideoDownloaderService()
        self.audio_separator = AudioSeparatorService()
        self.speech_recognizer = SpeechRecognitionService()
        self.translator = TranslationService()
        self.tts_service = TextToSpeechService()
        self.video_synthesizer = VideoSynthesisService()

        # Progress callback
        self.progress_callback = None

        logger.info("MainService đã được khởi tạo với tất cả service modules")

    def set_progress_callback(self, callback):
        """Thiết lập callback để báo cáo tiến độ"""
        self.progress_callback = callback

    def _report_progress(self, progress: float, message: str):
        """Báo cáo tiến độ"""
        if self.progress_callback:
            self.progress_callback(progress, message)

    async def process_video_dubbing(
        self,
        video_input: Union[str, bytes],
        translator_method: str = "google",
        voice_name: str = "vi",
        output_name: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Xử lý quy trình dubbing video hoàn chỉnh

        Args:
            video_input: URL YouTube, URL video, hoặc file bytes
            translator_method: Phương pháp dịch (google, azure, aws, local)
            voice_name: Tên voice sử dụng cho TTS
            output_name: Tên file output (optional)
            **kwargs: Các tham số bổ sung

        Returns:
            Dict chứa kết quả xử lý
        """
        start_time = datetime.now()
        temp_files = []

        try:
            self._report_progress(0, "Bắt đầu quá trình dubbing video...")

            # Phase 1: Download/Extract video
            self._report_progress(5, "Đang tải video...")
            video_path = await self._handle_video_input(video_input)
            temp_files.append(video_path)

            # Phase 2: Extract audio từ video
            self._report_progress(15, "Đang tách audio từ video...")
            audio_path = await self.video_synthesizer.extract_audio_from_video(video_path)
            temp_files.append(audio_path)

            # Phase 3: Tách vocals và background music
            self._report_progress(25, "Đang tách vocals và background music...")
            vocals_path, background_path = await self.audio_separator.extract_vocals(audio_path)
            temp_files.extend([vocals_path, background_path])

            # Phase 4: Speech recognition
            self._report_progress(35, "Đang nhận dạng giọng nói...")
            transcript = await self.speech_recognizer.transcribe_audio(vocals_path)
            logger.info(f"Đã transcribe thành công: {len(transcript.get('segments', []))} segments")

            # Phase 5: Translation
            self._report_progress(50, f"Đang dịch {len(transcript.get('segments', []))} segments với method: {translator_method}")
            translated_segments = await self.translator.translate_segments(
                transcript["segments"],
                target_lang="vi",
                method=translator_method
            )
            logger.info(f"Đã dịch thành công {len(translated_segments)} segments")

            # Phase 6: Text to Speech
            self._report_progress(70, f"Đang tạo audio tiếng Việt với voice: {voice_name}")
            viet_audio_path = await self.tts_service.create_audio_from_segments(
                translated_segments,
                voice_name=voice_name,
                engine="edgetts" # Sử dụng engine chất lượng cao hơn
            )
            temp_files.append(viet_audio_path)

            # Phase 7: Tạo subtitle file
            self._report_progress(80, "Đang tạo file subtitle...")
            sub_path = self.video_synthesizer.create_subtitle_file(translated_segments)
            temp_files.append(sub_path)

            # Phase 8: Tổng hợp video cuối cùng
            self._report_progress(90, "Đang tổng hợp video hoàn chỉnh...")
            final_video_path = await self.video_synthesizer.combine_audio_video(
                video_path=video_path,
                audio_path=viet_audio_path,
                subtitle_path=sub_path,
                background_audio_path=background_path,
                background_volume=kwargs.get('background_volume', 0.3),
                voice_volume=kwargs.get('voice_volume', 1.0)
            )

            # Phase 9: Cleanup và hoàn thành
            self._report_progress(95, "Đang dọn dẹp file tạm thời...")
            await self._cleanup_temp_files(temp_files)

            processing_time = (datetime.now() - start_time).total_seconds()

            result = {
                "success": True,
                "output_path": final_video_path,
                "processing_time": processing_time,
                "original_video": video_path,
                "vietnamese_audio": viet_audio_path,
                "subtitle_file": sub_path,
                "background_audio": background_path,
                "transcript": transcript,
                "translated_segments": translated_segments,
                "metadata": {
                    "translator_method": translator_method,
                    "voice_name": voice_name,
                    "output_name": output_name,
                    "created_at": datetime.now().isoformat(),
                    "processing_time_seconds": processing_time
                }
            }

            self._report_progress(100, f"Hoàn thành xử lý video trong {processing_time:.2f} giây")
            logger.info(f"Hoàn thành xử lý: {final_video_path}")

            return result

        except Exception as e:
            logger.error(f"Lỗi trong quá trình xử lý: {str(e)}")
            await self._cleanup_temp_files(temp_files)
            raise VideoProcessingException(f"Quá trình dubbing thất bại: {str(e)}")

    async def _handle_video_input(self, video_input: Union[str, bytes], original_filename: Optional[str] = None) -> str:
        """Xử lý input video từ nhiều nguồn khác nhau bằng cách sử dụng VideoDownloaderService"""
        try:
            if isinstance(video_input, str):
                if self.video_downloader.is_youtube_url(video_input):
                    video_info = await self.video_downloader.download_from_youtube(video_input)
                else:
                    video_info = await self.video_downloader.download_from_url(video_input)
                return video_info['file_path']

            elif isinstance(video_input, bytes):
                import uuid
                filename = f"upload_{uuid.uuid4().hex}.mp4" # Giả sử là mp4, cần cải tiến sau
                video_info = await self.video_downloader.save_uploaded_file(
                    file_content=video_input,
                    filename=filename,
                    original_filename=original_filename
                )
                return video_info['file_path']
            else:
                raise VideoProcessingException("Video input không hợp lệ. Phải là URL (str) hoặc file (bytes).")

        except Exception as e:
            logger.error(f"Lỗi khi xử lý video input: {str(e)}")
            # Re-raise với thông tin chi tiết hơn
            raise VideoProcessingException(f"Không thể xử lý video input: {e}")

    async def _cleanup_temp_files(self, temp_files: List[str]):
        """Dọn dẹp các file tạm thời"""
        try:
            for file_path in temp_files:
                if file_path and os.path.exists(file_path):
                    os.unlink(file_path)
                    logger.debug(f"Đã xóa file tạm: {file_path}")
        except Exception as e:
            logger.warning(f"Lỗi khi dọn dẹp file tạm: {str(e)}")

    async def get_service_status(self) -> Dict[str, Any]:
        """Lấy trạng thái của tất cả services"""
        return {
            "video_downloader": await self._check_service_status(self.video_downloader, "VideoDownloaderService"),
            "audio_separator": await self._check_service_status(self.audio_separator, "AudioSeparatorService"),
            "speech_recognition": await self._check_service_status(self.speech_recognizer, "SpeechRecognitionService"),
            "translation": await self._check_service_status(self.translator, "TranslationService"),
            "text_to_speech": await self._check_service_status(self.tts_service, "TextToSpeechService"),
            "video_synthesis": await self._check_service_status(self.video_synthesizer, "VideoSynthesisService"),
            "overall_status": "ready" if all([
                (await self._check_service_status(self.video_downloader, "VideoDownloaderService"))["available"],
                (await self._check_service_status(self.audio_separator, "AudioSeparatorService"))["available"],
                (await self._check_service_status(self.speech_recognizer, "SpeechRecognitionService"))["available"],
                (await self._check_service_status(self.translator, "TranslationService"))["available"],
                (await self._check_service_status(self.tts_service, "TextToSpeechService"))["available"],
                (await self._check_service_status(self.video_synthesizer, "VideoSynthesisService"))["available"]
            ]) else "partial"
        }

    async def _check_service_status(self, service, service_name: str) -> Dict[str, Any]:
        """Kiểm tra trạng thái của một service cụ thể"""
        try:
            # Kiểm tra các method cơ bản
            basic_methods = ["validate_audio_file", "validate_video_file", "get_supported_languages", "get_supported_voices"]

            available_methods = []
            for method_name in basic_methods:
                if hasattr(service, method_name):
                    available_methods.append(method_name)

            # Kiểm tra availability đặc biệt cho từng service
            if hasattr(service, 'check_model_availability'):
                model_available = await service.check_model_availability()
            elif hasattr(service, 'check_engine_availability'):
                model_available = await service.check_engine_availability()
            elif hasattr(service, 'check_service_availability'):
                model_available = await service.check_service_availability()
            elif hasattr(service, 'check_ffmpeg_availability'):
                model_available = await service.check_ffmpeg_availability()
            else:
                model_available = True

            return {
                "service": service_name,
                "available": model_available,
                "methods": available_methods,
                "status": "ready" if model_available else "unavailable"
            }

        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra trạng thái {service_name}: {str(e)}")
            return {
                "service": service_name,
                "available": False,
                "methods": [],
                "status": "error",
                "error": str(e)
            }

    def get_processing_options(self) -> Dict[str, Any]:
        """Lấy tất cả options cho quá trình xử lý"""
        return {
            "video_downloader": {
                "supported_sources": ["youtube", "url", "file_upload"],
                "quality_options": ["360p", "480p", "720p", "1080p", "best"],
                "format_options": ["mp4", "webm", "avi"]
            },
            "audio_separator": {
                "models": self.audio_separator.get_supported_models(),
                "model_info": {model: self.audio_separator.get_model_info(model) for model in self.audio_separator.get_supported_models()}
            },
            "speech_recognition": {
                "models": self.speech_recognizer.get_supported_models(),
                "languages": self.speech_recognizer.get_supported_languages()
            },
            "translation": {
                "methods": list(self.translator.get_supported_methods().keys()),
                "languages": self.translator.get_supported_languages(),
                "method_info": self.translator.get_supported_methods()
            },
            "text_to_speech": {
                "engines": list(self.tts_service.get_supported_engines().keys()),
                "voices": self.tts_service.get_supported_voices("edgetts"),
                "engine_info": self.tts_service.get_supported_engines()
            },
            "video_synthesis": {
                "subtitle_formats": self.video_synthesizer.get_supported_subtitle_formats(),
                "audio_formats": self.video_synthesizer.get_supported_audio_formats(),
                "processing_options": self.video_synthesizer.get_video_processing_options()
            }
        }

    def get_system_info(self) -> Dict[str, Any]:
        """Lấy thông tin hệ thống"""
        return {
            "temp_dir": str(self.temp_dir),
            "output_dir": str(self.output_dir),
            "models_dir": str(self.models_dir),
            "temp_dir_size": self._get_directory_size(self.temp_dir),
            "output_dir_size": self._get_directory_size(self.output_dir),
            "models_dir_size": self._get_directory_size(self.models_dir),
            "disk_usage": self._get_disk_usage()
        }

    def _get_directory_size(self, path: Path) -> int:
        """Lấy kích thước thư mục"""
        try:
            return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        except Exception:
            return 0

    def _get_disk_usage(self) -> Dict[str, Any]:
        """Lấy thông tin sử dụng disk"""
        try:
            import shutil
            usage = shutil.disk_usage(self.temp_dir)
            return {
                "total": usage.total,
                "used": usage.used,
                "free": usage.free,
                "usage_percent": (usage.used / usage.total) * 100
            }
        except Exception:
            return {"error": "Không thể lấy thông tin disk usage"}

    async def health_check(self) -> Dict[str, Any]:
        """Health check cho toàn bộ hệ thống"""
        try:
            service_status = await self.get_service_status()

            # Kiểm tra thư mục
            dirs_ok = all([
                self.temp_dir.exists(),
                self.output_dir.exists(),
                self.models_dir.exists()
            ])

            # Kiểm tra FFmpeg
            ffmpeg_available = await self.video_synthesizer.check_ffmpeg_availability()

            return {
                "status": "healthy" if (service_status["overall_status"] == "ready" and dirs_ok and ffmpeg_available) else "unhealthy",
                "services": service_status,
                "directories": {
                    "temp_dir": str(self.temp_dir),
                    "output_dir": str(self.output_dir),
                    "models_dir": str(self.models_dir),
                    "all_exist": dirs_ok
                },
                "dependencies": {
                    "ffmpeg": ffmpeg_available
                },
                "system": self.get_system_info(),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Lỗi khi health check: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def export_service_cache(self) -> Dict[str, Any]:
        """Export thông tin cache về tất cả services"""
        try:
            cache_file = self.temp_dir.parent / "app" / "services" / "service_cache.json"
            if cache_file.exists():
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return {"error": "Cache file không tồn tại"}
        except Exception as e:
            return {"error": f"Không thể đọc cache file: {str(e)}"}

    def update_service_cache(self, cache_data: Dict[str, Any]):
        """Cập nhật service cache"""
        try:
            cache_file = self.temp_dir.parent / "app" / "services" / "service_cache.json"
            cache_data["metadata"]["last_updated"] = datetime.now().isoformat()

            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)

            logger.info("Đã cập nhật service cache")
            return {"success": True}
        except Exception as e:
            logger.error(f"Lỗi khi cập nhật cache: {str(e)}")
            return {"success": False, "error": str(e)}