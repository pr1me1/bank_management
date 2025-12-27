import uuid
from typing import List

from starlette import status
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Query

from app.db import get_db
from app.dependencies import current_user_dep
from app.repo import GroupRepository
from app.schemas.responses import GroupResponse

router = APIRouter(prefix="/groups", tags=["Groups"])


@router.get("", response_model=List[GroupResponse])
def get_groups(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        db: Session = Depends(get_db),
):
    group_repo = GroupRepository(db)
    return group_repo.get_all(skip=skip, limit=limit)


@router.get("/{group_id}", response_model=GroupResponse)
def get_group(
        group_id: uuid.UUID,
        db: Session = Depends(get_db)
):
    """Get a group by ID."""
    group_repo = GroupRepository(db)
    group = group_repo.get_by_id(group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with ID {group_id} not found"
        )
    return group


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group(
        group_id: uuid.UUID,
        db: Session = Depends(get_db)
):
    """Delete a group."""
    group_repo = GroupRepository(db)
    success = group_repo.delete(group_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Group with ID {group_id} not found"
        )
    return None


__all__ = ['router']
