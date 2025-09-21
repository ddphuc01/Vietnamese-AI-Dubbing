#!/usr/bin/env python3
"""
Vietnamese AI Dubbing - Web UI với Gradio
Giao diện web đơn giản cho việc lồng tiếng video
"""

import gradio as gr
import os
from pathlib import Path
from main import VietnameseAIDubbing
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Khởi tạo dubbing instance
dubbing = VietnameseAIDubbing()

def process_video_gradio(video_input, translator_method, voice_name, output_name):
    """Function xử lý video cho Gradio interface"""

    def progress_callback(progress, message):
        # Update progress bar
        progress_bar = gr.Progress()
        progress_bar(progress/100, desc=message)
        return f"{progress:.1f}% - {message}"

    dubbing.set_progress_callback(progress_callback)

    # Validate inputs
    if video_input is None:
        return None, "❌ Vui lòng upload video hoặc nhập URL"

    # Xử lý input
    if isinstance(video_input, str) and video_input.startswith(('http://', 'https://')):
        video_path = video_input
    elif hasattr(video_input, 'name'):
        video_path = video_input.name
    else:
        return None, "❌ Input không hợp lệ"

    try:
        result = dubbing.process_video(
            video_input=video_path,
            translator_method=translator_method,
            voice_name=voice_name,
            output_name=output_name
        )

        if result["success"]:
            final_video = result["final_video"]
            subtitle_file = result["subtitle_file"]

            # Trả về video và message thành công
            return (
                final_video,
                f"✅ Hoàn thành!\n\n📹 Video: {os.path.basename(final_video)}\n📝 Phụ đề: {os.path.basename(subtitle_file)}"
            )
        else:
            return None, f"❌ Lỗi: {result['error']}"

    except Exception as e:
        logger.error(f"Lỗi xử lý: {str(e)}")
        return None, f"❌ Lỗi hệ thống: {str(e)}"

def preview_voice(voice_name):
    """Tạo preview audio cho voice"""
    try:
        preview_path = text_to_speech.preview_voice(voice_name)
        return preview_path
    except Exception as e:
        return f"❌ Lỗi tạo preview: {str(e)}"

