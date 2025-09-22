"""
Video Synthesis Service
Xử lý việc tổng hợp video từ các thành phần audio và subtitle
"""

import os
import logging
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import asyncio
import json
import subprocess

from app.core.config import settings
from app.core.exceptions import VideoProcessingException

logger = logging.getLogger(__name__)


class VideoSynthesisService:
    """Service xử lý việc tổng hợp video từ các thành phần"""

    def __init__(self):
        self.temp_dir = Path(settings.TEMP_DIR)
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir = Path(settings.OUTPUT_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    async def combine_audio_video(
        self,
        video_path: str,
        audio_path: str,
        subtitle_path: Optional[str] = None,
        output_path: Optional[str] = None,
        background_audio_path: Optional[str] = None,
        background_volume: float = 0.3,
        voice_volume: float = 1.0
    ) -> Dict[str, Any]:
        """
        Kết hợp video với audio và subtitle

        Args:
            video_path: Đường dẫn đến video gốc
            audio_path: Đường dẫn đến audio tiếng Việt
            subtitle_path: Đường dẫn đến file subtitle (optional)
            output_path: Đường dẫn file output (nếu None thì tạo tự động)
            background_audio_path: Đường dẫn đến background music (optional)
            background_volume: Volume của background music (0.0 - 1.0)
            voice_volume: Volume của voice (0.0 - 1.0)

        Returns:
            Dict chứa thông tin video được tạo
        """
        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file không tồn tại: {video_path}")
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file không tồn tại: {audio_path}")

            logger.info(f"Bắt đầu kết hợp video: {video_path} với audio: {audio_path}")

            # Tạo output path nếu không có
            if not output_path:
                video_name = Path(video_path).stem
                output_path = str(self.output_dir / f"{video_name}_dubbed.mp4")

            # Kết hợp audio và video
            final_video_path = await self._combine_audio_tracks(
                video_path=video_path,
                voice_audio_path=audio_path,
                background_audio_path=background_audio_path,
                output_path=output_path,
                background_volume=background_volume,
                voice_volume=voice_volume
            )

            # Thêm subtitle nếu có
            if subtitle_path and os.path.exists(subtitle_path):
                final_video_path = await self._add_subtitle_to_video(
                    video_path=final_video_path,
                    subtitle_path=subtitle_path,
                    output_path=output_path.replace('.mp4', '_with_subs.mp4')
                )

            # Lấy thông tin video cuối cùng
            video_info = self._get_video_info(final_video_path)

            result = {
                "success": True,
                "output_path": final_video_path,
                "original_video": video_path,
                "vietnamese_audio": audio_path,
                "subtitle_file": subtitle_path,
                "background_audio": background_audio_path,
                "file_size": video_info.get("size", 0),
                "duration": video_info.get("duration", 0),
                "resolution": video_info.get("resolution", "Unknown"),
                "bitrate": video_info.get("bitrate", 0)
            }

            logger.info(f"Đã tạo video hoàn chỉnh: {final_video_path}")
            return result

        except Exception as e:
            logger.error(f"Lỗi khi kết hợp audio video: {str(e)}")
            raise VideoProcessingException(f"Không thể kết hợp audio video: {str(e)}")

    async def _combine_audio_tracks(
        self,
        video_path: str,
        voice_audio_path: str,
        background_audio_path: Optional[str] = None,
        output_path: str = None,
        background_volume: float = 0.3,
        voice_volume: float = 1.0
    ) -> str:
        """Kết hợp nhiều audio track thành một video"""
        try:
            import tempfile

            # Tạo file tạm cho quá trình xử lý
            temp_output = output_path
            if not temp_output:
                temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
                temp_output = temp_file.name
                temp_file.close()

            # Chuẩn bị audio filters cho ffmpeg
            audio_filter = []

            if background_audio_path and os.path.exists(background_audio_path):
                # Có cả voice và background music
                audio_filter = [
                    f"[0:a]volume={voice_volume}[voice]",
                    f"[1:a]volume={background_volume}[bgm]",
                    "[voice][bgm]amix=inputs=2:duration=first[aout]"
                ]
            else:
                # Chỉ có voice
                audio_filter = [f"[0:a]volume={voice_volume}[aout]"]

            # Tạo filter string
            filter_string = ";".join(audio_filter)

            # Chuẩn bị inputs
            inputs = ['-i', video_path, '-i', voice_audio_path]
            if background_audio_path and os.path.exists(background_audio_path):
                inputs.extend(['-i', background_audio_path])

            # Chạy ffmpeg
            cmd = [
                'ffmpeg',
                '-y',  # Overwrite output files
                *inputs,
                '-filter_complex', filter_string,
                '-map', '0:v',  # Video từ input đầu tiên
                '-map', '[aout]',  # Audio từ filter output
                '-c:v', 'copy',  # Copy video codec
                '-c:a', 'aac',  # Audio codec
                '-shortest',  # Kết thúc khi input ngắn nhất kết thúc
                temp_output
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"FFmpeg error: {stderr.decode()}")
                raise VideoProcessingException(f"Không thể kết hợp audio: {stderr.decode()}")

            logger.info(f"Đã kết hợp audio tracks thành công: {temp_output}")
            return temp_output

        except Exception as e:
            logger.error(f"Lỗi khi kết hợp audio tracks: {str(e)}")
            raise VideoProcessingException(f"Không thể kết hợp audio tracks: {str(e)}")

    async def _add_subtitle_to_video(
        self,
        video_path: str,
        subtitle_path: str,
        output_path: str
    ) -> str:
        """Thêm subtitle vào video"""
        try:
            import tempfile

            # Tạo file tạm cho output
            temp_output = output_path
            if not temp_output:
                temp_file = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
                temp_output = temp_file.name
                temp_file.close()

            # Chạy ffmpeg để thêm subtitle
            cmd = [
                'ffmpeg',
                '-y',
                '-i', video_path,
                '-vf', f"subtitles={subtitle_path.replace('\\', '/')}",
                '-c:a', 'copy',
                temp_output
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"FFmpeg subtitle error: {stderr.decode()}")
                raise VideoProcessingException(f"Không thể thêm subtitle: {stderr.decode()}")

            logger.info(f"Đã thêm subtitle thành công: {temp_output}")
            return temp_output

        except Exception as e:
            logger.error(f"Lỗi khi thêm subtitle: {str(e)}")
            raise VideoProcessingException(f"Không thể thêm subtitle: {str(e)}")

    def create_subtitle_file(
        self,
        segments: List[Dict[str, Any]],
        output_path: Optional[str] = None,
        subtitle_format: str = "srt"
    ) -> str:
        """
        Tạo file subtitle từ segments

        Args:
            segments: Danh sách segments với text và timing
            output_path: Đường dẫn file output (nếu None thì tạo tự động)
            subtitle_format: Format subtitle (srt, vtt, ass)

        Returns:
            Đường dẫn đến file subtitle được tạo
        """
        try:
            if not segments:
                raise VideoProcessingException("Segments không được rỗng")

            # Tạo output path nếu không có
            if not output_path:
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(suffix=f'.{subtitle_format}', delete=False)
                output_path = temp_file.name
                temp_file.close()

            if subtitle_format.lower() == "srt":
                self._create_srt_file(segments, output_path)
            elif subtitle_format.lower() == "vtt":
                self._create_vtt_file(segments, output_path)
            elif subtitle_format.lower() == "ass":
                self._create_ass_file(segments, output_path)
            else:
                raise VideoProcessingException(f"Subtitle format không được hỗ trợ: {subtitle_format}")

            logger.info(f"Đã tạo subtitle file: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Lỗi khi tạo subtitle file: {str(e)}")
            raise VideoProcessingException(f"Không thể tạo subtitle file: {str(e)}")

    def _create_srt_file(self, segments: List[Dict[str, Any]], output_path: str):
        """Tạo file SRT subtitle"""
        def seconds_to_srt_time(seconds: float) -> str:
            """Chuyển đổi seconds thành format SRT time"""
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            milliseconds = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{milliseconds:03d}"

        with open(output_path, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments):
                start_time = segment.get("start", 0)
                end_time = segment.get("end", start_time + 1)  # Default 1 second if no end time
                text = segment.get("translated_text", segment.get("text", "")).strip()

                if not text:
                    continue

                f.write(f"{i + 1}\n")
                f.write(f"{seconds_to_srt_time(start_time)} --> {seconds_to_srt_time(end_time)}\n")
                f.write(f"{text}\n\n")

    def _create_vtt_file(self, segments: List[Dict[str, Any]], output_path: str):
        """Tạo file VTT subtitle"""
        def seconds_to_vtt_time(seconds: float) -> str:
            """Chuyển đổi seconds thành format VTT time"""
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            milliseconds = int((seconds % 1) * 1000)
            return f"{hours:02d}:{minutes:02d}:{secs:02d}.{milliseconds:03d}"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("WEBVTT\n\n")

            for segment in segments:
                start_time = segment.get("start", 0)
                end_time = segment.get("end", start_time + 1)
                text = segment.get("translated_text", segment.get("text", "")).strip()

                if not text:
                    continue

                f.write(f"{seconds_to_vtt_time(start_time)} --> {seconds_to_vtt_time(end_time)}\n")
                f.write(f"{text}\n\n")

    def _create_ass_file(self, segments: List[Dict[str, Any]], output_path: str):
        """Tạo file ASS subtitle"""
        def seconds_to_ass_time(seconds: float) -> str:
            """Chuyển đổi seconds thành format ASS time"""
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            centiseconds = int((seconds % 1) * 100)
            return f"{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"

        with open(output_path, 'w', encoding='utf-8') as f:
            # ASS header
            f.write("""[Script Info]
Title: Vietnamese AI Dubbing
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,48,&Hffffff,&Hffffff,&H0,&H0,0,0,0,0,100,100,0,0,1,2,0,2,10,10,10,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""")

            # ASS events
            for segment in segments:
                start_time = segment.get("start", 0)
                end_time = segment.get("end", start_time + 1)
                text = segment.get("translated_text", segment.get("text", "")).strip()

                if not text:
                    continue

                # Escape special characters
                text = text.replace('\\', '\\\\').replace('{', '\\{').replace('}', '\\}')

                f.write(f"Dialogue: 0,{seconds_to_ass_time(start_time)},{seconds_to_ass_time(end_time)},Default,,0,0,0,,{text}\n")

    def _get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Lấy thông tin video file"""
        try:
            if not os.path.exists(video_path):
                return {'error': 'File không tồn tại'}

            # Sử dụng ffprobe để lấy thông tin
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_path
            ]

            process = subprocess.run(cmd, capture_output=True, text=True)
            if process.returncode != 0:
                return {'error': 'Không thể đọc thông tin video'}

            import json
            info = json.loads(process.stdout)

            # Lấy thông tin cơ bản
            video_info = {
                'duration': float(info['format'].get('duration', 0)),
                'size': int(info['format'].get('size', 0)),
                'bitrate': int(info['format'].get('bit_rate', 0)),
                'format': info['format'].get('format_name', 'Unknown')
            }

            # Lấy thông tin video stream
            for stream in info.get('streams', []):
                if stream.get('codec_type') == 'video':
                    video_info.update({
                        'codec': stream.get('codec_name', 'Unknown'),
                        'width': int(stream.get('width', 0)),
                        'height': int(stream.get('height', 0)),
                        'resolution': f"{stream.get('width', 0)}x{stream.get('height', 0)}",
                        'fps': float(stream.get('r_frame_rate', '0/1').split('/')[0]) / float(stream.get('r_frame_rate', '0/1').split('/')[1]) if '/' in stream.get('r_frame_rate', '0/1') else float(stream.get('r_frame_rate', 0))
                    })
                    break

            return video_info

        except Exception as e:
            logger.error(f"Lỗi khi lấy thông tin video: {str(e)}")
            return {
                'error': str(e),
                'duration': 0,
                'size': os.path.getsize(video_path) if os.path.exists(video_path) else 0
            }

    async def extract_audio_from_video(
        self,
        video_path: str,
        output_path: Optional[str] = None,
        audio_format: str = "wav"
    ) -> str:
        """
        Tách audio từ video

        Args:
            video_path: Đường dẫn đến video
            output_path: Đường dẫn file output (nếu None thì tạo tự động)
            audio_format: Format audio output (wav, mp3, aac)

        Returns:
            Đường dẫn đến file audio được tách
        """
        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file không tồn tại: {video_path}")

            # Tạo output path nếu không có
            if not output_path:
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(suffix=f'.{audio_format}', delete=False)
                output_path = temp_file.name
                temp_file.close()

            # Chạy ffmpeg để tách audio
            cmd = [
                'ffmpeg',
                '-y',
                '-i', video_path,
                '-vn',  # No video
                '-acodec', 'copy' if audio_format == 'copy' else 'pcm_s16le' if audio_format == 'wav' else 'libmp3lame' if audio_format == 'mp3' else 'aac',
                '-ar', '16000',  # Sample rate 16kHz
                '-ac', '1',  # Mono
                output_path
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            if process.returncode != 0:
                logger.error(f"FFmpeg extract audio error: {stderr.decode()}")
                raise VideoProcessingException(f"Không thể tách audio: {stderr.decode()}")

            logger.info(f"Đã tách audio thành công: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Lỗi khi tách audio từ video: {str(e)}")
            raise VideoProcessingException(f"Không thể tách audio từ video: {str(e)}")

    def validate_video_file(self, video_path: str) -> bool:
        """
        Validate video file

        Args:
            video_path: Đường dẫn đến file video

        Returns:
            True nếu file hợp lệ
        """
        if not os.path.exists(video_path):
            return False

        valid_extensions = ['.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm']
        ext = Path(video_path).suffix.lower()

        return ext in valid_extensions

    def get_supported_subtitle_formats(self) -> List[str]:
        """Lấy danh sách subtitle formats được hỗ trợ"""
        return ["srt", "vtt", "ass", "ssa"]

    def get_supported_audio_formats(self) -> List[str]:
        """Lấy danh sách audio formats được hỗ trợ"""
        return ["wav", "mp3", "aac", "flac", "ogg"]

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
                        logger.info(f"Đã xóa file tạm video synthesis: {file_path}")

            # Dọn dẹp trong output_dir (giữ lại file mới hơn 7 ngày)
            for file_path in self.output_dir.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > (older_than_hours * 3600):
                        file_path.unlink()
                        logger.info(f"Đã xóa output file cũ: {file_path}")

        except Exception as e:
            logger.error(f"Lỗi khi dọn dẹp file tạm: {str(e)}")

    async def check_ffmpeg_availability(self) -> bool:
        """
        Kiểm tra FFmpeg có sẵn không

        Returns:
            True nếu FFmpeg có sẵn
        """
        try:
            process = await asyncio.create_subprocess_exec(
                "ffmpeg", "-version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()
            return process.returncode == 0

        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra FFmpeg: {str(e)}")
            return False

    def get_video_processing_options(self) -> Dict[str, Any]:
        """Lấy các options cho video processing"""
        return {
            "subtitle_formats": self.get_supported_subtitle_formats(),
            "audio_formats": self.get_supported_audio_formats(),
            "volume_ranges": {
                "background": {"min": 0.0, "max": 1.0, "default": 0.3},
                "voice": {"min": 0.0, "max": 2.0, "default": 1.0}
            },
            "supported_containers": [".mp4", ".mkv", ".avi", ".mov"],
            "recommended_settings": {
                "resolution": "1920x1080",
                "fps": 30,
                "audio_sample_rate": 44100,
                "audio_channels": 2
            }
        }