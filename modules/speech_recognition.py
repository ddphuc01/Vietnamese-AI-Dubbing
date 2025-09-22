import os
import json
from pathlib import Path
from funasr import AutoModel
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class SpeechRecognizer:
    """Module nhận dạng giọng nói sử dụng FunASR"""

    def __init__(self):
        self.temp_dir = Path(settings.TEMP_DIR)
        self.models_dir = Path(settings.MODELS_DIR)
        self.model = None

    def _init_model(self):
        """Khởi tạo FunASR model cho tiếng Việt"""
        if self.model is None:
            try:
                # Sử dụng model pre-trained cho tiếng Việt
                # Paraformer model tốt cho tiếng Việt
                model_dir = self.models_dir / "funasr"

                if not model_dir.exists():
                    logger.info("Downloading FunASR model cho tiếng Việt...")
                    # FunASR sẽ tự download model
                    model_dir.mkdir(parents=True, exist_ok=True)

                # Load model - FunASR sẽ tự detect và download
                self.model = AutoModel(
                    model="paraformer",
                    model_revision="v2.0.4",
                    device=settings.DEVICE
                )

                logger.info("Đã khởi tạo FunASR model cho tiếng Việt")

            except Exception as e:
                logger.error(f"Lỗi khởi tạo FunASR model: {str(e)}")
                raise Exception(f"Không thể tải FunASR model: {str(e)}")

    def transcribe_audio(self, audio_path: str) -> dict:
        """Nhận dạng speech từ audio file

        Args:
            audio_path: Đường dẫn đến file audio (vocals đã tách)

        Returns:
            dict: Transcript với format
            {
                "text": "full transcript",
                "segments": [
                    {
                        "text": "segment text",
                        "start": 0.0,
                        "end": 0.0,  # Không có timestamp
                        "speaker": "SPEAKER_00"
                    }
                ],
                "language": "vi"
            }
        """
        try:
            self._init_model()

            audio_path = Path(audio_path)
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file không tồn tại: {audio_path}")

            logger.info(f"Đang transcribe audio: {audio_path}")

            # FunASR inference - không dùng timestamp features
            result = self.model.generate(
                input=str(audio_path),
                batch_size_s=60,  # Batch size cho speed
            )

            logger.debug(f"FunASR raw result: {result}")

            # Parse result thành format chuẩn
            transcript_data = self._parse_funasr_result(result)

            logger.info(f"Đã transcribe thành công: {len(transcript_data['segments'])} segments")

            return transcript_data

        except Exception as e:
            logger.error(f"Lỗi khi transcribe audio: {str(e)}")
            raise Exception(f"Không thể transcribe audio: {str(e)}")

    def _parse_funasr_result(self, funasr_result) -> dict:
        """Parse kết quả từ FunASR thành format chuẩn"""
        try:
            # FunASR trả về list of dicts
            if isinstance(funasr_result, list) and len(funasr_result) > 0:
                result = funasr_result[0]
            else:
                result = funasr_result

            # Extract text
            full_text = ""

            # Fallback: create single segment without timestamp
            if "text" in result:
                full_text = result["text"]
                # Create single segment
                segments = [{
                    "text": full_text,
                    "start": 0.0,
                    "end": 0.0,  # Unknown duration
                    "speaker": "SPEAKER_00"
                }]
            else:
                segments = []

            return {
                "text": full_text.strip(),
                "segments": segments,
                "language": "vi"
            }

        except Exception as e:
            logger.error(f"Lỗi parse FunASR result: {str(e)}")
            # Return fallback
            return {
                "text": "Không thể transcribe",
                "segments": [],
                "language": "vi"
            }

    def detect_language(self, audio_path: str) -> str:
        """Detect ngôn ngữ của audio

        Args:
            audio_path: Đường dẫn audio

        Returns:
            str: Language code (vi, en, etc.)
        """
        try:
            # FunASR có thể detect language, nhưng tạm return vi
            return "vi"
        except Exception as e:
            logger.warning(f"Không thể detect language: {str(e)}")
            return "vi"

    def create_subtitle_file(self, transcript_data: dict, output_path: str, format: str = "srt"):
        """Tạo file subtitle từ transcript

        Args:
            transcript_data: Dữ liệu transcript
            output_path: Đường dẫn output
            format: srt hoặc vtt
        """
        try:
            segments = transcript_data.get("segments", [])
            full_text = transcript_data.get("text", "")

            # Nếu không có segments thực sự, chia text thành các subtitle hợp lý
            if not segments or all(s.get('start', 0) == s.get('end', 0) for s in segments):
                # Chia text thành các segment ~10 giây mỗi segment
                words = full_text.split()
                segment_duration = 10.0  # 10 seconds per segment
                chars_per_second = 15  # Approximate speaking rate

                new_segments = []
                current_segment = ""
                start_time = 0.0

                for word in words:
                    current_segment += word + " "
                    if len(current_segment) > chars_per_second * segment_duration:
                        end_time = start_time + len(current_segment) / chars_per_second
                        new_segments.append({
                            "text": current_segment.strip(),
                            "start": start_time,
                            "end": end_time
                        })
                        start_time = end_time
                        current_segment = ""

                # Add remaining text
                if current_segment.strip():
                    end_time = start_time + len(current_segment) / chars_per_second
                    new_segments.append({
                        "text": current_segment.strip(),
                        "start": start_time,
                        "end": end_time
                    })

                segments = new_segments if new_segments else [{
                    "text": full_text,
                    "start": 0.0,
                    "end": max(5.0, len(full_text) * 0.08)
                }]

            with open(output_path, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(segments, 1):
                    start_time = self._format_timestamp(segment.get('start', 0))
                    end_time = self._format_timestamp(segment.get('end', segment.get('start', 0) + 5.0))
                    text = segment.get('text', '').strip()

                    if text:  # Only write non-empty segments
                        if format == "srt":
                            f.write(f"{i}\n")
                            f.write(f"{start_time} --> {end_time}\n")
                            f.write(f"{text}\n\n")
                        elif format == "vtt":
                            if i == 1:  # Header for VTT
                                f.write("WEBVTT\n\n")
                            f.write(f"{start_time} --> {end_time}\n")
                            f.write(f"{text}\n\n")

            logger.info(f"Đã tạo subtitle file với {len(segments)} segments: {output_path}")

        except Exception as e:
            logger.error(f"Lỗi tạo subtitle file: {str(e)}")

    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds thành timestamp SRT/VTT"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
        else:
            return f"00:{minutes:02d}:{secs:02d},{millis:03d}"

# Global instance
speech_recognizer = SpeechRecognizer()