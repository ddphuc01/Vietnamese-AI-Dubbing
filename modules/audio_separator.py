import os
import shutil
from pathlib import Path
from demucs.api import Separator
from config.settings import settings
import logging
import torch
import gc
import time

logger = logging.getLogger(__name__)

# Global variables for model caching (similar to Linly-Dubbing)
auto_device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
separator = None
model_loaded = False
current_model_config = {}

def load_model(model_name: str = "htdemucs_ft", device: str = 'auto', progress: bool = True, shifts: int = 5) -> Separator:
    """
    Load Demucs model with lazy loading and caching.
    Similar to Linly-Dubbing implementation.
    """
    global separator, model_loaded, current_model_config

    if separator is not None:
        # Check if configuration changed
        requested_config = {
            'model_name': model_name,
            'device': 'auto' if device == 'auto' else device,
            'shifts': shifts
        }

        if current_model_config == requested_config:
            logger.info(f'Demucs model already loaded and config matches')
            return separator
        else:
            logger.info(f'Demucs model config changed, reloading...')
            release_model()

    logger.info(f'Loading Demucs model: {model_name}')
    t_start = time.time()

    device_to_use = auto_device if device == 'auto' else torch.device(device)
    separator = Separator(model_name, device=device_to_use, progress=progress, shifts=shifts)

    # Store current model configuration
    current_model_config = {
        'model_name': model_name,
        'device': 'auto' if device == 'auto' else device,
        'shifts': shifts
    }

    model_loaded = True
    t_end = time.time()
    logger.info(f'Demucs model loaded successfully in {t_end - t_start:.2f} seconds')

    return separator

def release_model():
    """
    Release model resources to prevent memory leaks.
    """
    global separator, model_loaded, current_model_config

    if separator is not None:
        logger.info('Releasing Demucs model resources...')
        separator = None
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        model_loaded = False
        current_model_config = {}
        logger.info('Demucs model resources released')

class AudioSeparator:
    """Module tách vocals khỏi background music sử dụng Demucs API"""

    def __init__(self):
        self.temp_dir = Path(settings.TEMP_DIR)
        self.models_dir = Path(settings.MODELS_DIR)

    def extract_vocals(self, audio_path: str) -> tuple[str, str]:
        """Tách vocals và background từ audio sử dụng demucs API

        Args:
            audio_path: Đường dẫn đến file audio input

        Returns:
            tuple: (vocals_path, background_path)
        """
        try:
            audio_path = Path(audio_path)
            if not audio_path.exists():
                raise FileNotFoundError(f"Audio file không tồn tại: {audio_path}")

            logger.info(f"Đang tách vocals từ: {audio_path} sử dụng Demucs API")

            # Load model with default settings
            if not model_loaded:
                load_model()

            vocal_output_path = self.temp_dir / f"{audio_path.stem}_vocals.wav"
            background_output_path = self.temp_dir / f"{audio_path.stem}_background.wav"

            if vocal_output_path.exists() and background_output_path.exists():
                logger.info(f'Audio đã được tách trước đó: {audio_path.stem}')
                return str(vocal_output_path), str(background_output_path)

            t_start = time.time()

            try:
                # Use Demucs API directly
                origin, separated = separator.separate_audio_file(str(audio_path))
            except Exception as e:
                logger.error(f'Separation failed: {e}')
                # Retry with model reload
                release_model()
                load_model()
                logger.info('Retrying separation with reloaded model...')
                origin, separated = separator.separate_audio_file(str(audio_path))

            t_end = time.time()
            logger.info(f'Audio separation completed in {t_end - t_start:.2f} seconds')

            # Process separated audio (combine all non-vocal stems)
            vocals = separated['vocals'].numpy().T
            instruments = None

            for k, v in separated.items():
                if k == 'vocals':
                    continue
                if instruments is None:
                    instruments = v
                else:
                    instruments += v

            if instruments is not None:
                instruments = instruments.numpy().T
            else:
                # Fallback: create silent background
                import numpy as np
                instruments = np.zeros_like(vocals)

            # Save WAV files
            from scipy.io import wavfile
            wavfile.write(str(vocal_output_path), 44100, vocals.astype(np.int16))
            wavfile.write(str(background_output_path), 44100, instruments.astype(np.int16))

            logger.info(f'Vocals saved: {vocal_output_path}')
            logger.info(f'Background saved: {background_output_path}')

            return str(vocal_output_path), str(background_output_path)

        except Exception as e:
            logger.error(f'Lỗi khi tách audio: {str(e)}')
            # Fallback to simple copy (preserve original behavior)
            logger.warning("Demucs failed, falling back to copy mode")
            return self._fallback_extract_vocals(audio_path)

    def _fallback_extract_vocals(self, audio_path: Path) -> tuple[str, str]:
        """Fallback: copy original audio as vocals, create silent background"""
        logger.warning("Using fallback: copy original audio as vocals")

        final_vocals = self.temp_dir / f"{audio_path.stem}_vocals.wav"
        final_background = self.temp_dir / f"{audio_path.stem}_background.wav"

        shutil.copy2(audio_path, final_vocals)

        # Create silent background
        import soundfile as sf
        import numpy as np
        data, sr = sf.read(str(audio_path))
        silent_data = np.zeros_like(data)
        sf.write(str(final_background), silent_data, sr)

        return str(final_vocals), str(final_background)

    def cleanup_temp_files(self):
        """Xóa files tạm thời"""
        try:
            # Clean up any temporary demucs files if needed
            logger.debug("Cleanup completed for audio separator")
        except Exception as e:
            logger.warning(f"Không thể xóa temp files: {str(e)}")

# Global instance
audio_separator = AudioSeparator()