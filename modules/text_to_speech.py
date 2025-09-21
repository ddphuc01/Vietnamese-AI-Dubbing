import asyncio
import os
from pathlib import Path
import edge_tts
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class TextToSpeech:
    """Module tổng hợp giọng nói sử dụng EdgeTTS"""

    def __init__(self):
        self.temp_dir = Path(settings.TEMP_DIR)
        self.voice = settings.DEFAULT_VOICE

    async def _generate_speech_async(self, text: str, output_path: str, voice: str = None) -> str:
        """Generate speech asynchronously"""
        if voice is None:
            voice = self.voice

        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            return output_path
        except Exception as e:
            logger.error(f"Lỗi generate speech: {str(e)}")
            raise

    def generate_speech(self, text: str, voice_name: str = None, output_filename: str = None) -> str:
        """Tổng hợp giọng nói từ text

        Args:
            text: Văn bản cần tổng hợp
            voice_name: Tên voice (optional)
            output_filename: Tên file output (optional)

        Returns:
            str: Đường dẫn đến file audio đã tạo
        """
        try:
            if voice_name is None:
                voice_name = self.voice

            # Validate voice
            if voice_name not in settings.VIETNAMESE_VOICES:
                logger.warning(f"Voice {voice_name} không có sẵn, sử dụng default {self.voice}")
                voice_name = self.voice

            # Tạo filename
            if output_filename is None:
                output_filename = f"tts_{hash(text) % 10000}.mp3"

            output_path = self.temp_dir / output_filename

            logger.info(f"Đang tổng hợp giọng nói: {voice_name} - {len(text)} ký tự")

            # Run async function
            asyncio.run(self._generate_speech_async(text, str(output_path), voice_name))

            if not output_path.exists():
                raise Exception("File audio không được tạo")

            logger.info(f"Đã tạo audio thành công: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Lỗi generate speech: {str(e)}")
            raise Exception(f"Không thể tạo audio từ text: {str(e)}")

    def generate_speech_for_segments(self, segments: list, voice_name: str = None) -> list:
        """Tạo audio cho từng segment

        Args:
            segments: List of segments với 'text' và 'start' keys
            voice_name: Voice name

        Returns:
            list: List of (segment, audio_path) tuples
        """
        audio_files = []

        for i, segment in enumerate(segments):
            text = segment.get("text", "").strip()
            if not text:
                continue

            # Tạo filename dựa trên timestamp
            start_time = segment.get("start", 0)
            filename = f"segment_{int(start_time * 1000)}.mp3"  # milliseconds

            try:
                audio_path = self.generate_speech(text, voice_name, filename)
                audio_files.append((segment, audio_path))
                logger.debug(f"Đã tạo audio cho segment {i+1}: {text[:50]}...")
            except Exception as e:
                logger.error(f"Lỗi tạo audio cho segment {i+1}: {str(e)}")
                # Có thể tạo silent audio để thay thế
                continue

        logger.info(f"Đã tạo {len(audio_files)} audio files từ {len(segments)} segments")
        return audio_files

    def get_available_voices(self) -> list:
        """Trả về danh sách voices tiếng Việt có sẵn"""
        return settings.VIETNAMESE_VOICES.copy()

    def preview_voice(self, voice_name: str, text: str = "Xin chào, đây là bản demo giọng nói tiếng Việt.") -> str:
        """Tạo audio preview cho voice

        Args:
            voice_name: Tên voice
            text: Text mẫu

        Returns:
            str: Đường dẫn đến file preview
        """
        try:
            filename = f"preview_{voice_name.replace('-', '_')}.mp3"
            return self.generate_speech(text, voice_name, filename)
        except Exception as e:
            logger.error(f"Lỗi tạo preview cho voice {voice_name}: {str(e)}")
            raise

    def adjust_audio_speed(self, audio_path: str, speed_factor: float = 1.0) -> str:
        """Điều chỉnh tốc độ audio (optional)

        Args:
            audio_path: Đường dẫn audio gốc
            speed_factor: Hệ số tốc độ (>1 faster, <1 slower)

        Returns:
            str: Đường dẫn audio đã điều chỉnh
        """
        try:
            from pydub import AudioSegment
            import os

            audio = AudioSegment.from_file(audio_path)

            # Adjust speed
            if speed_factor != 1.0:
                audio = audio.speedup(playback_speed=speed_factor)

            output_path = str(Path(audio_path).parent / f"adjusted_{Path(audio_path).name}")
            audio.export(output_path, format="mp3")

            logger.debug(f"Đã điều chỉnh tốc độ audio: {speed_factor}x")
            return output_path

        except Exception as e:
            logger.warning(f"Không thể điều chỉnh tốc độ: {str(e)}")
            return audio_path

# Global instance
text_to_speech = TextToSpeech()