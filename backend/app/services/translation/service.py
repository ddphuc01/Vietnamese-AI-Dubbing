"""
Translation Service
Xử lý việc dịch text từ ngôn ngữ này sang ngôn ngữ khác
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import asyncio
import json

from app.core.config import settings
from app.core.exceptions import VideoProcessingException

logger = logging.getLogger(__name__)


class TranslationService:
    """Service xử lý việc dịch text"""

    def __init__(self):
        self.temp_dir = Path(settings.TEMP_DIR)
        self.temp_dir.mkdir(exist_ok=True)
        self.models_dir = Path(settings.MODELS_DIR) / "translation"
        self.models_dir.mkdir(parents=True, exist_ok=True)

        # Cấu hình mặc định
        self.default_method = "google"
        self.default_target_lang = "vi"

    async def translate_segments(
        self,
        segments: List[Dict[str, Any]],
        target_lang: str = "vi",
        method: str = "google"
    ) -> List[Dict[str, Any]]:
        """
        Dịch danh sách segments

        Args:
            segments: Danh sách segments cần dịch
            target_lang: Ngôn ngữ đích
            method: Phương pháp dịch (google, azure, aws, local)

        Returns:
            Danh sách segments đã được dịch
        """
        try:
            if not segments:
                return []

            logger.info(f"Bắt đầu dịch {len(segments)} segments sang {target_lang} với method {method}")

            if method.lower() == "google":
                return await self._translate_with_google(segments, target_lang)
            elif method.lower() == "azure":
                return await self._translate_with_azure(segments, target_lang)
            elif method.lower() == "aws":
                return await self._translate_with_aws(segments, target_lang)
            elif method.lower() == "openrouter":
                return await self._translate_with_openrouter(segments, target_lang)
            elif method.lower() == "ollama":
                return await self._translate_with_ollama(segments, target_lang)
            elif method.lower() == "local":
                return await self._translate_with_local_model(segments, target_lang)
            else:
                raise VideoProcessingException(f"Phương pháp dịch không được hỗ trợ: {method}")

        except Exception as e:
            logger.error(f"Lỗi khi dịch segments: {str(e)}")
            raise VideoProcessingException(f"Không thể dịch segments: {str(e)}")

    async def _translate_with_openrouter(
        self,
        segments: List[Dict[str, Any]],
        target_lang: str = "vi",
        model: str = "google/gemini-pro"
    ) -> List[Dict[str, Any]]:
        """Dịch sử dụng OpenRouter API"""
        try:
            import httpx
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise VideoProcessingException("OPENROUTER_API_KEY chưa được cấu hình")

            translated_segments = []
            async with httpx.AsyncClient() as client:
                for segment in segments:
                    try:
                        response = await client.post(
                            "https://openrouter.ai/api/v1/chat/completions",
                            headers={
                                "Authorization": f"Bearer {api_key}",
                                "Content-Type": "application/json"
                            },
                            json={
                                "model": model,
                                "messages": [
                                    {"role": "system", "content": f"Translate the following text to {target_lang}. Output only the translated text."},
                                    {"role": "user", "content": segment["text"]}
                                ]
                            }
                        )
                        response.raise_for_status()
                        data = response.json()
                        translated_text = data['choices'][0]['message']['content'].strip()
                        translated_segments.append({**segment, "translated_text": translated_text})
                    except Exception as e:
                        logger.warning(f"Lỗi khi dịch segment với OpenRouter: {e}")
                        translated_segments.append({**segment, "translated_text": segment["text"]})
            return translated_segments
        except Exception as e:
            raise VideoProcessingException(f"Lỗi khi sử dụng OpenRouter: {e}")

    async def _translate_with_ollama(
        self,
        segments: List[Dict[str, Any]],
        target_lang: str = "vi",
        model: str = "llama3"
    ) -> List[Dict[str, Any]]:
        """Dịch sử dụng Ollama local server"""
        try:
            import httpx
            ollama_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/generate")
            
            translated_segments = []
            async with httpx.AsyncClient(timeout=60.0) as client:
                for segment in segments:
                    try:
                        response = await client.post(
                            ollama_url,
                            json={
                                "model": model,
                                "prompt": f"Translate the following text to {target_lang}. Output only the translated text.\n\n{segment['text']}",
                                "stream": False
                            }
                        )
                        response.raise_for_status()
                        data = response.json()
                        translated_text = data['response'].strip()
                        translated_segments.append({**segment, "translated_text": translated_text})
                    except Exception as e:
                        logger.warning(f"Lỗi khi dịch segment với Ollama: {e}")
                        translated_segments.append({**segment, "translated_text": segment["text"]})
            return translated_segments
        except Exception as e:
            raise VideoProcessingException(f"Lỗi khi sử dụng Ollama: {e}")


    async def _translate_with_google(
        self,
        segments: List[Dict[str, Any]],
        target_lang: str = "vi"
    ) -> List[Dict[str, Any]]:
        """Dịch sử dụng Google Translate API"""
        try:
            from googletrans import Translator
            import time

            translator = Translator()
            translated_segments = []

            for i, segment in enumerate(segments):
                try:
                    # Dịch text
                    result = translator.translate(
                        segment["text"],
                        dest=target_lang,
                        src='auto'
                    )

                    translated_segments.append({
                        **segment,
                        "translated_text": result.text,
                        "detected_source_lang": result.src,
                        "target_lang": target_lang,
                        "confidence": result.extra_data.get('confidence', 0.0) if hasattr(result, 'extra_data') else 0.0
                    })

                    # Tránh rate limiting
                    if (i + 1) % 10 == 0:
                        await asyncio.sleep(1)

                except Exception as e:
                    logger.warning(f"Lỗi khi dịch segment {i}: {str(e)}")
                    # Giữ nguyên text gốc nếu không dịch được
                    translated_segments.append({
                        **segment,
                        "translated_text": segment["text"],
                        "detected_source_lang": "unknown",
                        "target_lang": target_lang,
                        "confidence": 0.0,
                        "error": str(e)
                    })

            logger.info(f"Đã dịch thành công {len(translated_segments)} segments với Google Translate")
            return translated_segments

        except ImportError:
            logger.error("googletrans chưa được cài đặt")
            raise VideoProcessingException("googletrans chưa được cài đặt. Chạy: pip install googletrans==4.0.0-rc1")
        except Exception as e:
            logger.error(f"Lỗi khi sử dụng Google Translate: {str(e)}")
            raise VideoProcessingException(f"Không thể dịch với Google Translate: {str(e)}")

    async def _translate_with_azure(
        self,
        segments: List[Dict[str, Any]],
        target_lang: str = "vi"
    ) -> List[Dict[str, Any]]:
        """Dịch sử dụng Azure Translator"""
        try:
            import os
            from azure.ai.translation.text import TextTranslationClient
            from azure.core.credentials import AzureKeyCredential

            # Lấy API key từ environment
            api_key = os.getenv("AZURE_TRANSLATOR_KEY")
            endpoint = os.getenv("AZURE_TRANSLATOR_ENDPOINT")
            region = os.getenv("AZURE_TRANSLATOR_REGION")

            if not all([api_key, endpoint, region]):
                raise VideoProcessingException("Azure Translator credentials chưa được cấu hình")

            client = TextTranslationClient(
                credential=AzureKeyCredential(api_key),
                endpoint=endpoint,
                region=region
            )

            translated_segments = []

            for segment in segments:
                try:
                    # Dịch text
                    response = client.translate(
                        body=[segment["text"]],
                        to_language=[target_lang],
                        from_language=None
                    )

                    if response and len(response) > 0:
                        translation = response[0].translations[0]
                        translated_segments.append({
                            **segment,
                            "translated_text": translation.text,
                            "detected_source_lang": translation.detected_language.language if translation.detected_language else "unknown",
                            "target_lang": target_lang,
                            "confidence": translation.confidence if translation.confidence else 0.0
                        })
                    else:
                        raise Exception("Không nhận được response từ Azure")

                except Exception as e:
                    logger.warning(f"Lỗi khi dịch segment: {str(e)}")
                    translated_segments.append({
                        **segment,
                        "translated_text": segment["text"],
                        "detected_source_lang": "unknown",
                        "target_lang": target_lang,
                        "confidence": 0.0,
                        "error": str(e)
                    })

            logger.info(f"Đã dịch thành công {len(translated_segments)} segments với Azure Translator")
            return translated_segments

        except ImportError:
            logger.error("azure-ai-texttranslate chưa được cài đặt")
            raise VideoProcessingException("azure-ai-texttranslate chưa được cài đặt. Chạy: pip install azure-ai-texttranslate")
        except Exception as e:
            logger.error(f"Lỗi khi sử dụng Azure Translator: {str(e)}")
            raise VideoProcessingException(f"Không thể dịch với Azure Translator: {str(e)}")

    async def _translate_with_aws(
        self,
        segments: List[Dict[str, Any]],
        target_lang: str = "vi"
    ) -> List[Dict[str, Any]]:
        """Dịch sử dụng AWS Translate"""
        try:
            import boto3

            # Lấy credentials từ environment
            aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            aws_region = os.getenv("AWS_REGION", "us-east-1")

            if not aws_access_key or not aws_secret_key:
                raise VideoProcessingException("AWS credentials chưa được cấu hình")

            client = boto3.client(
                'translate',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region
            )

            translated_segments = []

            for segment in segments:
                try:
                    # Dịch text
                    response = client.translate_text(
                        Text=segment["text"],
                        SourceLanguageCode='auto',
                        TargetLanguageCode=target_lang
                    )

                    translated_segments.append({
                        **segment,
                        "translated_text": response['TranslatedText'],
                        "detected_source_lang": response.get('SourceLanguageCode', 'unknown'),
                        "target_lang": target_lang,
                        "confidence": response.get('AppliedTerminologies', [{}])[0].get('Terms', [{}])[0].get('Confidence', 0.0) if response.get('AppliedTerminologies') else 0.0
                    })

                except Exception as e:
                    logger.warning(f"Lỗi khi dịch segment: {str(e)}")
                    translated_segments.append({
                        **segment,
                        "translated_text": segment["text"],
                        "detected_source_lang": "unknown",
                        "target_lang": target_lang,
                        "confidence": 0.0,
                        "error": str(e)
                    })

            logger.info(f"Đã dịch thành công {len(translated_segments)} segments với AWS Translate")
            return translated_segments

        except ImportError:
            logger.error("boto3 chưa được cài đặt")
            raise VideoProcessingException("boto3 chưa được cài đặt. Chạy: pip install boto3")
        except Exception as e:
            logger.error(f"Lỗi khi sử dụng AWS Translate: {str(e)}")
            raise VideoProcessingException(f"Không thể dịch với AWS Translate: {str(e)}")

    async def _translate_with_local_model(
        self,
        segments: List[Dict[str, Any]],
        target_lang: str = "vi"
    ) -> List[Dict[str, Any]]:
        """Dịch sử dụng local model (MarianMT)"""
        try:
            from transformers import MarianMTModel, MarianTokenizer
            import torch

            # Load model và tokenizer
            model_name = f"Helsinki-NLP/opus-mt-en-{target_lang}" if target_lang != "vi" else "Helsinki-NLP/opus-mt-en-vi"
            tokenizer = MarianTokenizer.from_pretrained(model_name)
            model = MarianMTModel.from_pretrained(model_name)

            # Sử dụng GPU nếu có
            device = "cuda" if torch.cuda.is_available() else "cpu"
            model = model.to(device)

            translated_segments = []

            for segment in segments:
                try:
                    # Tokenize
                    inputs = tokenizer(
                        segment["text"],
                        return_tensors="pt",
                        padding=True,
                        truncation=True,
                        max_length=512
                    ).to(device)

                    # Generate translation
                    translated = model.generate(**inputs)
                    translated_text = tokenizer.batch_decode(translated, skip_special_tokens=True)[0]

                    translated_segments.append({
                        **segment,
                        "translated_text": translated_text,
                        "detected_source_lang": "en",  # Local models thường chỉ hỗ trợ English
                        "target_lang": target_lang,
                        "confidence": 0.8  # Confidence mặc định cho local models
                    })

                except Exception as e:
                    logger.warning(f"Lỗi khi dịch segment: {str(e)}")
                    translated_segments.append({
                        **segment,
                        "translated_text": segment["text"],
                        "detected_source_lang": "unknown",
                        "target_lang": target_lang,
                        "confidence": 0.0,
                        "error": str(e)
                    })

            logger.info(f"Đã dịch thành công {len(translated_segments)} segments với local model")
            return translated_segments

        except ImportError:
            logger.error("transformers chưa được cài đặt")
            raise VideoProcessingException("transformers chưa được cài đặt. Chạy: pip install transformers torch")
        except Exception as e:
            logger.error(f"Lỗi khi sử dụng local model: {str(e)}")
            raise VideoProcessingException(f"Không thể dịch với local model: {str(e)}")

    async def translate_with_fallback(
        self,
        segments: List[Dict[str, Any]],
        target_lang: str = "vi",
        primary_method: str = "google",
        fallback_method: str = "local"
    ) -> List[Dict[str, Any]]:
        """
        Dịch với fallback mechanism

        Args:
            segments: Danh sách segments cần dịch
            target_lang: Ngôn ngữ đích
            primary_method: Phương pháp chính
            fallback_method: Phương pháp dự phòng

        Returns:
            Danh sách segments đã được dịch
        """
        try:
            logger.info(f"Thử dịch với phương pháp chính: {primary_method}")
            return await self.translate_segments(segments, target_lang, primary_method)
        except Exception as e:
            logger.warning(f"Phương pháp chính {primary_method} thất bại: {str(e)}")
            logger.info(f"Chuyển sang phương pháp dự phòng: {fallback_method}")
            try:
                return await self.translate_segments(segments, target_lang, fallback_method)
            except Exception as e2:
                logger.error(f"Cả hai phương pháp đều thất bại: {str(e2)}")
                raise VideoProcessingException(f"Không thể dịch segments: {str(e2)}")

    def translate_text(
        self,
        text: str,
        target_lang: str = "vi",
        method: str = "google"
    ) -> Dict[str, Any]:
        """
        Dịch một đoạn text đơn giản

        Args:
            text: Text cần dịch
            target_lang: Ngôn ngữ đích
            method: Phương pháp dịch

        Returns:
            Dict chứa kết quả dịch
        """
        try:
            # Tạo segment giả
            fake_segment = {
                "id": 0,
                "start": 0,
                "end": 0,
                "text": text,
                "speaker": "SPEAKER_01"
            }

            # Dịch
            translated_segments = asyncio.run(
                self.translate_segments([fake_segment], target_lang, method)
            )

            if translated_segments:
                return {
                    "original_text": text,
                    "translated_text": translated_segments[0]["translated_text"],
                    "detected_source_lang": translated_segments[0].get("detected_source_lang", "unknown"),
                    "target_lang": target_lang,
                    "confidence": translated_segments[0].get("confidence", 0.0),
                    "success": True
                }
            else:
                return {
                    "original_text": text,
                    "translated_text": text,
                    "detected_source_lang": "unknown",
                    "target_lang": target_lang,
                    "confidence": 0.0,
                    "success": False,
                    "error": "Không thể dịch text"
                }

        except Exception as e:
            logger.error(f"Lỗi khi dịch text: {str(e)}")
            return {
                "original_text": text,
                "translated_text": text,
                "detected_source_lang": "unknown",
                "target_lang": target_lang,
                "confidence": 0.0,
                "success": False,
                "error": str(e)
            }

    def get_supported_languages(self) -> Dict[str, str]:
        """Lấy danh sách ngôn ngữ được hỗ trợ"""
        return {
            "vi": "Tiếng Việt",
            "en": "English",
            "zh": "中文",
            "ja": "日本語",
            "ko": "한국어",
            "fr": "Français",
            "de": "Deutsch",
            "es": "Español",
            "ru": "Русский",
            "pt": "Português",
            "it": "Italiano",
            "th": "ไทย",
            "ar": "العربية",
            "hi": "हिन्दी",
            "tr": "Türkçe",
            "pl": "Polski",
            "nl": "Nederlands",
            "sv": "Svenska",
            "da": "Dansk",
            "no": "Norsk",
            "fi": "Suomi",
            "he": "עברית",
            "uk": "Українська",
            "cs": "Čeština",
            "ro": "Română",
            "hu": "Magyar",
            "el": "Ελληνικά",
            "bg": "Български",
            "hr": "Hrvatski",
            "sk": "Slovenčina",
            "sl": "Slovenščina",
            "et": "Eesti",
            "lv": "Latviešu",
            "lt": "Lietuvių",
            "mt": "Malti",
            "ga": "Gaeilge",
            "cy": "Cymraeg",
            "is": "Íslenska",
            "mk": "Македонски",
            "sq": "Shqip",
            "bs": "Bosanski",
            "sr": "Српски",
            "hy": "Հայերեն",
            "ka": "ქართული",
            "mn": "Монгол",
            "kk": "Қазақ",
            "uz": "O'zbek",
            "az": "Azərbaycan",
            "tg": "Тоҷикӣ",
            "tk": "Türkmen",
            "ky": "Кыргыз",
            "ne": "नेपाली",
            "si": "සිංහල",
            "km": "ខ្មែរ",
            "lo": "ລາວ",
            "my": "မြန်မာဘာသာ",
            "am": "አማርኛ",
            "ti": "ትግርኛ",
            "om": "Afaan Oromoo",
            "so": "Soomaali",
            "sw": "Kiswahili",
            "yo": "Yorùbá",
            "ig": "Igbo",
            "ha": "Hausa",
            "zu": "isiZulu",
            "xh": "isiXhosa",
            "af": "Afrikaans",
            "ms": "Bahasa Melayu",
            "id": "Bahasa Indonesia",
            "tl": "Filipino",
            "jw": "Jawa",
            "su": "Sunda",
            "ceb": "Cebuano",
            "mg": "Malagasy",
            "ml": "മലയാളം",
            "ta": "தமிழ்",
            "te": "తెలుగు",
            "kn": "ಕನ್ನಡ",
            "mr": "मराठी",
            "gu": "ગુજરાતી",
            "pa": "ਪੰਜਾਬੀ",
            "bn": "বাংলা",
            "ur": "اردو",
            "fa": "فارسی",
            "ps": "پښتو",
            "sd": "سنڌي",
            "dv": "ދިވެހި",
            "ht": "Kreyòl Ayisyen",
            "haw": "ʻŌlelo Hawaiʻi",
            "sm": "Gagana Samoa",
            "mi": "Te Reo Māori",
            "fj": "Vosa Vakaviti",
            "ty": "Reo Tahiti",
            "rar": "Māori Kūki ʻĀirani"
        }

    def get_supported_methods(self) -> Dict[str, Dict[str, Any]]:
        """Lấy thông tin về các phương pháp dịch được hỗ trợ"""
        return {
            "google": {
                "name": "Google Translate",
                "description": "Dịch sử dụng Google Translate API",
                "free_tier": True,
                "rate_limit": "100 requests/second",
                "languages": "100+ languages"
            },
            "azure": {
                "name": "Azure Translator",
                "description": "Dịch sử dụng Azure Cognitive Services",
                "free_tier": True,
                "rate_limit": "Varies by tier",
                "languages": "100+ languages"
            },
            "aws": {
                "name": "AWS Translate",
                "description": "Dịch sử dụng Amazon Translate",
                "free_tier": True,
                "rate_limit": "Varies by region",
                "languages": "75+ languages"
            },
            "openrouter": {
                "name": "OpenRouter",
                "description": "Dịch sử dụng các mô hình LLM qua OpenRouter.ai",
                "free_tier": False,
                "rate_limit": "Varies by model",
                "languages": "Most languages"
            },
            "ollama": {
                "name": "Ollama",
                "description": "Dịch sử dụng mô hình LLM chạy trên server Ollama cục bộ",
                "free_tier": True,
                "rate_limit": "No limit",
                "languages": "Varies by model"
            },
            "local": {
                "name": "Local Model",
                "description": "Dịch sử dụng local MarianMT models",
                "free_tier": True,
                "rate_limit": "No limit",
                "languages": "Limited language pairs"
            }
        }

    async def check_service_availability(self, method: str = "google") -> bool:
        """
        Kiểm tra service có sẵn không

        Args:
            method: Phương pháp cần kiểm tra

        Returns:
            True nếu service có sẵn
        """
        try:
            if method.lower() == "google":
                from googletrans import Translator
                return True
            elif method.lower() == "azure":
                return all([
                    os.getenv("AZURE_TRANSLATOR_KEY"),
                    os.getenv("AZURE_TRANSLATOR_ENDPOINT"),
                    os.getenv("AZURE_TRANSLATOR_REGION")
                ])
            elif method.lower() == "aws":
                return all([
                    os.getenv("AWS_ACCESS_KEY_ID"),
                    os.getenv("AWS_SECRET_ACCESS_KEY")
                ])
            elif method.lower() == "openrouter":
                return os.getenv("OPENROUTER_API_KEY") is not None
            elif method.lower() == "ollama":
                try:
                    import httpx
                    async with httpx.AsyncClient() as client:
                        response = await client.get(os.getenv("OLLAMA_API_URL", "http://localhost:11434"))
                        return response.status_code == 200
                except Exception:
                    return False
            elif method.lower() == "local":
                try:
                    from transformers import MarianMTModel, MarianTokenizer
                    return True
                except ImportError:
                    return False
            else:
                return False
        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra service {method}: {str(e)}")
            return False

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
                        logger.info(f"Đã xóa file tạm translation: {file_path}")

            # Dọn dẹp trong models_dir
            for file_path in self.models_dir.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > (older_than_hours * 3600):
                        file_path.unlink()
                        logger.info(f"Đã xóa model file cũ: {file_path}")

        except Exception as e:
            logger.error(f"Lỗi khi dọn dẹp file tạm: {str(e)}")