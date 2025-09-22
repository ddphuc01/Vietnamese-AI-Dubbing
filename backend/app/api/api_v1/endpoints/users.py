"""
Users endpoints for user management
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.user import User
from app.core.exceptions import NotFoundException

router = APIRouter()


@router.get("/", response_model=List[dict], summary="List all users")
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """List all users"""

    query = select(User).offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()

    return [
        {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "last_login": user.last_login
        }
        for user in users
    ]


@router.get("/{user_id}", response_model=dict, summary="Get user by ID")
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific user by ID"""

    query = select(User).where(User.id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundException(f"User with ID {user_id} not found")

    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "last_login": user.last_login
    }


@router.get("/by-email/{email}", response_model=dict, summary="Get user by email")
async def get_user_by_email(
    email: str,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific user by email"""

    query = select(User).where(User.email == email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise NotFoundException(f"User with email {email} not found")

    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "full_name": user.full_name,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
        "created_at": user.created_at,
        "updated_at": user.updated_at,
        "last_login": user.last_login
    }


@router.get("/stats/summary", response_model=dict, summary="Get user statistics")
async def get_user_stats(db: AsyncSession = Depends(get_db)):
    """Get summary statistics for users"""

    # Count total users
    total_users_query = select(User)
    total_users_result = await db.execute(total_users_query)
    total_users = len(total_users_result.scalars().all())

    # Count active users
    active_users_query = select(User).where(User.is_active == True)
    active_users_result = await db.execute(active_users_query)
    active_users = len(active_users_result.scalars().all())

    # Count admin users
    admin_users_query = select(User).where(User.is_superuser == True)
    admin_users_result = await db.execute(admin_users_query)
    admin_users = len(admin_users_result.scalars().all())

    return {
        "total_users": total_users,
        "active_users": active_users,
        "inactive_users": total_users - active_users,
        "admin_users": admin_users,
        "regular_users": total_users - admin_users
    }