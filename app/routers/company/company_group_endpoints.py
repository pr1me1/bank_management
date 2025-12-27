import uuid
from typing import List

from starlette import status
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException

from app.db import get_db
from app.dependencies import current_user_dep
from app.models import CompanyGroup
from app.repo import CompanyGroupRepository
from app.schemas.requests import CompanyGroupCreate
from app.schemas.responses import CompanyGroupResponse

router = APIRouter(prefix="/company-groups", tags=["Company Groups"])


@router.post("", response_model=CompanyGroupResponse, status_code=status.HTTP_201_CREATED)
def create_company_group(
        company_group: CompanyGroupCreate,
        db: Session = Depends(get_db)
):
    """Link a company to a group."""
    company_group_repo = CompanyGroupRepository(db)

    existing = company_group_repo.get_by_company_and_group(
        company_group.company_id,
        company_group.group_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This company is already linked to this group"
        )

    return company_group_repo.create(**company_group.model_dump())


@router.get("", response_model=List[CompanyGroupResponse])
def get_company_groups(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """Get all company groups with pagination."""
    company_group_repo = CompanyGroupRepository(db)
    return company_group_repo.get_all(skip=skip, limit=limit)


@router.get("/{company_group_id}", response_model=CompanyGroupResponse)
def get_company_group(
        company_group_id: uuid.UUID,
        db: Session = Depends(get_db)
):
    """Get a company group by ID."""
    company_group_repo = CompanyGroupRepository(db)
    company_group = company_group_repo.get_by_id(company_group_id)
    if not company_group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company group with ID {company_group_id} not found"
        )
    return company_group


@router.get("/company/{company_id}", response_model=List[CompanyGroupResponse])
def get_company_groups_by_company(
        company_id: uuid.UUID,
        db: Session = Depends(get_db)
):
    """Get all groups for a company."""
    company_group_repo = CompanyGroupRepository(db)
    return company_group_repo.get_by_company_id(company_id)


@router.get("/group/{group_id}", response_model=List[CompanyGroupResponse])
def get_company_groups_by_group(
        group_id: uuid.UUID,
        db: Session = Depends(get_db)
):
    """Get all companies for a group."""
    company_group_repo = CompanyGroupRepository(db)
    return company_group_repo.get_by_group_id(group_id)


@router.delete("/{company_group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company_group(
        company_group_id: uuid.UUID,
        db: Session = Depends(get_db)
):
    """Unlink a company from a group."""
    company_group_repo = CompanyGroupRepository(db)
    success = company_group_repo.delete(company_group_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company group with ID {company_group_id} not found"
        )
    return None


@router.post("/{company_id}/add-group", status_code=status.HTTP_201_CREATED)
def create_company_group(
        group_id: uuid.UUID,
        company_id: uuid.UUID,
        db: Session = Depends(get_db)
):
    existing = db.query(CompanyGroup).filter(
        CompanyGroup.group_id == group_id,
        CompanyGroup.company_id == company_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company already in this group"
        )

    new_relation = CompanyGroup(group_id=group_id, company_id=company_id)
    db.add(new_relation)
    db.commit()
    db.refresh(new_relation)

    return {"message": "success"}


__all__ = ['router']
