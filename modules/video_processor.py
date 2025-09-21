import os
from pathlib import Path
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
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
            video = VideoFileClip(video_path)

            # Load Vietnamese audio
            viet_audio = AudioFileClip(vietnamese_audio_path)

            # Mix audios if background exists
            if background_audio_path and os.path.exists(background_audio_path):
                bg_audio = AudioFileClip(background_audio_path)

                # Mix Vietnamese audio với background
                # Giả sử Vietnamese audio là main, background là phụ
                mixed_audio = CompositeAudioClip([
                    viet_audio.set_duration(video.duration),
                    bg_audio.set_duration(video.duration).set_volume(0.3)  # Background nhỏ hơn
                ])
            else:
                mixed_audio = viet_audio.set_duration(video.duration)

            # Set audio cho video
            video = video.set_audio(mixed_audio)

            # Burn subtitles nếu có
            if subtitle_path and os.path.exists(subtitle_path):
                logger.info("Đang burn subtitles vào video...")
                # MoviePy có thể add text clips, nhưng phức tạp
                # Sử dụng ffmpeg cho stable hơn
                video = self._burn_subtitles(video, subtitle_path)

            # Tạo output filename
            if output_filename is None:
                base_name = Path(video_path).stem
                output_filename = f"{base_name}_vietnamese_dubbed.mp4"

            output_path = self.output_dir / output_filename

            # Export video
            logger.info(f"Đang export video final: {output_path}")
            video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                temp_audiofile=str(self.temp_dir / "temp_audio.m4a"),
                remove_temp=True,
                fps=24
            )

            # Cleanup
            video.close()
            viet_audio.close()
            if background_audio_path:
                bg_audio.close()

            logger.info(f"Đã tạo video final thành công: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Lỗi kết hợp video: {str(e)}")
            raise Exception(f"Không thể tạo video final: {str(e)}")

    def _burn_subtitles(self, video_clip, subtitle_path: str):
        """Burn subtitles vào video sử dụng ffmpeg"""
        try:
            # Sử dụng ffmpeg để burn subtitles
            import subprocess

            # Tạo temp video path
            temp_video = self.temp_dir / "temp_video_with_subs.mp4"

            # FFmpeg command để burn subtitles
            cmd = [
                'ffmpeg',
                '-i', str(video_clip.filename),  # Input video
                '-vf', f"subtitles={subtitle_path}:force_style='FontSize=24,PrimaryColour=&HFFFFFF&,OutlineColour=&H000000&'",
                '-c:v', 'libx264',
                '-c:a', 'copy',
                '-y',  # Overwrite
                str(temp_video)
            ]

            subprocess.run(cmd, check=True, capture_output=True)

            # Load video mới với subtitles
            return VideoFileClip(str(temp_video))

        except Exception as e:
            logger.warning(f"Không thể burn subtitles: {str(e)}, tiếp tục without subtitles")
            return video_clip

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

    def optimize_video(self, video_path: str, target_size_mb: int = None,
                      target_resolution: tuple = None) -> str:
        """Tối ưu video: giảm size, resolution nếu cần

        Args:
            video_path: Video input
            target_size_mb: Kích thước mục tiêu (MB)
            target_resolution: Resolution mục tiêu (width, height)

        Returns:
            str: Đường dẫn video optimized
        """
        try:
            video = VideoFileClip(video_path)

            # Resize nếu cần
            if target_resolution:
                width, height = target_resolution
                video = video.resize(width=width, height=height)

            # Tạo output filename
            base_name = Path(video_path).stem
            output_filename = f"{base_name}_optimized.mp4"
            output_path = self.output_dir / output_filename

            # Export với compression
            video.write_videofile(
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                bitrate='800k',  # Low bitrate for smaller size
                fps=24,
                preset='medium'
            )

            video.close()

            logger.info(f"Đã optimize video: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Lỗi optimize video: {str(e)}")
            return video_path

# Global instance
video_processor = VideoProcessor()