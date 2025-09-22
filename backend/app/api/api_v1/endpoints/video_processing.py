"""
Video processing endpoints for AI dubbing
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
import uuid
import os
from pathlib import Path

from app.core.database import get_db
from app.core.exceptions import VideoProcessingException, FileUploadException
from app.core.config import settings
from app.models.job import Job, JobStatus
from app.services.main_service import MainService

router = APIRouter()


@router.post("/process", response_model=Dict[str, Any], summary="Process video for AI dubbing")
async def process_video(
    background_tasks: BackgroundTasks,
    video_file: Optional[UploadFile] = File(None),
    video_url: Optional[str] = Form(None),
    youtube_url: Optional[str] = Form(None),
    options: Optional[str] = Form(None),  # JSON string with processing options
    db = Depends(get_db)
):
    """Process a video file or URL for AI dubbing"""

    # Validate input
    if not video_file and not video_url and not youtube_url:
        raise HTTPException(
            status_code=400,
            detail="Either video_file, video_url, or youtube_url must be provided"
        )

    if video_file and (video_url or youtube_url):
        raise HTTPException(
            status_code=400,
            detail="Only one input method allowed (file, URL, or YouTube)"
        )

    # Validate file type if file upload
    video_input = None
    if video_file:
        if not video_file.filename:
            raise FileUploadException("No file selected")

        file_extension = Path(video_file.filename).suffix.lower()
        if file_extension not in settings.SUPPORTED_VIDEO_FORMATS:
            raise FileUploadException(
                f"Unsupported file format. Supported formats: {', '.join(settings.SUPPORTED_VIDEO_FORMATS)}"
            )

        # Check file size
        content = await video_file.read()
        file_size = len(content)
        await video_file.seek(0)  # Reset file pointer

        if file_size > settings.MAX_FILE_SIZE:
            raise FileUploadException(
                f"File too large. Maximum size: {settings.MAX_FILE_SIZE / (1024*1024):.0f}MB"
            )
        video_input = content
    else:
        video_input = youtube_url or video_url

    # Create job record
    job_id = str(uuid.uuid4())
    job = Job(
        job_id=job_id,
        status=JobStatus.PENDING,
        progress=0.0,
        input_type="file" if video_file else ("youtube" if youtube_url else "url"),
        input_filename=video_file.filename if video_file else None,
        processing_options=options if options else {}
    )

    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Start background processing
    main_service = MainService()
    background_tasks.add_task(main_service.process_video_dubbing, video_input=video_input)

    return {
        "job_id": job_id,
        "status": job.status,
        "message": "Video processing started",
        "estimated_time": "Processing time depends on video length and complexity"
    }


@router.get("/status/{job_id}", response_model=Dict[str, Any], summary="Get processing status")
async def get_processing_status(
    job_id: str,
    db = Depends(get_db)
):
    """Get the current status of a video processing job"""

    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "job_id": job.job_id,
        "status": job.status,
        "progress": job.progress,
        "message": job.message,
        "output_path": job.output_path
    }


@router.get("/download/{job_id}", summary="Download processed video")
async def download_processed_video(
    job_id: str,
    db = Depends(get_db)
):
    """Download the processed video file"""

    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != JobStatus.COMPLETED or not job.output_path:
        raise HTTPException(status_code=400, detail="Job is not completed or output path is missing")

    output_path = Path(job.output_path)
    if not output_path.is_file():
        raise HTTPException(status_code=404, detail="Processed file not found")

    return FileResponse(output_path, media_type="video/mp4", filename=output_path.name)


@router.post("/cancel/{job_id}", response_model=Dict[str, Any], summary="Cancel processing job")
async def cancel_processing_job(
    job_id: str,
    db = Depends(get_db)
):
    """Cancel a running video processing job"""

    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status not in [JobStatus.PENDING, JobStatus.PROCESSING]:
        raise HTTPException(status_code=400, detail="Job cannot be cancelled in its current state")

    job.status = JobStatus.CANCELLED
    await db.commit()

    return {
        "job_id": job_id,
        "status": "cancelled",
        "message": "Job cancelled successfully"
    }


@router.get("/supported-formats", response_model=Dict[str, Any], summary="Get supported formats")
async def get_supported_formats():
    """Get information about supported video formats and processing options"""

    return {
        "supported_video_formats": settings.SUPPORTED_VIDEO_FORMATS,
        "max_file_size_mb": settings.MAX_VIDEO_SIZE_MB,
        "processing_options": {
            "speech_recognition": {
                "enabled": True,
                "model": "FunASR",
                "languages": ["vi", "en"]
            },
            "translation": {
                "enabled": True,
                "target_language": "vi",
                "services": ["google", "azure"]
            },
            "text_to_speech": {
                "enabled": True,
                "voice": "vi-VN-NamMinhNeural",
                "speed": 1.0,
                "pitch": 0
            },
            "video_synthesis": {
                "enabled": True,
                "output_format": "mp4",
                "quality": "high"
            }
        }
    }