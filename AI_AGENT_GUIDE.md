# AI Agent Guide - Vietnamese AI Dubbing Project

## Tổng quan Dự án

Dự án này là một ứng dụng lồng tiếng AI tự động, chuyển đổi video từ tiếng Trung sang tiếng Việt. Dưới đây là hướng dẫn cho AI agents để hiểu và tiếp tục phát triển dự án.

## Cấu trúc Repository

### Frontend (React + TypeScript)
```
frontend/
├── src/
│   ├── components/    # UI Components
│   ├── hooks/        # Custom React hooks
│   ├── services/     # API services
│   ├── types/        # TypeScript definitions
│   └── utils/        # Utility functions
```

### Backend (Python)
```
backend/
├── app/
│   ├── api/         # API endpoints
│   ├── models/      # Data models
│   └── services/    # Business logic
└── modules/         # Core functionality modules
```

## Quy trình Xử lý

1. **Video Download**
   - Input: URL (YouTube/Bilibili/Douyin)
   - Output: Video file, audio, subtitles
   - Key files: `modules/downloader/`

2. **Voice Separation**
   - Model: htdemucs_ft
   - Input: Original audio
   - Output: Vocal & instrumental tracks
   - Key files: `modules/separator/`

3. **Speech Recognition**
   - Model: FunASR
   - Input: Vocal track
   - Output: JSON/SRT subtitles
   - Key files: `modules/recognition/`

4. **Translation**
   - Engines: GTX API, Openrouter.ai, Ollama
   - Input: Source subtitles
   - Output: Translated subtitles
   - Key files: `modules/translator/`

5. **Text-to-Speech**
   - Model: EdgeTTS (Vietnamese)
   - Input: Translated text
   - Output: Synthesized audio
   - Key files: `modules/tts/`

6. **Video Processing**
   - Input: Original video, new audio
   - Output: Final dubbed video
   - Key files: `modules/processor/`

## Hướng dẫn cho AI Agents

### 1. Tiếp cận Code
- Đọc `DEVELOPMENT_PLAN.md` trước
- Xem xét cấu trúc thư mục hiện tại
- Kiểm tra dependencies trong package.json và requirements.txt

### 2. Quy tắc Phát triển
- Tuân thủ TypeScript cho frontend
- Sử dụng Python type hints
- Viết unit tests cho mọi feature mới
- Cập nhật documentation khi thay đổi

### 3. Best Practices
- Sử dụng async/await cho các operations bất đồng bộ
- Implement error handling
- Optimize resource usage
- Follow SOLID principles

### 4. Testing
- Unit tests cho mỗi module
- Integration tests cho pipeline
- Test với nhiều loại input khác nhau

### 5. Debugging Guide
- Check logs trong `logs/`
- Sử dụng Python debugger
- React DevTools cho frontend
- Monitoring tools

### 6. Known Issues & Solutions
- Memory usage với large videos
- GPU optimization cho ML models
- Error handling trong pipeline
- Resource management

### 7. Performance Optimization
- Caching strategies
- Parallel processing
- Resource allocation
- Memory management

### 8. Security Considerations
- API authentication
- Input validation
- Resource limits
- Error handling

## Checkpoints cho AI Agents

1. **Trước khi bắt đầu**
   - [ ] Đã đọc toàn bộ documentation
   - [ ] Hiểu rõ cấu trúc project
   - [ ] Kiểm tra environment setup

2. **Trong quá trình phát triển**
   - [ ] Follow coding standards
   - [ ] Write tests
   - [ ] Update documentation
   - [ ] Handle errors appropriately

3. **Trước khi commit**
   - [ ] Tests pass
   - [ ] Linter checks pass
   - [ ] Documentation updated
   - [ ] Performance validated

## Resources & References

1. **Model Documentation**
   - FunASR: [Link]
   - EdgeTTS: [Link]
   - htdemucs_ft: [Link]

2. **API Documentation**
   - YouTube API
   - Bilibili API
   - Douyin API

3. **Libraries & Tools**
   - yt-dlp
   - FFmpeg
   - PyTorch
   - React