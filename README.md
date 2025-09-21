# 🎬 Vietnamese AI Dubbing

<div align="center">
  <h1>Vietnamese AI Dubbing</h1>
  <p><strong>🎯 Công cụ AI lồng tiếng video tự động sang tiếng Việt</strong></p>
  <p><em>"AI Empowerment, Language Without Borders"</em></p>

  [![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
  [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
  [![Gradio](https://img.shields.io/badge/Gradio-4.0+-orange.svg)](https://gradio.app/)

  <img src="https://img.shields.io/badge/YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white" />
  <img src="https://img.shields.io/badge/TikTok-000000?style=for-the-badge&logo=tiktok&logoColor=white" />
</div>

---

## 📖 Giới thiệu

**Vietnamese AI Dubbing** là một công cụ AI tiên tiến cho việc lồng tiếng video tự động sang tiếng Việt. Sử dụng các công nghệ AI hiện đại như:

- 🎤 **FunASR** cho nhận dạng giọng nói tiếng Việt
- 🌐 **Google Translate / OpenRouter / Ollama** cho dịch thuật
- 🔊 **EdgeTTS** cho tổng hợp giọng nói tiếng Việt tự nhiên
- 🎵 **Demucs** cho tách vocals khỏi background music
- 🎬 **MoviePy** cho xử lý video chuyên nghiệp

### ✨ Tính năng chính

- 🚀 **Tự động hóa hoàn toàn**: Upload video → Nhận video lồng tiếng tiếng Việt
- 📺 **Hỗ trợ nhiều nguồn**: YouTube, TikTok, upload file trực tiếp
- 🎯 **Chất lượng cao**: Sử dụng models AI tiên tiến nhất
- 🌍 **Đa phương thức dịch**: Google Translate (free), OpenRouter API, Ollama local
- 🎭 **Nhiều giọng đọc**: Đa dạng giọng EdgeTTS tiếng Việt
- 📝 **Phụ đề tự động**: Tạo subtitle file .srt
- ⚡ **Xử lý nhanh**: Tối ưu cho video ngắn đến trung bình

---

## 🎯 Demo

![Demo GIF](demo.gif)

*Video demo sẽ được cập nhật sau*

---

## 🛠️ Cài đặt

### Yêu cầu hệ thống

- **Python**: 3.8 hoặc cao hơn
- **RAM**: Tối thiểu 8GB (16GB khuyến nghị)
- **GPU**: NVIDIA GPU với CUDA 11.0+ (khuyến nghị cho tốc độ)
- **Disk**: 10GB free space cho models và temp files

### 1. Clone repository

```bash
git clone https://github.com/your-username/Vietnamese-AI-Dubbing.git
cd Vietnamese-AI-Dubbing
```

### 2. Tạo môi trường ảo

```bash
# Tạo conda environment
conda create -n vi-dubbing python=3.10 -y
conda activate vi-dubbing

# Hoặc sử dụng venv
python -m venv vi-dubbing
source vi-dubbing/bin/activate  # Linux/Mac
# hoặc vi-dubbing\Scripts\activate  # Windows
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình môi trường

```bash
# Copy file config mẫu
cp .env.example .env

# Edit .env file với thông tin của bạn
nano .env  # hoặc notepad .env
```

**Nội dung .env cần thiết:**

```env
# OpenRouter API (tùy chọn, cho dịch chất lượng cao)
OPENROUTER_API_KEY=your_openrouter_key_here
OPENROUTER_MODEL=microsoft/wizardlm-2-8x22b

# Ollama (tùy chọn, cho dịch local)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Cài đặt mặc định
DEFAULT_TRANSLATOR=gtx_free
DEFAULT_VOICE=vi-VN-HoaiMyNeural
TEMP_DIR=./temp
OUTPUT_DIR=./output
```

### 5. Download models (tự động khi chạy lần đầu)

Models sẽ được download tự động khi bạn chạy ứng dụng lần đầu. Hoặc chạy manual:

```bash
# Download FunASR model
python -c "from modules.speech_recognition import speech_recognizer; speech_recognizer._init_model()"

# Download Demucs model (sẽ download khi sử dụng)
```

---

## 🚀 Sử dụng

### Web UI (Khuyến nghị)

```bash
python webui.py
```

Truy cập: http://localhost:7860

### Command Line

```bash
# Basic usage
python main.py "https://www.youtube.com/watch?v=VIDEO_ID"

# Với tùy chọn
python main.py "path/to/video.mp4" --translator openrouter --voice vi-VN-NamMinhNeural --output my_video_dubbed.mp4
```

### Python API

```python
from main import VietnameseAIDubbing

dubbing = VietnameseAIDubbing()

result = dubbing.process_video(
    video_input="https://www.youtube.com/watch?v=VIDEO_ID",
    translator_method="gtx_free",
    voice_name="vi-VN-HoaiMyNeural"
)

if result["success"]:
    print(f"Video hoàn thành: {result['final_video']}")
    print(f"Phụ đề: {result['subtitle_file']}")
```

---

## ⚙️ Cấu hình chi tiết

### Phương thức dịch

| Method | Ưu điểm | Nhược điểm | Yêu cầu |
|--------|---------|------------|---------|
| `gtx_free` | Miễn phí, nhanh | Giới hạn rate, chất lượng trung bình | Không |
| `openrouter` | Chất lượng cao, nhiều model | Cần API key, có phí | OpenRouter API key |
| `ollama` | Local, không phụ thuộc internet | Cần setup Ollama, chậm hơn | Ollama server |

### Giọng đọc tiếng Việt

- `vi-VN-HoaiMyNeural` (Female, default)
- `vi-VN-NamMinhNeural` (Male)
- `vi-VN-HoaiMyNeural` (Female alternative)

### Tham số nâng cao

Chỉnh sửa trong `config/settings.py`:

```python
# Thư mục
TEMP_DIR = "./temp"          # Files tạm thời
OUTPUT_DIR = "./output"      # Kết quả final

# Model settings
ASR_MODEL = "funasr"         # Speech recognition
TTS_ENGINE = "edge-tts"      # Text-to-speech
SEPARATOR_MODEL = "htdemucs_ft"  # Audio separation
```

---

## 📋 Workflow chi tiết

1. **📥 Input Processing**: Download video từ URL hoặc xử lý file upload
2. **🎵 Audio Extraction**: Tách audio từ video gốc
3. **🎤 Vocal Separation**: Sử dụng Demucs tách vocals khỏi background
4. **🎯 Speech Recognition**: FunASR chuyển audio thành text với timestamps
5. **🌐 Translation**: Dịch text sang tiếng Việt (fallback system)
6. **🔊 Text-to-Speech**: EdgeTTS tạo audio tiếng Việt
7. **🎬 Video Composition**: Ghép audio mới vào video gốc
8. **📝 Subtitle Generation**: Tạo file phụ đề .srt

---

## 🐛 Troubleshooting

### Lỗi thường gặp

**1. "CUDA out of memory"**
```bash
# Giảm batch size hoặc sử dụng CPU
export CUDA_VISIBLE_DEVICES=""
```

**2. "OpenRouter API key invalid"**
- Kiểm tra API key trong .env
- Đảm bảo có đủ credits

**3. "FunASR model download failed"**
```bash
# Manual download
pip install modelscope
modelscope download --model funasr models/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch
```

**4. Video quá dài (>30 phút)**
- Chia nhỏ video trước khi xử lý
- Sử dụng settings để giới hạn duration

### Logs và Debug

```bash
# Xem logs chi tiết
tail -f temp/vietnamese_dubbing.log

# Chạy với debug mode
python -c "import logging; logging.basicConfig(level=logging.DEBUG)" && python main.py video.mp4
```

---

## 🤝 Đóng góp

Chúng tôi hoan nghênh mọi đóng góp!

1. Fork repository
2. Tạo feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Tạo Pull Request

### Phát triển

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black .
isort .
```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

## 🙏 Credits

- **FunASR**: https://github.com/alibaba-damo-academy/FunASR
- **EdgeTTS**: https://github.com/rany2/edge-tts
- **Demucs**: https://github.com/facebookresearch/demucs
- **MoviePy**: https://github.com/Zulko/moviepy
- **Gradio**: https://github.com/gradio-app/gradio

---

## 📞 Liên hệ

- **GitHub Issues**: [Báo lỗi/đề xuất](https://github.com/your-username/Vietnamese-AI-Dubbing/issues)
- **Discord**: *Link sẽ được cập nhật*
- **Email**: your-email@example.com

---

## 🏆 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=your-username/Vietnamese-AI-Dubbing&type=Date)](https://star-history.com/#your-username/Vietnamese-AI-Dubbing&Date)

---

<div align="center">
  <p><strong>Made with ❤️ for the Vietnamese AI community</strong></p>
  <p>
    <a href="#vietnamese-ai-dubbing">Về đầu trang</a> •
    <a href="#-cài-đặt">Cài đặt</a> •
    <a href="#-sử-dụng">Sử dụng</a> •
    <a href="#-troubleshooting">Troubleshooting</a>
  </p>
</div>