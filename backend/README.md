# Vietnamese AI Dubbing Backend

FastAPI backend for Vietnamese AI Dubbing system.

## Features

- 🚀 **FastAPI** - Modern, fast web framework for building APIs
- 📊 **SQLAlchemy** - Async database ORM
- 🔐 **Authentication** - JWT-based authentication system
- 📁 **File Upload** - Support for video file uploads
- 🎯 **Job Management** - Background job processing system
- 📈 **Progress Tracking** - Real-time job progress updates
- 🏥 **Health Checks** - Comprehensive health monitoring
- 📚 **OpenAPI Documentation** - Auto-generated API documentation

## Quick Start

### Prerequisites

- Python 3.8+
- SQLite (for development) or PostgreSQL (for production)

### Installation

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations:**
   ```bash
   # Database tables will be created automatically on startup
   ```

6. **Start the server:**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

### Alternative: Using uvicorn directly

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once the server is running, you can access:

- **Interactive API docs:** http://localhost:8000/docs
- **Alternative docs:** http://localhost:8000/redoc
- **OpenAPI schema:** http://localhost:8000/openapi.json

## Project Structure

```
backend/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── app/
│   ├── api/               # API routers
│   │   └── api_v1/
│   │       └── endpoints/ # API endpoints
│   ├── core/              # Core functionality
│   │   ├── config.py      # Configuration
│   │   ├── database.py    # Database setup
│   │   ├── exceptions.py  # Custom exceptions
│   │   └── logging.py     # Logging configuration
│   ├── models/            # Database models
│   │   ├── job.py         # Job model
│   │   └── user.py        # User model
│   ├── services/          # Business logic
│   │   └── video_processor.py
│   └── utils/             # Utility functions
│       └── file_handler.py
```

## Configuration

The application uses the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./vietnamese_ai_dubbing.db` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-change-in-production` |
| `DEBUG` | Enable debug mode | `True` |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins | `["http://localhost:3000"]` |

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black app/
isort app/

# Lint code
flake8 app/
mypy app/
```

### Database

For development, the app uses SQLite. For production, consider using PostgreSQL:

```bash
# PostgreSQL example
DATABASE_URL=postgresql://user:password@localhost/vietnamese_ai_dubbing
```

## API Endpoints

### Health Check
- `GET /health` - Basic health check
- `GET /health/detailed` - Detailed health check with database status
- `GET /health/ready` - Readiness check for load balancers

### Jobs
- `GET /api/v1/jobs` - List all jobs
- `GET /api/v1/jobs/{job_id}` - Get job details
- `DELETE /api/v1/jobs/{job_id}` - Delete job
- `GET /api/v1/jobs/stats/summary` - Get job statistics

### Video Processing
- `POST /api/v1/video/process` - Process video for AI dubbing
- `GET /api/v1/video/status/{job_id}` - Get processing status
- `GET /api/v1/video/download/{job_id}` - Download processed video
- `POST /api/v1/video/cancel/{job_id}` - Cancel processing job
- `GET /api/v1/video/supported-formats` - Get supported formats

### Users
- `GET /api/v1/users` - List all users
- `GET /api/v1/users/{user_id}` - Get user by ID
- `GET /api/v1/users/by-email/{email}` - Get user by email
- `GET /api/v1/users/stats/summary` - Get user statistics

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations

1. **Security:**
   - Change `SECRET_KEY` to a strong random value
   - Use HTTPS in production
   - Set `DEBUG=False`

2. **Database:**
   - Use PostgreSQL for production
   - Set up database backups
   - Configure connection pooling

3. **File Storage:**
   - Configure cloud storage (S3, GCS) for uploaded files
   - Set up cleanup jobs for temporary files

4. **Monitoring:**
   - Add logging to external service (ELK, DataDog)
   - Set up health check endpoints for load balancers
   - Monitor API performance and errors

## Contributing

1. Follow the existing code style
2. Write tests for new features
3. Update documentation as needed
4. Use meaningful commit messages

## License

This project is licensed under the MIT License.