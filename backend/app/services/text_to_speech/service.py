"""
Text to Speech Service
Xử lý việc chuyển đổi text thành audio với nhiều voice khác nhau
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


class TextToSpeechService:
    """Service xử lý việc chuyển đổi text thành audio"""

    def __init__(self):
        self.temp_dir = Path(settings.TEMP_DIR)
        self.temp_dir.mkdir(exist_ok=True)
        self.models_dir = Path(settings.MODELS_DIR) / "text_to_speech"
        self.models_dir.mkdir(parents=True, exist_ok=True)

        # Cấu hình mặc định
        self.default_engine = "gtts"
        self.default_voice = "vi"
        self.default_speed = 1.0
        self.default_lang = "vi"

    async def text_to_speech(
        self,
        text: str,
        voice_name: str = "vi",
        engine: str = "gtts",
        speed: float = 1.0,
        output_path: Optional[str] = None,
        language: str = "vi"
    ) -> Dict[str, Any]:
        """
        Chuyển đổi text thành audio

        Args:
            text: Text cần chuyển đổi
            voice_name: Tên voice sử dụng
            engine: Engine sử dụng (gtts, pyttsx3, azure, aws, elevenlabs)
            speed: Tốc độ nói (0.5 - 2.0)
            output_path: Đường dẫn file output (nếu None thì tạo tự động)
            language: Ngôn ngữ

        Returns:
            Dict chứa thông tin audio được tạo
        """
        try:
            if not text.strip():
                raise VideoProcessingException("Text không được rỗng")

            logger.info(f"Bắt đầu TTS: {len(text)} ký tự với voice {voice_name} và engine {engine}")

            if engine.lower() == "gtts":
                return await self._tts_with_gtts(text, voice_name, speed, output_path, language)
            elif engine.lower() == "pyttsx3":
                return await self._tts_with_pyttsx3(text, voice_name, speed, output_path, language)
            elif engine.lower() == "azure":
                return await self._tts_with_azure(text, voice_name, speed, output_path, language)
            elif engine.lower() == "aws":
                return await self._tts_with_aws(text, voice_name, speed, output_path, language)
            elif engine.lower() == "elevenlabs":
                return await self._tts_with_elevenlabs(text, voice_name, speed, output_path, language)
            elif engine.lower() == "edgetts":
                return await self._tts_with_edgetts(text, voice_name, speed, output_path, language)
            else:
                raise VideoProcessingException(f"Engine không được hỗ trợ: {engine}")

        except Exception as e:
            logger.error(f"Lỗi khi TTS: {str(e)}")
            raise VideoProcessingException(f"Không thể chuyển đổi text thành audio: {str(e)}")

    async def _tts_with_edgetts(
        self,
        text: str,
        voice_name: str = "vi-VN-HoaiMyNeural",
        speed: float = 1.0,
        output_path: Optional[str] = None,
        language: str = "vi"
    ) -> Dict[str, Any]:
        """TTS sử dụng Edge-TTS"""
        try:
            import edge_tts
            import tempfile

            if not output_path:
                temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                output_path = temp_file.name
                temp_file.close()

            rate_str = f"{int((speed - 1.0) * 100)}%"
            communicate = edge_tts.Communicate(text, voice_name, rate=rate_str)
            await communicate.save(output_path)

            file_size = os.path.getsize(output_path)
            duration = self._get_audio_duration(output_path)

            result = {
                "success": True, "engine": "edgetts", "voice": voice_name,
                "language": language, "speed": speed, "output_path": output_path,
                "file_size": file_size, "duration": duration, "text_length": len(text),
                "text_preview": text[:100] + "..." if len(text) > 100 else text
            }
            logger.info(f"Đã tạo audio với Edge-TTS: {output_path}")
            return result
        except ImportError:
            logger.error("edge-tts chưa được cài đặt")
            raise VideoProcessingException("edge-tts chưa được cài đặt. Chạy: pip install edge-tts")
        except Exception as e:
            logger.error(f"Lỗi khi sử dụng Edge-TTS: {str(e)}")
            raise VideoProcessingException(f"Không thể TTS với Edge-TTS: {str(e)}")


    async def _tts_with_gtts(
        self,
        text: str,
        voice_name: str = "vi",
        speed: float = 1.0,
        output_path: Optional[str] = None,
        language: str = "vi"
    ) -> Dict[str, Any]:
        """TTS sử dụng Google Text-to-Speech"""
        try:
            from gtts import gTTS
            import pygame
            import tempfile

            # Tạo TTS object
            tts = gTTS(text=text, lang=language, slow=(speed < 1.0))

            # Tạo file tạm nếu không có output_path
            if not output_path:
                temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                output_path = temp_file.name
                temp_file.close()

            # Save audio
            tts.save(output_path)

            # Lấy thông tin file
            file_size = os.path.getsize(output_path)
            duration = self._get_audio_duration(output_path)

            result = {
                "success": True,
                "engine": "gtts",
                "voice": voice_name,
                "language": language,
                "speed": speed,
                "output_path": output_path,
                "file_size": file_size,
                "duration": duration,
                "text_length": len(text),
                "text_preview": text[:100] + "..." if len(text) > 100 else text
            }

            logger.info(f"Đã tạo audio với gTTS: {output_path}")
            return result

        except ImportError:
            logger.error("gtts chưa được cài đặt")
            raise VideoProcessingException("gtts chưa được cài đặt. Chạy: pip install gtts")
        except Exception as e:
            logger.error(f"Lỗi khi sử dụng gTTS: {str(e)}")
            raise VideoProcessingException(f"Không thể TTS với gTTS: {str(e)}")

    async def _tts_with_pyttsx3(
        self,
        text: str,
        voice_name: str = "vi",
        speed: float = 1.0,
        output_path: Optional[str] = None,
        language: str = "vi"
    ) -> Dict[str, Any]:
        """TTS sử dụng pyttsx3 (offline)"""
        try:
            import pyttsx3
            import tempfile

            # Khởi tạo engine
            engine = pyttsx3.init()

            # Cấu hình voice
            voices = engine.getProperty('voices')
            selected_voice = None

            # Tìm voice phù hợp
            for voice in voices:
                if voice_name.lower() in voice.name.lower():
                    selected_voice = voice
                    break

            if selected_voice:
                engine.setProperty('voice', selected_voice.id)

            # Cấu hình speed
            engine.setProperty('rate', int(200 * speed))  # Default rate is 200

            # Tạo file tạm nếu không có output_path
            if not output_path:
                temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                output_path = temp_file.name
                temp_file.close()

            # Save audio
            engine.save_to_file(text, output_path)
            engine.runAndWait()

            # Lấy thông tin file
            file_size = os.path.getsize(output_path)
            duration = self._get_audio_duration(output_path)

            result = {
                "success": True,
                "engine": "pyttsx3",
                "voice": voice_name,
                "language": language,
                "speed": speed,
                "output_path": output_path,
                "file_size": file_size,
                "duration": duration,
                "text_length": len(text),
                "text_preview": text[:100] + "..." if len(text) > 100 else text
            }

            logger.info(f"Đã tạo audio với pyttsx3: {output_path}")
            return result

        except ImportError:
            logger.error("pyttsx3 chưa được cài đặt")
            raise VideoProcessingException("pyttsx3 chưa được cài đặt. Chạy: pip install pyttsx3")
        except Exception as e:
            logger.error(f"Lỗi khi sử dụng pyttsx3: {str(e)}")
            raise VideoProcessingException(f"Không thể TTS với pyttsx3: {str(e)}")

    async def _tts_with_azure(
        self,
        text: str,
        voice_name: str = "vi",
        speed: float = 1.0,
        output_path: Optional[str] = None,
        language: str = "vi"
    ) -> Dict[str, Any]:
        """TTS sử dụng Azure Cognitive Services"""
        try:
            import os
            import tempfile
            from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, AudioConfig

            # Lấy credentials từ environment
            api_key = os.getenv("AZURE_SPEECH_KEY")
            region = os.getenv("AZURE_SPEECH_REGION")

            if not api_key or not region:
                raise VideoProcessingException("Azure Speech credentials chưa được cấu hình")

            # Cấu hình Azure Speech
            speech_config = SpeechConfig(subscription=api_key, region=region)
            speech_config.speech_synthesis_voice_name = voice_name

            # Cấu hình speed
            speech_config.speech_synthesis_rate = int((speed - 1.0) * 100)  # Convert to percentage

            # Tạo file tạm nếu không có output_path
            if not output_path:
                temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
                output_path = temp_file.name
                temp_file.close()

            # Cấu hình audio output
            audio_config = AudioConfig(filename=output_path)

            # Tạo synthesizer
            synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

            # Synthesize
            result = synthesizer.speak_text_async(text).get()

            if result.reason == 1:  # Succeeded
                # Lấy thông tin file
                file_size = os.path.getsize(output_path)
                duration = self._get_audio_duration(output_path)

                tts_result = {
                    "success": True,
                    "engine": "azure",
                    "voice": voice_name,
                    "language": language,
                    "speed": speed,
                    "output_path": output_path,
                    "file_size": file_size,
                    "duration": duration,
                    "text_length": len(text),
                    "text_preview": text[:100] + "..." if len(text) > 100 else text
                }

                logger.info(f"Đã tạo audio với Azure TTS: {output_path}")
                return tts_result
            else:
                raise VideoProcessingException(f"Azure TTS thất bại: {result.reason}")

        except ImportError:
            logger.error("azure-cognitiveservices-speech chưa được cài đặt")
            raise VideoProcessingException("azure-cognitiveservices-speech chưa được cài đặt. Chạy: pip install azure-cognitiveservices-speech")
        except Exception as e:
            logger.error(f"Lỗi khi sử dụng Azure TTS: {str(e)}")
            raise VideoProcessingException(f"Không thể TTS với Azure: {str(e)}")

    async def _tts_with_aws(
        self,
        text: str,
        voice_name: str = "vi",
        speed: float = 1.0,
        output_path: Optional[str] = None,
        language: str = "vi"
    ) -> Dict[str, Any]:
        """TTS sử dụng AWS Polly"""
        try:
            import boto3
            import tempfile

            # Lấy credentials từ environment
            aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
            aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
            aws_region = os.getenv("AWS_REGION", "us-east-1")

            if not aws_access_key or not aws_secret_key:
                raise VideoProcessingException("AWS credentials chưa được cấu hình")

            # Tạo Polly client
            polly_client = boto3.client(
                'polly',
                aws_access_key_id=aws_access_key,
                aws_secret_access_key=aws_secret_key,
                region_name=aws_region
            )

            # Tạo file tạm nếu không có output_path
            if not output_path:
                temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                output_path = temp_file.name
                temp_file.close()

            # Synthesize speech
            response = polly_client.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=voice_name,
                Engine='neural'  # Use neural engine for better quality
            )

            # Save audio
            if "AudioStream" in response:
                with open(output_path, 'wb') as file:
                    file.write(response['AudioStream'].read())

                # Lấy thông tin file
                file_size = os.path.getsize(output_path)
                duration = self._get_audio_duration(output_path)

                result = {
                    "success": True,
                    "engine": "aws",
                    "voice": voice_name,
                    "language": language,
                    "speed": speed,
                    "output_path": output_path,
                    "file_size": file_size,
                    "duration": duration,
                    "text_length": len(text),
                    "text_preview": text[:100] + "..." if len(text) > 100 else text
                }

                logger.info(f"Đã tạo audio với AWS Polly: {output_path}")
                return result
            else:
                raise VideoProcessingException("Không nhận được audio stream từ AWS")

        except ImportError:
            logger.error("boto3 chưa được cài đặt")
            raise VideoProcessingException("boto3 chưa được cài đặt. Chạy: pip install boto3")
        except Exception as e:
            logger.error(f"Lỗi khi sử dụng AWS Polly: {str(e)}")
            raise VideoProcessingException(f"Không thể TTS với AWS: {str(e)}")

    async def _tts_with_elevenlabs(
        self,
        text: str,
        voice_name: str = "vi",
        speed: float = 1.0,
        output_path: Optional[str] = None,
        language: str = "vi"
    ) -> Dict[str, Any]:
        """TTS sử dụng ElevenLabs"""
        try:
            import requests
            import tempfile

            # Lấy API key từ environment
            api_key = os.getenv("ELEVENLABS_API_KEY")

            if not api_key:
                raise VideoProcessingException("ElevenLabs API key chưa được cấu hình")

            # Tạo file tạm nếu không có output_path
            if not output_path:
                temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                output_path = temp_file.name
                temp_file.close()

            # API endpoint
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_name}"

            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": api_key
            }

            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5,
                    "style": 0.5,
                    "use_speaker_boost": True
                }
            }

            # Make request
            response = requests.post(url, json=data, headers=headers)

            if response.status_code == 200:
                # Save audio
                with open(output_path, 'wb') as file:
                    file.write(response.content)

                # Lấy thông tin file
                file_size = os.path.getsize(output_path)
                duration = self._get_audio_duration(output_path)

                result = {
                    "success": True,
                    "engine": "elevenlabs",
                    "voice": voice_name,
                    "language": language,
                    "speed": speed,
                    "output_path": output_path,
                    "file_size": file_size,
                    "duration": duration,
                    "text_length": len(text),
                    "text_preview": text[:100] + "..." if len(text) > 100 else text
                }

                logger.info(f"Đã tạo audio với ElevenLabs: {output_path}")
                return result
            else:
                raise VideoProcessingException(f"ElevenLabs API error: {response.status_code} - {response.text}")

        except ImportError:
            logger.error("requests chưa được cài đặt")
            raise VideoProcessingException("requests chưa được cài đặt. Chạy: pip install requests")
        except Exception as e:
            logger.error(f"Lỗi khi sử dụng ElevenLabs: {str(e)}")
            raise VideoProcessingException(f"Không thể TTS với ElevenLabs: {str(e)}")

    def _get_audio_duration(self, audio_path: str) -> float:
        """Lấy duration của audio file"""
        try:
            import subprocess
            import json

            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                audio_path
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                info = json.loads(result.stdout)
                return float(info['format'].get('duration', 0))
            else:
                return 0.0
        except Exception:
            return 0.0

    async def create_audio_from_segments(
        self,
        segments: List[Dict[str, Any]],
        voice_name: str = "vi",
        engine: str = "gtts",
        speed: float = 1.0,
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Tạo audio từ danh sách segments

        Args:
            segments: Danh sách segments với text và timing
            voice_name: Tên voice sử dụng
            engine: Engine sử dụng
            speed: Tốc độ nói
            output_path: Đường dẫn file output

        Returns:
            Dict chứa thông tin audio được tạo
        """
        try:
            if not segments:
                raise VideoProcessingException("Segments không được rỗng")

            logger.info(f"Bắt đầu tạo audio từ {len(segments)} segments")

            # Tạo audio cho từng segment
            segment_files = []
            total_duration = 0

            for i, segment in enumerate(segments):
                try:
                    # Tạo audio cho segment này
                    segment_text = segment.get("translated_text", segment.get("text", ""))
                    if not segment_text.strip():
                        continue

                    # Tạo file tạm cho segment
                    import tempfile
                    temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                    temp_path = temp_file.name
                    temp_file.close()

                    # TTS cho segment
                    result = await self.text_to_speech(
                        text=segment_text,
                        voice_name=voice_name,
                        engine=engine,
                        speed=speed,
                        output_path=temp_path
                    )

                    if result["success"]:
                        segment_files.append({
                            "file_path": result["output_path"],
                            "duration": result["duration"],
                            "start_time": segment.get("start", 0),
                            "end_time": segment.get("end", 0)
                        })
                        total_duration += result["duration"]

                except Exception as e:
                    logger.warning(f"Lỗi khi tạo audio cho segment {i}: {str(e)}")
                    continue

            if not segment_files:
                raise VideoProcessingException("Không thể tạo audio cho bất kỳ segment nào")

            # Ghép các audio segments thành một file
            if not output_path:
                import tempfile
                temp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
                output_path = temp_file.name
                temp_file.close()

            # Ghép audio files
            await self._concatenate_audio_files([s["file_path"] for s in segment_files], output_path)

            # Dọn dẹp temp files
            for segment_file in segment_files:
                try:
                    os.unlink(segment_file["file_path"])
                except:
                    pass

            # Lấy thông tin file cuối cùng
            file_size = os.path.getsize(output_path)
            duration = self._get_audio_duration(output_path)

            result = {
                "success": True,
                "engine": engine,
                "voice": voice_name,
                "speed": speed,
                "output_path": output_path,
                "file_size": file_size,
                "duration": duration,
                "segments_count": len(segment_files),
                "total_segments": len(segments)
            }

            logger.info(f"Đã tạo audio hoàn chỉnh từ segments: {output_path}")
            return result

        except Exception as e:
            logger.error(f"Lỗi khi tạo audio từ segments: {str(e)}")
            raise VideoProcessingException(f"Không thể tạo audio từ segments: {str(e)}")

    async def _concatenate_audio_files(self, input_files: List[str], output_path: str):
        """Ghép nhiều audio files thành một file"""
        try:
            import subprocess

            # Tạo file list cho ffmpeg
            list_file = output_path + '.txt'
            with open(list_file, 'w') as f:
                for input_file in input_files:
                    f.write(f"file '{input_file}'\n")

            # Chạy ffmpeg để ghép files
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', list_file,
                '-c', 'copy',
                output_path
            ]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            stdout, stderr = await process.communicate()

            # Dọn dẹp list file
            try:
                os.unlink(list_file)
            except:
                pass

            if process.returncode != 0:
                raise VideoProcessingException(f"Không thể ghép audio files: {stderr.decode()}")

        except Exception as e:
            logger.error(f"Lỗi khi ghép audio files: {str(e)}")
            raise VideoProcessingException(f"Không thể ghép audio files: {str(e)}")

    def get_supported_voices(self, engine: str = "gtts") -> Dict[str, Any]:
        """Lấy danh sách voices được hỗ trợ cho engine"""
        voices = {
            "gtts": {
                "vi": "Tiếng Việt",
                "en": "English",
                "ja": "日本語",
                "ko": "한국어",
                "fr": "Français",
                "de": "Deutsch",
                "es": "Español",
                "zh": "中文"
            },
            "pyttsx3": {
                "system": "System voices (depends on OS)"
            },
            "azure": {
                "vi-VN-HoaiMyNeural": "Tiếng Việt (Nữ)",
                "vi-VN-NamMinhNeural": "Tiếng Việt (Nam)",
                "en-US-JennyNeural": "English US (Female)",
                "en-US-GuyNeural": "English US (Male)",
                "ja-JP-NanamiNeural": "Japanese (Female)",
                "ko-KR-SunHiNeural": "Korean (Female)"
            },
            "aws": {
                "Joanna": "English US (Female)",
                "Matthew": "English US (Male)",
                "Ivy": "English US (Female, Child)",
                "Justin": "English US (Male, Child)",
                "Kendra": "English US (Female)",
                "Kimberly": "English US (Female)",
                "Salli": "English US (Female)",
                "Joey": "English US (Male)"
            },
            "elevenlabs": {
                "custom": "Custom voices (requires API key)"
            },
            "edgetts": {
                "vi-VN-HoaiMyNeural": "Tiếng Việt (Nữ - Hoài My)",
                "vi-VN-NamMinhNeural": "Tiếng Việt (Nam - Nam Minh)",
                "en-US-JennyNeural": "English US (Female)",
                "ja-JP-NanamiNeural": "Japanese (Female)"
            }
        }

        return voices.get(engine, {})

    def get_supported_engines(self) -> Dict[str, Dict[str, Any]]:
        """Lấy thông tin về các engines được hỗ trợ"""
        return {
            "edgetts": {
                "name": "Edge TTS",
                "description": "Free high-quality TTS from Microsoft Edge",
                "offline": False,
                "quality": "Excellent",
                "languages": "70+ languages",
                "free_tier": True
            },
            "gtts": {
                "name": "Google Text-to-Speech",
                "description": "Free TTS service từ Google",
                "offline": False,
                "quality": "Good",
                "languages": "50+ languages",
                "free_tier": True
            },
            "pyttsx3": {
                "name": "pyttsx3",
                "description": "Offline TTS sử dụng system voices",
                "offline": True,
                "quality": "Depends on system",
                "languages": "System languages",
                "free_tier": True
            },
            "azure": {
                "name": "Azure Cognitive Services",
                "description": "High-quality TTS từ Microsoft",
                "offline": False,
                "quality": "Excellent",
                "languages": "75+ languages",
                "free_tier": True
            },
            "aws": {
                "name": "AWS Polly",
                "description": "Neural TTS từ Amazon",
                "offline": False,
                "quality": "Excellent",
                "languages": "30+ languages",
                "free_tier": True
            },
            "elevenlabs": {
                "name": "ElevenLabs",
                "description": "AI-powered TTS với quality cao",
                "offline": False,
                "quality": "Excellent",
                "languages": "20+ languages",
                "free_tier": False
            }
        }

    async def check_engine_availability(self, engine: str = "gtts") -> bool:
        """
        Kiểm tra engine có sẵn không

        Args:
            engine: Engine cần kiểm tra

        Returns:
            True nếu engine có sẵn
        """
        try:
            if engine.lower() == "edgetts":
                import edge_tts
                return True
            elif engine.lower() == "gtts":
                from gtts import gTTS
                return True
            elif engine.lower() == "pyttsx3":
                import pyttsx3
                return True
            elif engine.lower() == "azure":
                import os
                return all([
                    os.getenv("AZURE_SPEECH_KEY"),
                    os.getenv("AZURE_SPEECH_REGION")
                ])
            elif engine.lower() == "aws":
                import os
                return all([
                    os.getenv("AWS_ACCESS_KEY_ID"),
                    os.getenv("AWS_SECRET_ACCESS_KEY")
                ])
            elif engine.lower() == "elevenlabs":
                import os
                return bool(os.getenv("ELEVENLABS_API_KEY"))
            else:
                return False
        except Exception as e:
            logger.error(f"Lỗi khi kiểm tra engine {engine}: {str(e)}")
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
                        logger.info(f"Đã xóa file tạm TTS: {file_path}")

            # Dọn dẹp trong models_dir
            for file_path in self.models_dir.glob("*"):
                if file_path.is_file():
                    file_age = current_time - file_path.stat().st_mtime
                    if file_age > (older_than_hours * 3600):
                        file_path.unlink()
                        logger.info(f"Đã xóa model file cũ: {file_path}")

        except Exception as e:
            logger.error(f"Lỗi khi dọn dẹp file tạm: {str(e)}")