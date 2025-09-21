import os
from dotenv import load_dotenv

# Load biến môi trường từ .env file
load_dotenv()

class Settings:
    """Cấu hình cho ứng dụng Vietnamese AI Dubbing"""

    # OpenRouter API
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "microsoft/wizardlm-2-8x22b")

    # Ollama settings
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

    # Default settings
    DEFAULT_TRANSLATOR = os.getenv("DEFAULT_TRANSLATOR", "gtx_free")  # gtx_free, openrouter, ollama
    DEFAULT_VOICE = os.getenv("DEFAULT_VOICE", "vi-VN-HoaiMyNeural")
    OUTPUT_FORMAT = os.getenv("OUTPUT_FORMAT", "mp4")

    # Directories
    TEMP_DIR = os.getenv("TEMP_DIR", "./temp")
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")
    MODELS_DIR = "./models"

    # TTS settings
    VIETNAMESE_VOICES = [
        "vi-VN-HoaiMyNeural",
        "vi-VN-NamMinhNeural",
        "vi-VN-HoaiMyNeural"  # female
    ]

    # Translation methods
    TRANSLATION_METHODS = ["gtx_free", "openrouter", "ollama"]

    @classmethod
    def validate_settings(cls):
        """Validate các thiết lập cần thiết"""
        if cls.DEFAULT_TRANSLATOR not in cls.TRANSLATION_METHODS:
            raise ValueError(f"DEFAULT_TRANSLATOR phải là một trong {cls.TRANSLATION_METHODS}")

        if cls.DEFAULT_VOICE not in cls.VIETNAMESE_VOICES:
            raise ValueError(f"DEFAULT_VOICE phải là một trong {cls.VIETNAMESE_VOICES}")

        # Tạo thư mục nếu chưa có
        os.makedirs(cls.TEMP_DIR, exist_ok=True)
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.MODELS_DIR, exist_ok=True)

# Khởi tạo settings
settings = Settings()
settings.validate_settings()