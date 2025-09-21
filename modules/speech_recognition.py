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
                    vad_model="fsmn-vad",
                    punc_model="ct-punc",
                    spk_model="cam++",
                    device='cuda' if hasattr(settings, 'device') and settings.device == 'cuda' else 'cpu'
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
                        "end": 2.5,
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

            # FunASR inference
            result = self.model.generate(
                input=str(audio_path),
                batch_size_s=60,  # Batch size cho speed
                return_spk_res=True,  # Trả về speaker diarization
                return_punc_res=True,  # Thêm punctuation
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
            segments = []

            # Parse utterances/sentences
            if "sentence_info" in result:
                for sentence in result["sentence_info"]:
                    text = sentence.get("text", "").strip()
                    if text:
                        # Tính timestamp (approximate)
                        start_time = sentence.get("start", 0) / 1000  # ms to seconds
                        end_time = sentence.get("end", 0) / 1000

                        segments.append({
                            "text": text,
                            "start": start_time,
                            "end": end_time,
                            "speaker": "SPEAKER_00"  # FunASR có thể detect speakers
                        })

                        full_text += text + " "

            # Fallback if no sentence_info
            if not segments and "text" in result:
                full_text = result["text"]
                # Create single segment
                segments = [{
                    "text": full_text,
                    "start": 0.0,
                    "end": 0.0,  # Unknown duration
                    "speaker": "SPEAKER_00"
                }]

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

            with open(output_path, 'w', encoding='utf-8') as f:
                for i, segment in enumerate(segments, 1):
                    start_time = self._format_timestamp(segment['start'])
                    end_time = self._format_timestamp(segment['end'])
                    text = segment['text']

                    if format == "srt":
                        f.write(f"{i}\n")
                        f.write(f"{start_time} --> {end_time}\n")
                        f.write(f"{text}\n\n")
                    elif format == "vtt":
                        if i == 1:  # Header for VTT
                            f.write("WEBVTT\n\n")
                        f.write(f"{start_time} --> {end_time}\n")
                        f.write(f"{text}\n\n")

            logger.info(f"Đã tạo subtitle file: {output_path}")

        except Exception as e:
            logger.error(f"Lỗi tạo subtitle file: {str(e)}")

    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds thành timestamp SRT/VTT"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)

        if hours > 0:
            return "02d"
        else:
            return "02d"

# Global instance
speech_recognizer = SpeechRecognizer()