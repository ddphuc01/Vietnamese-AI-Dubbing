#!/usr/bin/env python3
"""
Vietnamese AI Dubbing - Main Pipeline
Công cụ lồng tiếng video tự động sang tiếng Việt
"""

import os
import sys
from pathlib import Path
import logging
from typing import Optional, Dict, Any

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from config.settings import settings
from modules.video_downloader import video_downloader
from modules.audio_separator import audio_separator
from modules.speech_recognition import speech_recognizer
from modules.translator import translator
from modules.text_to_speech import text_to_speech
from modules.video_processor import video_processor

# Setup logging
log_file_path = Path(settings.LOG_DIR) / 'vietnamese_dubbing.log'
handlers = [logging.StreamHandler(sys.stdout)]

try:
    # Ensure the log directory exists
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    handlers.append(file_handler)
except (IOError, OSError) as e:
    # Log an error to the console if file logging fails
    sys.stderr.write(f"WARNING: Could not set up file logger at {log_file_path}: {e}\n")
    sys.stderr.write("WARNING: Logging will proceed to console only.\n")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)

class VietnameseAIDubbing:
    """Main class orchestrating the AI dubbing pipeline"""

    def __init__(self):
        logger.info("Khởi tạo Vietnamese AI Dubbing pipeline")
        self.progress_callback = None

    def set_progress_callback(self, callback):
        """Set callback for progress updates"""
        self.progress_callback = callback

    def _update_progress(self, step: str, progress: float, message: str):
        """Update progress"""
        logger.info(f"[{step}] {progress:.1f}% - {message}")
        if self.progress_callback:
            self.progress_callback(progress, message)

    def process_video(self,
                     video_input: str,
                     translator_method: str = None,
                     voice_name: str = None,
                     output_name: str = None) -> Dict[str, Any]:
        """Process full pipeline từ video input đến output

        Args:
            video_input: URL hoặc path của video
            translator_method: Phương thức dịch ('gtx_free', 'openrouter', 'ollama')
            voice_name: Tên voice tiếng Việt
            output_name: Tên file output tùy chỉnh

        Returns:
            Dict với kết quả và metadata
        """
        try:
            # Validate inputs
            logger.info("Bước 1: Validate inputs")
            if not video_input:
                raise ValueError("Video input không được để trống")

            if translator_method is None:
                translator_method = settings.DEFAULT_TRANSLATOR

            if voice_name is None:
                voice_name = settings.DEFAULT_VOICE

            logger.info(f"Bắt đầu xử lý video: {video_input}")
            logger.info(f"Translator: {translator_method}, Voice: {voice_name}")

            # Step 1: Download/Prepare video
            logger.info("Bước 2: Download/Prepare video")
            self._update_progress("DOWNLOAD", 5, "Đang tải video...")
            if video_input.startswith(('http://', 'https://')):
                logger.info(f"Downloading video từ URL: {video_input}")
                video_path = video_downloader.download_from_url(video_input)
                logger.info(f"Đã download video thành công: {video_path}")
            else:
                logger.info(f"Xử lý file upload: {video_input}")
                video_path = video_downloader.handle_uploaded_file(video_input)
                logger.info(f"Đã chuẩn bị video: {video_path}")

            # Step 2: Extract audio và tách vocals
            logger.info("Bước 3: Extract audio và tách vocals")
            self._update_progress("AUDIO_EXTRACT", 15, "Đang tách audio vocals...")
            logger.info("Extracting audio từ video...")
            audio_path = self._extract_audio_from_video(video_path)
            logger.info(f"Đã extract audio: {audio_path}")
            logger.info("Tách vocals từ background music...")
            vocals_path, background_path = audio_separator.extract_vocals(audio_path)
            logger.info(f"Đã tách vocals: {vocals_path}")
            if background_path:
                logger.info(f"Background music: {background_path}")

            # Step 3: Speech recognition
            logger.info("Bước 4: Speech recognition")
            self._update_progress("TRANSCRIBE", 30, "Đang nhận dạng giọng nói...")
            logger.info(f"Transcribing audio: {vocals_path}")
            transcript = speech_recognizer.transcribe_audio(vocals_path)
            logger.info(f"Đã transcribe thành công: {len(transcript.get('segments', []))} segments")

            # Step 4: Translate to Vietnamese
            logger.info("Bước 5: Translate to Vietnamese")
            self._update_progress("TRANSLATE", 50, "Đang dịch sang tiếng Việt...")
            logger.info(f"Translating {len(transcript.get('segments', []))} segments với method: {translator_method}")
            translated_segments = translator.translate_segments(
                transcript["segments"],
                target_lang="vi",
                method=translator_method
            )
            logger.info(f"Đã dịch thành công {len(translated_segments)} segments")

            # Step 5: Text-to-speech
            logger.info("Bước 6: Text-to-speech")
            self._update_progress("TTS", 70, "Đang tổng hợp giọng nói tiếng Việt...")
            logger.info(f"Generating speech với voice: {voice_name}")
            viet_audio_path = self._create_vietnamese_audio(translated_segments, voice_name)
            logger.info(f"Đã tạo Vietnamese audio: {viet_audio_path}")

            # Step 6: Create subtitle file
            logger.info("Bước 7: Create subtitle file")
            self._update_progress("SUBTITLES", 85, "Đang tạo phụ đề...")
            logger.info("Creating subtitle file từ translated segments")
            sub_path = self._create_subtitle_file(translated_segments)
            logger.info(f"Đã tạo subtitle file: {sub_path}")

            # Step 7: Combine video + audio + subtitles
            logger.info("Bước 8: Combine video + audio + subtitles")
            self._update_progress("FINALIZE", 95, "Đang tạo video final...")
            logger.info("Combining video với Vietnamese audio và subtitles")
            final_video_path = video_processor.combine_audio_video(
                video_path=video_path,
                vietnamese_audio_path=viet_audio_path,
                background_audio_path=background_path,
                subtitle_path=sub_path,
                output_filename=output_name
            )
            logger.info(f"Đã tạo video final: {final_video_path}")

            self._update_progress("COMPLETE", 100, "Hoàn thành!")

            # Cleanup temp files
            logger.info("Bước 9: Cleanup temp files")
            self._cleanup_temp_files()

            result = {
                "success": True,
                "final_video": final_video_path,
                "subtitle_file": sub_path,
                "transcript": transcript,
                "translated_segments": translated_segments,
                "metadata": {
                    "original_video": video_path,
                    "translator_method": translator_method,
                    "voice_used": voice_name,
                    "processing_time": "calculated_time"  # Có thể add timer
                }
            }

            logger.info(f"Hoàn thành pipeline thành công: {final_video_path}")
            return result

        except Exception as e:
            logger.error(f"Lỗi trong pipeline: {str(e)}")
            self._cleanup_temp_files()
            return {
                "success": False,
                "error": str(e),
                "metadata": {}
            }

    def _extract_audio_from_video(self, video_path: str) -> str:
        """Extract audio từ video sử dụng ffmpeg"""
        from moviepy import VideoFileClip
        import os

        audio_path = str(Path(settings.TEMP_DIR) / f"{Path(video_path).stem}_audio.wav")

        try:
            video = VideoFileClip(video_path)
            video.audio.write_audiofile(audio_path)
            video.close()
            return audio_path
        except Exception as e:
            logger.error(f"Lỗi extract audio: {str(e)}")
            raise

    def _create_vietnamese_audio(self, segments: list, voice_name: str) -> str:
        """Tạo audio tiếng Việt từ segments"""
        try:
            # Create single audio file by concatenating segments
            from pydub import AudioSegment
            import os

            combined_audio = AudioSegment.empty()

            for segment in segments:
                text = segment.get("text", "").strip()
                if text:
                    # Generate audio cho segment
                    audio_path = text_to_speech.generate_speech(text, voice_name)
                    segment_audio = AudioSegment.from_file(audio_path)

                    # Add silence/padding dựa trên timing
                    start_time = segment.get("start", 0)
                    end_time = segment.get("end", 0)

                    if start_time > 0 and len(combined_audio) < start_time * 1000:
                        silence_duration = start_time * 1000 - len(combined_audio)
                        silence = AudioSegment.silent(duration=silence_duration)
                        combined_audio += silence

                    combined_audio += segment_audio

            # Export combined audio
            output_path = str(Path(settings.TEMP_DIR) / "vietnamese_audio.mp3")
            combined_audio.export(output_path, format="mp3")

            return output_path

        except Exception as e:
            logger.error(f"Lỗi tạo Vietnamese audio: {str(e)}")
            raise

    def _create_subtitle_file(self, segments: list) -> str:
        """Tạo file subtitle từ translated segments"""
        sub_path = str(Path(settings.OUTPUT_DIR) / "subtitles_vi.srt")
        speech_recognizer.create_subtitle_file(
            {"segments": segments},
            sub_path,
            format="srt"
        )
        return sub_path

    def _cleanup_temp_files(self):
        """Xóa files tạm thời"""
        try:
            import shutil
            # Có thể xóa một số temp files, nhưng cẩn thận không xóa output
            audio_separator.cleanup_temp_files()
            logger.debug("Đã cleanup temp files")
        except Exception as e:
            logger.warning(f"Lỗi cleanup: {str(e)}")

def main():
    """Main function cho CLI usage"""
    import argparse

    parser = argparse.ArgumentParser(description="Vietnamese AI Dubbing")
    parser.add_argument("video_input", help="URL hoặc path của video")
    parser.add_argument("--translator", choices=["gtx_free", "openrouter", "ollama"],
                       default=settings.DEFAULT_TRANSLATOR, help="Phương thức dịch")
    parser.add_argument("--voice", default=settings.DEFAULT_VOICE,
                       help="Voice tiếng Việt")
    parser.add_argument("--output", help="Tên file output")

    args = parser.parse_args()

    # Khởi tạo và chạy
    dubbing = VietnameseAIDubbing()

    result = dubbing.process_video(
        video_input=args.video_input,
        translator_method=args.translator,
        voice_name=args.voice,
        output_name=args.output
    )

    if result["success"]:
        print(f"✅ Thành công! Video final: {result['final_video']}")
        print(f"📝 Phụ đề: {result['subtitle_file']}")
    else:
        print(f"❌ Lỗi: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()