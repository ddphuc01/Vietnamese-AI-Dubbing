"""
Main API router for version 1
"""

from fastapi import APIRouter

from app.api.api_v1.endpoints import jobs, health, video_processing, users


# Create main API router
api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)

api_router.include_router(
    jobs.router,
    prefix="/jobs",
    tags=["jobs"]
)

api_router.include_router(
    video_processing.router,
    prefix="/video",
    tags=["video-processing"]
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"]
)