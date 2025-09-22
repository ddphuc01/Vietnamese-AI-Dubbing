import requests
from deep_translator import GoogleTranslator as DeepGoogleTranslator
from openai import OpenAI
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class Translator:
    """Module dịch văn bản với fallback system"""

    def __init__(self):
        self.google_translator = DeepGoogleTranslator
        self.openai_client = None
        self.ollama_available = self._check_ollama()

    def _check_ollama(self) -> bool:
        """Kiểm tra Ollama có available không"""
        try:
            response = requests.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

    def _init_openai_client(self):
        """Khởi tạo OpenAI client cho OpenRouter"""
        if self.openai_client is None and settings.OPENROUTER_API_KEY:
            self.openai_client = OpenAI(
                api_key=settings.OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1"
            )

    def translate_text(self, text: str, target_lang: str = "vi", method: str = None) -> str:
        """Dịch văn bản với fallback system

        Args:
            text: Văn bản cần dịch
            target_lang: Ngôn ngữ đích (mặc định 'vi')
            method: Phương thức dịch ('gtx_free', 'openrouter', 'ollama')

        Returns:
            str: Văn bản đã dịch
        """
        if not text.strip():
            return text

        if method is None:
            method = settings.DEFAULT_TRANSLATOR

        methods_to_try = [method]

        # Thêm fallback methods nếu method chính fail
        if method == "gtx_free":
            methods_to_try.extend(["ollama"])
        elif method == "openrouter":
            methods_to_try.extend(["gtx_free", "ollama"])
        elif method == "ollama":
            methods_to_try.extend(["gtx_free"])

        for attempt_method in methods_to_try:
            try:
                logger.info(f"Đang thử dịch với method: {attempt_method}")
                if attempt_method == "gtx_free":
                    return self._translate_gtx_free(text, target_lang)
                elif attempt_method == "openrouter":
                    return self._translate_openrouter(text, target_lang)
                elif attempt_method == "ollama":
                    return self._translate_ollama(text, target_lang)
            except Exception as e:
                logger.warning(f"Method {attempt_method} thất bại: {str(e)}")
                continue

        # Nếu tất cả methods đều fail, return original text
        logger.error("Tất cả methods dịch đều thất bại, trả về text gốc")
        return text

    def _translate_gtx_free(self, text: str, target_lang: str) -> str:
        """Dịch sử dụng Google Translate API free"""
        try:
            # Use auto detection for source language
            translator = self.google_translator(source='auto', target=target_lang)
            translated_text = translator.translate(text)

            logger.info("Dịch thành công với Google Translate Free")
            return translated_text

        except Exception as e:
            logger.error(f"Lỗi Google Translate: {str(e)}")
            raise

    def _translate_openrouter(self, text: str, target_lang: str) -> str:
        """Dịch sử dụng OpenRouter API"""
        try:
            self._init_openai_client()
            if not self.openai_client:
                raise Exception("OpenRouter API key không được cấu hình")

            prompt = f"""Translate the following text to Vietnamese. Only return the translated text, nothing else:

{text}"""

            response = self.openai_client.chat.completions.create(
                model=settings.OPENROUTER_MODEL,
                messages=[
                    {"role": "system", "content": "You are a professional translator. Translate accurately and naturally."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )

            translated_text = response.choices[0].message.content.strip()

            # Clean up response (remove quotes if present)
            if translated_text.startswith('"') and translated_text.endswith('"'):
                translated_text = translated_text[1:-1]

            logger.info("Dịch thành công với OpenRouter")
            return translated_text

        except Exception as e:
            logger.error(f"Lỗi OpenRouter: {str(e)}")
            raise

    def _translate_ollama(self, text: str, target_lang: str) -> str:
        """Dịch sử dụng Ollama local model"""
        try:
            if not self.ollama_available:
                raise Exception("Ollama không available")

            prompt = f"""Translate the following text to Vietnamese. Only return the translated text, nothing else:

{text}"""

            payload = {
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False
            }

            response = requests.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                translated_text = result.get("response", "").strip()

                logger.info("Dịch thành công với Ollama")
                return translated_text
            else:
                raise Exception(f"Ollama API error: {response.status_code}")

        except Exception as e:
            logger.error(f"Lỗi Ollama: {str(e)}")
            raise

    def translate_segments(self, segments: list, target_lang: str = "vi", method: str = None) -> list:
        """Dịch list of segments

        Args:
            segments: List of dicts with 'text' key
            target_lang: Target language
            method: Translation method

        Returns:
            list: Segments with translated text
        """
        translated_segments = []

        for segment in segments:
            original_text = segment.get("text", "")
            if original_text.strip():
                translated_text = self.translate_text(original_text, target_lang, method)
            else:
                translated_text = original_text

            new_segment = segment.copy()
            new_segment["text"] = translated_text
            new_segment["original_text"] = original_text  # Keep original for reference

            translated_segments.append(new_segment)

        logger.info(f"Đã dịch {len(translated_segments)} segments")
        return translated_segments

    def get_available_methods(self) -> list:
        """Trả về list methods có sẵn"""
        methods = ["gtx_free"]  # Always available

        if settings.OPENROUTER_API_KEY:
            methods.append("openrouter")

        if self.ollama_available:
            methods.append("ollama")

        return methods

# Global instance
translator = Translator()