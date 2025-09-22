"""
Database configuration and connection management
"""

import asyncio
import logging
from typing import Generator, AsyncGenerator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


# Create sync engine for SQLite
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    poolclass=StaticPool if settings.DATABASE_URL.startswith("sqlite") else None,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

# Create sync session factory
session_factory = sessionmaker(
    bind=engine,
    expire_on_commit=False
)

# Create async engine for SQLite
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://"),
    echo=settings.DEBUG,
    future=True,
    poolclass=StaticPool if settings.DATABASE_URL.startswith("sqlite") else None,
    connect_args={"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

# Create async session factory
async_session_factory = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database - create tables if they don't exist"""
    try:
        async with async_engine.begin() as conn:
            # Import all models here to ensure they are registered
            from app.models import job, user  # noqa: F401

            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize database: {e}")
        raise


async def close_db() -> None:
    """Close database connections"""
    try:
        await async_engine.dispose()
        logger.info("✅ Database connections closed")
    except Exception as e:
        logger.error(f"❌ Error closing database connections: {e}")


async def reset_db() -> None:
    """Reset database - drop all tables and recreate them"""
    try:
        async with async_engine.begin() as conn:
            # Import all models here to ensure they are registered
            from app.models import job, user  # noqa: F401

            # Drop all tables
            await conn.run_sync(Base.metadata.drop_all)
            # Recreate all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Database reset successfully")
    except Exception as e:
        logger.error(f"❌ Failed to reset database: {e}")
        raise


# Test database connection
async def test_db_connection() -> bool:
    """Test database connection"""
    try:
        async with async_session_factory() as session:
            await session.execute("SELECT 1")
            return True
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False