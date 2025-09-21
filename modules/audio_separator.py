import os
import shutil
from pathlib import Path
from demucs.api import Separator
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class AudioSeparator:
    """Module tách vocals khỏi background music sử dụng Demucs"""

    def __init__(self):
        self.temp_dir = Path(settings.TEMP_DIR)
        self.models_dir = Path(settings.MODELS_DIR)
        self.separator = None

    def _init_separator(self):
        """Khởi tạo Demucs separator với model htdemucs_ft"""
        if self.separator is None:
            try:
                # Sử dụng model htdemucs_ft cho chất lượng tốt
                self.separator = Separator(
                    model="htdemucs_ft",  # High quality model
                    repo=None,  # Sử dụng model mặc định
                    device='cuda' if settings.device == 'cuda' else 'cpu'
                )
                logger.info("Đã khởi tạo Demucs separator với model htdemucs_ft")
            except Exception as e:
                logger.error(f"Lỗi khởi tạo separator: {str(e)}")
                # Fallback to basic model
                self.separator = Separator(model="htdemucs")

    def extract_vocals(self, audio_path: str) -> tuple[str, str]:
        """Tách vocals và background từ audio

        Args:
            audio_path: Đường dẫn đến file audio input

        Returns:
            tuple: (vocals_path, background_path)
        """
        try:
            self._init_separator()

            audio_path = Path(audio_path)
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file không tồn tại: {audio_path}")

            logger.info(f"Đang tách vocals từ: {audio_path}")

            # Thư mục output cho demucs
            output_dir = self.temp_dir / "separated"
            output_dir.mkdir(exist_ok=True)

            # Chạy separation
            # Demucs sẽ tạo thư mục con với tên model
            result_dir = self.separator.separate_audio_file(
                audio_path=str(audio_path),
                output_dir=str(output_dir)
            )

            # Tìm file vocals và background
            result_path = Path(result_dir)

            # Demucs output structure: output_dir/model_name/audio_name/(vocals.wav, drums.wav, bass.wav, other.wav, guitar.wav)
            # Với htdemucs_ft, vocals là "vocals.wav", background là mix của others
            vocals_file = result_path / "vocals.wav"

            if not vocals_file.exists():
                # Thử tìm trong subdirs
                for subdir in result_path.iterdir():
                    if subdir.is_dir():
                        vocals_candidate = subdir / "vocals.wav"
                        if vocals_candidate.exists():
                            vocals_file = vocals_candidate
                            result_path = subdir
                            break

            if not vocals_file.exists():
                raise FileNotFoundError("Không tìm thấy file vocals.wav sau khi tách")

            # Tạo file background bằng cách combine các track khác vocals
            background_files = []
            for track_file in result_path.glob("*.wav"):
                if track_file.name != "vocals.wav":
                    background_files.append(track_file)

            # Nếu không có background files, tạo silent background
            if not background_files:
                background_path = result_path / "background.wav"
                # Tạo silent audio với cùng duration
                import soundfile as sf
                import numpy as np

                # Đọc info vocals để tạo background cùng duration
                vocals_data, sr = sf.read(str(vocals_file))
                silent_data = np.zeros_like(vocals_data)
                sf.write(str(background_path), silent_data, sr)
            else:
                # Merge các background tracks
                background_path = result_path / "background.wav"
                self._mix_audio_files(background_files, background_path)

            # Copy files ra temp dir với tên rõ ràng
            final_vocals = self.temp_dir / f"{audio_path.stem}_vocals.wav"
            final_background = self.temp_dir / f"{audio_path.stem}_background.wav"

            shutil.copy2(vocals_file, final_vocals)
            shutil.copy2(background_path, final_background)

            logger.info(f"Đã tách thành công: vocals={final_vocals}, background={final_background}")

            return str(final_vocals), str(final_background)

        except Exception as e:
            logger.error(f"Lỗi khi tách audio: {str(e)}")
            raise Exception(f"Không thể tách vocals từ audio: {str(e)}")

    def _mix_audio_files(self, audio_files: list, output_path: Path):
        """Mix nhiều audio files thành một file"""
        try:
            import soundfile as sf
            import numpy as np

            mixed_data = None
            sample_rate = None

            for audio_file in audio_files:
                data, sr = sf.read(str(audio_file))
                if sample_rate is None:
                    sample_rate = sr
                    mixed_data = data
                else:
                    # Resample if needed (đơn giản, assume same sr)
                    mixed_data += data

            # Normalize để tránh clipping
            if np.max(np.abs(mixed_data)) > 1.0:
                mixed_data = mixed_data / np.max(np.abs(mixed_data))

            sf.write(str(output_path), mixed_data, sample_rate)

        except Exception as e:
            logger.error(f"Lỗi khi mix audio: {str(e)}")
            # Fallback: copy file đầu tiên
            shutil.copy2(str(audio_files[0]), str(output_path))

    def cleanup_temp_files(self):
        """Xóa files tạm thời"""
        try:
            separated_dir = self.temp_dir / "separated"
            if separated_dir.exists():
                shutil.rmtree(separated_dir)
                logger.debug("Đã xóa temp files của audio separator")
        except Exception as e:
            logger.warning(f"Không thể xóa temp files: {str(e)}")

# Global instance
audio_separator = AudioSeparator()