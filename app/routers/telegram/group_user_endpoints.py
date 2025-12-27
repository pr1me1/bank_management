from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from starlette import status

from app.db import get_db
from app.dependencies import current_user_dep
from app.models.telegram.group_users import GroupRole
from app.repo import GroupUserRepository
from app.schemas.responses.models.group_user_responses import GroupUserResponse

router = APIRouter(prefix="/group-users", tags=["Group Users"])


@router.get("", response_model=List[GroupUserResponse])
def get_group_users(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        db: Session = Depends(get_db)
):
    """Get all group users with pagination."""
    group_user_repo = GroupUserRepository(db)
    return group_user_repo.get_all(skip=skip, limit=limit)


@router.get("/{group_user_id}", response_model=GroupUserResponse)
def get_group_user(
        group_user_id: int,
        db: Session = Depends(get_db)
):
    """Get a group user by ID."""
    group_user_repo = GroupUserRepository(db)
    group_user = group_user_repo.get_by_id(group_user_id)
    if not group_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group user with ID {group_user_id} not found"
        )
    return group_user


@router.get("/group/{group_id}", response_model=List[GroupUserResponse])
def get_group_users_by_group(
        group_id: int,
        db: Session = Depends(get_db)
):
    """Get all users in a group."""
    group_user_repo = GroupUserRepository(db)
    return group_user_repo.get_by_group_id(group_id)


@router.get("/user/{user_id}", response_model=List[GroupUserResponse])
def get_group_users_by_user(
        user_id: int,
        db: Session = Depends(get_db)
):
    """Get all groups for a user."""
    group_user_repo = GroupUserRepository(db)
    return group_user_repo.get_by_user_id(user_id)


@router.get("/group/{group_id}/role/{role}", response_model=List[GroupUserResponse])
def get_group_users_by_role(
        group_id: int,
        role: GroupRole,
        db: Session = Depends(get_db)
):
    """Get all users with a specific role in a group."""
    group_user_repo = GroupUserRepository(db)
    return group_user_repo.get_by_role(group_id, role)


@router.delete("/{group_user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group_user(
        group_user_id: int,
        db: Session = Depends(get_db)
):
    """Delete a group user relationship."""
    group_user_repo = GroupUserRepository(db)
    success = group_user_repo.delete(group_user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group user with ID {group_user_id} not found"
        )
    return None


__all__ = ['router']
