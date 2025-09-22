import os
from pathlib import Path
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class VideoProcessor:
    """Module xử lý video final: combine audio mới với video gốc"""

    def __init__(self):
        self.temp_dir = Path(settings.TEMP_DIR)
        self.output_dir = Path(settings.OUTPUT_DIR)

    def combine_audio_video(self, video_path: str, vietnamese_audio_path: str,
                           background_audio_path: str = None,
                           subtitle_path: str = None,
                           output_filename: str = None) -> str:
        """Kết hợp audio tiếng Việt với video gốc

        Args:
            video_path: Đường dẫn video gốc
            vietnamese_audio_path: Audio tiếng Việt đã tạo
            background_audio_path: Background music (optional)
            subtitle_path: File subtitle (optional)
            output_filename: Tên file output (optional)

        Returns:
            str: Đường dẫn video final
        """
        try:
            logger.info("Đang kết hợp video và audio...")

            # Load video
            logger.info(f"Loading video: {video_path}")
            video = VideoFileClip(video_path)
            logger.info("Video loaded successfully")

            # Load Vietnamese audio
            logger.info(f"Loading Vietnamese audio: {vietnamese_audio_path}")
            viet_audio = AudioFileClip(vietnamese_audio_path)
            logger.info("Vietnamese audio loaded successfully")

            # Mix audios if background exists
            if background_audio_path and os.path.exists(background_audio_path):
                logger.info(f"Loading background audio: {background_audio_path}")
                bg_audio = AudioFileClip(background_audio_path)
                logger.info("Background audio loaded successfully")

                # Mix Vietnamese audio với background
                logger.info("Mixing Vietnamese audio với background music")
                mixed_audio = CompositeAudioClip([
                    viet_audio,
                    bg_audio
                ])
                logger.info("Audio mixing completed")
            else:
                logger.info("No background audio, using Vietnamese audio only")
                mixed_audio = viet_audio

            # Set audio cho video
            logger.info("Setting mixed audio to video")
            video = video.with_audio(mixed_audio)
            logger.info("Audio set to video successfully")

            # Tạo output filename
            if output_filename is None:
                base_name = Path(video_path).stem
                output_filename = f"{base_name}_vietnamese_dubbed.mp4"
                logger.info(f"Generated output filename: {output_filename}")

            output_path = self.output_dir / output_filename
            logger.info(f"Output path: {output_path}")

            # Export video
            logger.info(f"Đang export video final: {output_path}")
            video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                fps=24
            )

            # Cleanup
            logger.info("Cleaning up resources")
            video.close()
            viet_audio.close()
            if background_audio_path:
                bg_audio.close()
            logger.info("Cleanup completed")

            logger.info(f"Đã tạo video final thành công: {output_path}")

            return str(output_path)

        except Exception as e:
            logger.error(f"Lỗi kết hợp video: {str(e)}")
            raise Exception(f"Không thể tạo video final: {str(e)}")

    def add_soft_subtitles(self, video_path: str, subtitle_path: str,
                          output_filename: str = None) -> str:
        """Thêm soft subtitles (không burn vào video)

        Args:
            video_path: Video gốc
            subtitle_path: File subtitle
            output_filename: Tên output

        Returns:
            str: Đường dẫn video với subtitles
        """
        try:
            # Với soft subtitles, chỉ cần copy video và subtitle cùng folder
            if output_filename is None:
                base_name = Path(video_path).stem
                output_filename = f"{base_name}_with_subs.mp4"

            output_path = self.output_dir / output_filename

            # Copy video
            import shutil
            shutil.copy2(video_path, output_path)

            # Copy subtitle file cùng tên
            sub_output = self.output_dir / f"{Path(output_filename).stem}.srt"
            shutil.copy2(subtitle_path, sub_output)

            logger.info(f"Đã thêm soft subtitles: {sub_output}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Lỗi thêm soft subtitles: {str(e)}")
            raise

# Global instance
video_processor = VideoProcessor()