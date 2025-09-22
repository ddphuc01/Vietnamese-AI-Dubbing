# Vietnamese AI Dubbing 🌟

**Công cụ lồng tiếng video AI tự động sang tiếng Việt**

[![React](https://img.shields.io/badge/React-19.1.1-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)](https://fastapi.tiangolo.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8.2-blue.svg)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-yellow.svg)](https://python.org/)

## 🎯 Tính năng

- 🎥 **Xử lý video thông minh** - Upload video hoặc nhập URL từ YouTube, Vimeo
- 🎙️ **Nhận diện giọng nói** - Sử dụng FunASR để chuyển giọng nói thành văn bản
- 🌐 **Dịch tự động** - Dịch sang tiếng Việt với Google Translate, OpenRouter AI
- 🎵 **Tổng hợp giọng nói** - Sử dụng EdgeTTS với giọng tiếng Việt tự nhiên
- 📊 **Quản lý Jobs** - Theo dõi tiến độ xử lý video real-time
- 🎨 **Giao diện hiện đại** - React 19 + Mantine UI với dark mode
- 📱 **Responsive** - Hoạt động tốt trên mọi thiết bị
- ⚡ **Hiệu suất cao** - FastAPI backend với async processing

## 🚀 Cài đặt nhanh

### Yêu cầu hệ thống

- **Python 3.8+**
- **Node.js 18+**
- **Git**

### Cách 1: Chạy tự động (Khuyến nghị)

```bash
# Clone repository
git clone <repository-url>
cd vietnamese-ai-dubbing

# Chạy cả backend và frontend
python run_both.py
```

Sau đó truy cập:
- 🌐 **Frontend:** http://localhost:5173
- 🔧 **Backend API:** http://localhost:8000
- 📚 **API Docs:** http://localhost:8000/docs

### Cách 2: Chạy thủ công

#### Backend (FastAPI)

```bash
cd backend

# Tạo virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy server
python main.py
```

#### Frontend (React)

```bash
cd frontend

# Cài đặt dependencies
npm install

# Chạy development server
npm run dev
```

## 📁 Cấu trúc dự án

```
vietnamese-ai-dubbing/
├── backend/                    # FastAPI Backend
│   ├── main.py                # App entry point
│   ├── requirements.txt       # Python dependencies
│   └── app/
│       ├── api/              # API endpoints
│       ├── core/             # Core functionality
│       ├── models/           # Database models
│       ├── services/         # Business logic
│       └── utils/            # Utilities
├── frontend/  # React Frontend
│   ├── src/
│   │   ├── components/       # UI components
│   │   ├── pages/           # Page components
│   │   ├── api/             # API client
│   │   ├── store/           # State management
│   │   └── router/          # React Router
│   ├── package.json         # Node dependencies
│   └── vite.config.ts       # Vite configuration
├── run_both.py              # Script chạy cả 2 servers
└── README.md               # Tài liệu này
```

## 🎮 Cách sử dụng

### 1. Upload Video

- **Từ máy tính:** Kéo thả file video hoặc click để chọn
- **Từ URL:** Nhập URL từ YouTube, Vimeo, hoặc các nền tảng khác
- **Hỗ trợ:** MP4, AVI, MOV, MKV, WebM (tối đa 500MB)

### 2. Cấu hình xử lý

- **Giọng đọc:** Chọn giọng tiếng Việt (Nam Minh, Hoài My, Ngọc Lam...)
- **Cài đặt nâng cao:** Tốc độ, cao độ, âm lượng
- **Chất lượng:** 720p, 1080p, 4K

### 3. Xử lý

- Click "Lồng tiếng ngay" để bắt đầu
- Theo dõi tiến độ real-time
- Nhận thông báo khi hoàn thành

### 4. Tải kết quả

- Tải video hoàn chỉnh với audio tiếng Việt
- Tải riêng file audio nếu cần
- Chia sẻ trực tiếp từ ứng dụng

## 🔧 API Endpoints

### Health Check
- `GET /health` - Kiểm tra trạng thái server
- `GET /health/detailed` - Thông tin chi tiết
- `GET /health/ready` - Kiểm tra sẵn sàng

### Video Processing
- `POST /api/v1/video/process` - Bắt đầu xử lý video
- `GET /api/v1/video/status/{job_id}` - Trạng thái xử lý
- `GET /api/v1/video/download/{job_id}` - Tải video đã xử lý

### Job Management
- `GET /api/v1/jobs` - Danh sách jobs
- `GET /api/v1/jobs/{job_id}` - Chi tiết job
- `GET /api/v1/jobs/stats/summary` - Thống kê

## 🛠️ Development

### Backend Development

```bash
cd backend

# Cài đặt dev dependencies
pip install -r requirements-dev.txt

# Chạy tests
pytest

# Format code
black app/
isort app/

# Lint code
flake8 app/
mypy app/
```

### Frontend Development

```bash
cd frontend

# Type checking
npm run type-check

# Lint code
npm run lint

# Format code
npm run format
```

## 📦 Dependencies

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **Python-Multipart** - File uploads

### Frontend
- **React 19** - UI framework
- **TypeScript** - Type safety
- **Mantine** - UI components
- **Zustand** - State management
- **React Router** - Routing
- **Axios** - HTTP client

## 🚀 Deployment

### Docker

```bash
# Build và chạy với Docker Compose
docker-compose up --build
```

### Production

1. **Backend:** Deploy FastAPI với Gunicorn + Uvicorn
2. **Frontend:** Build React app và serve với Nginx
3. **Database:** Sử dụng PostgreSQL thay vì SQLite
4. **File Storage:** Cấu hình cloud storage (S3, GCS)

## 🤝 Đóng góp

Chúng tôi hoan nghênh mọi đóng góp!

1. Fork dự án
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 🙏 Lời cảm ơn

- **React Team** - React framework
- **FastAPI Team** - FastAPI framework
- **Mantine Team** - UI components
- **FunASR** - Speech recognition
- **EdgeTTS** - Text-to-speech
- **Cộng đồng AI Việt Nam** - Hỗ trợ và động viên

## 📞 Liên hệ

- **Email:** contact@vietnamese-ai-dubbing.com
- **GitHub:** github.com/vietnamese-ai-dubbing
- **Issues:** Tạo issue trên GitHub

---

**Vietnamese AI Dubbing** - Mang công nghệ AI đến với mọi người Việt Nam 🇻🇳