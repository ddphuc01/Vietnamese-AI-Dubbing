"""
Health check endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.core.database import get_db
from app.core.config import settings

from app.services.main_service import MainService

router = APIRouter()
main_service = MainService()


@router.get("/", response_model=Dict[str, str])
def basic_health_check():
    """Basic health check"""
    return {"status": "ok"}


@router.get("/options", response_model=Dict[str, Any])
def get_processing_options():
    """Lấy tất cả các tùy chọn xử lý có sẵn"""
    try:
        return main_service.get_processing_options()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/detailed", summary="Detailed health check")
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check including database connectivity"""
    health_status = {
        "status": "healthy",
        "service": settings.SERVER_NAME,
        "version": "1.0.0",
        "database": "unknown",
        "checks": {}
    }

    # Check database connectivity
    try:
        await db.execute(text("SELECT 1"))
        health_status["database"] = "connected"
        health_status["checks"]["database"] = "✅ Database connection successful"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["database"] = "disconnected"
        health_status["checks"]["database"] = f"❌ Database connection failed: {str(e)}"

    # Add more health checks here as needed
    # - External API connectivity
    # - File system access
    # - Model availability
    # - etc.

    return health_status


@router.get("/ready", summary="Readiness check")
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness check for load balancers and orchestration systems"""
    try:
        # Basic database connectivity check
        await db.execute(text("SELECT 1"))

        return {
            "status": "ready",
            "message": "Service is ready to handle requests"
        }
    except Exception as e:
        return {
            "status": "not_ready",
            "message": f"Service is not ready: {str(e)}"
        }