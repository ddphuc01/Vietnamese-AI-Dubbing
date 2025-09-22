"""
Jobs endpoints for managing video processing tasks
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.job import Job, JobStatus
from app.core.exceptions import NotFoundException

router = APIRouter()


@router.get("/", response_model=List[dict], summary="List all jobs")
async def list_jobs(
    status: Optional[JobStatus] = Query(None, description="Filter by job status"),
    user_id: Optional[str] = Query(None, description="Filter by user ID"),
    limit: int = Query(50, ge=1, le=100, description="Number of jobs to return"),
    offset: int = Query(0, ge=0, description="Number of jobs to skip"),
    db: AsyncSession = Depends(get_db)
):
    """List all video processing jobs with optional filtering"""

    # Build query
    query = select(Job).options(selectinload(Job.user))

    if status:
        query = query.where(Job.status == status)
    if user_id:
        query = query.where(Job.user_id == user_id)

    query = query.order_by(desc(Job.created_at)).offset(offset).limit(limit)

    result = await db.execute(query)
    jobs = result.scalars().all()

    return [
        {
            "id": job.id,
            "job_id": job.job_id,
            "status": job.status,
            "progress": job.progress,
            "input_type": job.input_type,
            "input_filename": job.input_filename,
            "output_filename": job.output_filename,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
            "started_at": job.started_at,
            "completed_at": job.completed_at,
            "processing_time": job.processing_time,
            "error_message": job.error_message
        }
        for job in jobs
    ]


@router.get("/{job_id}", response_model=dict, summary="Get job by ID")
async def get_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific job by its job_id"""

    query = select(Job).options(selectinload(Job.user)).where(Job.job_id == job_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        raise NotFoundException(f"Job with ID {job_id} not found")

    return {
        "id": job.id,
        "job_id": job.job_id,
        "status": job.status,
        "progress": job.progress,
        "input_type": job.input_type,
        "input_path": job.input_path,
        "input_filename": job.input_filename,
        "processing_options": job.processing_options,
        "output_path": job.output_path,
        "output_filename": job.output_filename,
        "error_message": job.error_message,
        "error_details": job.error_details,
        "created_at": job.created_at,
        "updated_at": job.updated_at,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
        "processing_time": job.processing_time,
        "file_size": job.file_size,
        "duration": job.duration,
        "metadata": job.metadata,
        "user_id": job.user_id
    }


@router.delete("/{job_id}", response_model=dict, summary="Delete job")
async def delete_job(
    job_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete a job by its job_id"""

    query = select(Job).where(Job.job_id == job_id)
    result = await db.execute(query)
    job = result.scalar_one_or_none()

    if not job:
        raise NotFoundException(f"Job with ID {job_id} not found")

    await db.delete(job)
    await db.commit()

    return {
        "message": f"Job {job_id} deleted successfully",
        "job_id": job_id
    }


@router.get("/stats/summary", response_model=dict, summary="Get job statistics")
async def get_job_stats(db: AsyncSession = Depends(get_db)):
    """Get summary statistics for all jobs"""

    # Count jobs by status
    status_counts = {}
    for status in JobStatus:
        query = select(Job).where(Job.status == status)
        result = await db.execute(query)
        count = len(result.scalars().all())
        status_counts[status.value] = count

    # Get total jobs
    total_jobs_query = select(Job)
    total_jobs_result = await db.execute(total_jobs_query)
    total_jobs = len(total_jobs_result.scalars().all())

    # Get average processing time for completed jobs
    completed_jobs_query = select(Job).where(
        and_(Job.status == JobStatus.COMPLETED, Job.processing_time.isnot(None))
    )
    completed_jobs_result = await db.execute(completed_jobs_query)
    completed_jobs = completed_jobs_result.scalars().all()

    avg_processing_time = None
    if completed_jobs:
        total_time = sum(job.processing_time for job in completed_jobs if job.processing_time)
        avg_processing_time = total_time / len(completed_jobs)

    return {
        "total_jobs": total_jobs,
        "status_counts": status_counts,
        "average_processing_time_seconds": avg_processing_time,
        "success_rate": (
            status_counts.get("completed", 0) / total_jobs * 100
            if total_jobs > 0 else 0
        )
    }