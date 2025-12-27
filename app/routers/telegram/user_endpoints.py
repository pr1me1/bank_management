from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from starlette import status

from app.db import get_db
from app.dependencies import current_user_dep
from app.repo import UserRepository
from app.schemas.responses import UserResponse
from app.schemas.requests import UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(
        user: UserCreate,
        db: Session = Depends(get_db)
):
    """Create a new user."""
    user_repo = UserRepository(db)

    existing = user_repo.get_by_telegram_id(user.telegram_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with telegram_id {user.telegram_id} already exists"
        )

    return user_repo.create(**user.model_dump())


@router.get("", response_model=List[UserResponse])
def get_users(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        db: Session = Depends(get_db)
):
    """Get all users with pagination."""
    user_repo = UserRepository(db)
    return user_repo.get_all(skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
        user_id: int,
        db: Session = Depends(get_db)
):
    """Get a user by ID."""
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user


@router.get("/telegram/{telegram_id}", response_model=UserResponse)
def get_user_by_telegram_id(
        telegram_id: int,
        db: Session = Depends(get_db)
):
    """Get a user by Telegram ID."""
    user_repo = UserRepository(db)
    user = user_repo.get_by_telegram_id(telegram_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with telegram_id {telegram_id} not found"
        )
    return user


@router.get("/username/{username}", response_model=UserResponse)
def get_user_by_username(
        username: str,
        db: Session = Depends(get_db)
):
    """Get a user by username."""
    user_repo = UserRepository(db)
    user = user_repo.get_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with username {username} not found"
        )
    return user


@router.get("/search/name", response_model=List[UserResponse])
def search_users_by_name(
        search_term: str = Query(..., description="Search term for first or last name"),
        limit: int = Query(10, ge=1, le=100),
        db: Session = Depends(get_db)
):
    """Search users by first name or last name."""
    user_repo = UserRepository(db)
    return user_repo.search_by_name(search_term, limit=limit)


@router.put("/{user_id}", response_model=UserResponse)
def update_user(
        user_id: int,
        user_update: UserUpdate,
        db: Session = Depends(get_db)
):
    """Update a user."""
    user_repo = UserRepository(db)
    user = user_repo.update(user_id, **user_update.model_dump(exclude_unset=True))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
        user_id: int,
        db: Session = Depends(get_db)
):
    """Delete a user."""
    user_repo = UserRepository(db)
    success = user_repo.delete(user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found"
        )
    return None


__all__ = ['router']
