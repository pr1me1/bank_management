from typing import List

from starlette import status
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Query

from app.db import get_db
from app.dependencies import current_user_dep
from app.repo import CompanyCounteragentRepository
from app.schemas.responses import CompanyCounteragentResponse
from app.schemas.requests import (
    CompanyCounteragentCreate,
    CompanyCounteragentUpdate
)

router = APIRouter(prefix="/company-counteragents", tags=["Company Counteragents"])


@router.post("", response_model=CompanyCounteragentResponse, status_code=status.HTTP_201_CREATED)
def create_company_counteragent(
        counteragent: CompanyCounteragentCreate,
        db: Session = Depends(get_db)
):
    """Create a new company counteragent."""
    counteragent_repo = CompanyCounteragentRepository(db)

    existing = counteragent_repo.get_by_company_and_counteragent_inn(
        counteragent.company_id,
        counteragent.counteragent_inn,
        counteragent.counteragent_hr
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This counteragent already exists for this company"
        )

    return counteragent_repo.create(**counteragent.model_dump())


@router.get("", response_model=List[CompanyCounteragentResponse])
def get_company_counteragents(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        db: Session = Depends(get_db)
):
    """Get all company counteragents with pagination."""
    counteragent_repo = CompanyCounteragentRepository(db)
    return counteragent_repo.get_all(skip=skip, limit=limit)


@router.get("/{counteragent_id}", response_model=CompanyCounteragentResponse)
def get_company_counteragent(
        counteragent_id: int,
        db: Session = Depends(get_db)
):
    """Get a company counteragent by ID."""
    counteragent_repo = CompanyCounteragentRepository(db)
    counteragent = counteragent_repo.get_by_id(counteragent_id)
    if not counteragent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company counteragent with ID {counteragent_id} not found"
        )
    return counteragent


@router.get("/company/{company_id}", response_model=List[CompanyCounteragentResponse])
def get_company_counteragents_by_company(
        company_id: int,
        db: Session = Depends(get_db)
):
    """Get all counteragents for a company."""
    counteragent_repo = CompanyCounteragentRepository(db)
    return counteragent_repo.get_by_company_id(company_id)


@router.get("/counteragent/{counteragent_id}", response_model=List[CompanyCounteragentResponse])
def get_company_counteragents_by_counteragent(
        counteragent_id: int,
        db: Session = Depends(get_db)
):
    """Get all companies where this company is a counteragent."""
    counteragent_repo = CompanyCounteragentRepository(db)
    return counteragent_repo.get_by_counteragent_id(counteragent_id)


@router.put("/{counteragent_id}", response_model=CompanyCounteragentResponse)
def update_company_counteragent(
        counteragent_id: int,
        counteragent_update: CompanyCounteragentUpdate,
        db: Session = Depends(get_db)
):
    """Update a company counteragent."""
    counteragent_repo = CompanyCounteragentRepository(db)
    counteragent = counteragent_repo.update(
        counteragent_id, **counteragent_update.model_dump(exclude_unset=True)
    )
    if not counteragent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company counteragent with ID {counteragent_id} not found"
        )
    return counteragent


@router.delete("/{counteragent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company_counteragent(
        counteragent_id: int,
        db: Session = Depends(get_db)
):
    """Delete a company counteragent."""
    counteragent_repo = CompanyCounteragentRepository(db)
    success = counteragent_repo.delete(counteragent_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company counteragent with ID {counteragent_id} not found"
        )
    return None


__all__ = ['router']