# Tạo Gradio interface
def create_ui():
    """Tạo giao diện Gradio"""

    with gr.Blocks(
        title="Vietnamese AI Dubbing",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {
            max-width: 1200px;
            margin: auto;
        }
        .title {
            text-align: center;
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 1em;
            color: #2563eb;
        }
        """
    ) as interface:

        gr.HTML("""
        <div class="title">
            🎬 Vietnamese AI Dubbing<br>
            <small style="font-size: 0.6em; color: #666;">Công cụ lồng tiếng video tự động sang tiếng Việt</small>
        </div>
        """)

        with gr.Tabs():

            # Tab chính: Dubbing
            with gr.TabItem("🎥 Lồng tiếng Video"):

                with gr.Row():

                    with gr.Column(scale=1):

                        # Input section
                        gr.Markdown("### 📥 Input Video")

                        input_type = gr.Radio(
                            ["Upload File", "YouTube URL"],
                            label="Chọn loại input",
                            value="Upload File"
                        )

                        video_file = gr.File(
                            label="Upload Video",
                            file_types=[".mp4", ".avi", ".mov", ".mkv", ".webm"],
                            visible=True
                        )

                        video_url = gr.Textbox(
                            label="YouTube URL",
                            placeholder="https://www.youtube.com/watch?v=...",
                            visible=False
                        )

                        def toggle_input(input_type):
                            if input_type == "Upload File":
                                return gr.update(visible=True), gr.update(visible=False)
                            else:
                                return gr.update(visible=False), gr.update(visible=True)

                        input_type.change(
                            toggle_input,
                            inputs=input_type,
                            outputs=[video_file, video_url]
                        )

                        # Settings section
                        gr.Markdown("### ⚙️ Cài đặt")

                        translator_method = gr.Dropdown(
                            choices=settings.TRANSLATION_METHODS,
                            value=settings.DEFAULT_TRANSLATOR,
                            label="Phương thức dịch",
                            info="Chọn cách dịch: Google Translate (free), OpenRouter API, hoặc Ollama local"
                        )

                        voice_name = gr.Dropdown(
                            choices=settings.VIETNAMESE_VOICES,
                            value=settings.DEFAULT_VOICE,
                            label="Giọng đọc tiếng Việt",
                            info="Chọn giọng EdgeTTS cho tiếng Việt"
                        )

                        output_name = gr.Textbox(
                            label="Tên file output (tùy chọn)",
                            placeholder="video_dubbed_vi.mp4",
                            info="Để trống để dùng tên mặc định"
                        )

                        # Process button
                        process_btn = gr.Button(
                            "🚀 Bắt đầu lồng tiếng",
                            variant="primary",
                            size="lg"
                        )

                    with gr.Column(scale=1):

                        # Output section
                        gr.Markdown("### 📤 Kết quả")

                        output_video = gr.Video(
                            label="Video đã lồng tiếng",
                            interactive=False
                        )

                        status_text = gr.Textbox(
                            label="Trạng thái",
                            lines=5,
                            interactive=False,
                            placeholder="Chờ xử lý..."
                        )

                        # Preview voice section
                        gr.Markdown("### 🔊 Preview Giọng")
                        preview_btn = gr.Button("🎵 Nghe thử giọng", size="sm")
                        preview_audio = gr.Audio(
                            label="Audio Preview",
                            interactive=False
                        )

                # Event handlers
                process_btn.click(
                    process_video_gradio,
                    inputs=[video_file, translator_method, voice_name, output_name],
                    outputs=[output_video, status_text]
                ).then(
                    lambda: gr.update(value=""),
                    outputs=[],
                    js="() => {document.querySelector('video')?.load()}"
                )

                preview_btn.click(
                    preview_voice,
                    inputs=[voice_name],
                    outputs=[preview_audio]
                )

            # Tab: Thông tin
            with gr.TabItem("ℹ️ Thông tin"):

                gr.Markdown("""
                ## Vietnamese AI Dubbing

                Công cụ AI tự động lồng tiếng video sang tiếng Việt với chất lượng cao.

                ### Tính năng chính:
                - 🎥 **Tự động download** từ YouTube/TikTok
                - 🎵 **Tách vocals** khỏi background music
                - 🎤 **Nhận dạng giọng nói** với FunASR
                - 🌐 **Dịch đa phương thức** (Google, OpenRouter, Ollama)
                - 🔊 **Tổng hợp giọng** với EdgeTTS tiếng Việt
                - 🎬 **Ghép video final** với phụ đề

                ### Cách sử dụng:
                1. Upload video hoặc paste URL
                2. Chọn phương thức dịch và giọng đọc
                3. Click "Bắt đầu lồng tiếng"
                4. Tải video kết quả

                ### Lưu ý:
                - Video quá dài có thể tốn thời gian xử lý
                - Cần cấu hình API keys cho OpenRouter/Ollama
                - Kết quả phụ thuộc vào chất lượng audio gốc
                """)

                # Hiển thị available methods
                available_methods = translator.get_available_methods()
                gr.Markdown(f"**Phương thức dịch có sẵn:** {', '.join(available_methods)}")

            # Tab: Logs (nếu cần)
            with gr.TabItem("📋 Logs"):
                log_text = gr.Textbox(
                    label="Processing Logs",
                    lines=20,
                    interactive=False,
                    value="Logs sẽ hiển thị ở đây khi xử lý..."
                )

    return interface

def main():
    """Chạy web UI"""
    interface = create_ui()

    # Launch với settings
    interface.queue(max_size=10)  # Queue để xử lý nhiều request
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,  # Set True để public URL
        show_error=True,
        quiet=False
    )

if __name__ == "__main__":
    main()