import logging
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from starlette import status

from app.core.redis import get_redis_client
from app.db import get_db
from app.dependencies import get_company_repository
from app.repo import CompanyRepository
from app.schemas import CompanyCreate
from app.schemas.responses import CompanyResponse, CompanyListResponse
from app.services.gnk_api_service import GNKAPIService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/companies",
    tags=["Companies"]
)


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
        company: CompanyCreate,
        company_repo: CompanyRepository = Depends(get_company_repository)
):
    existing = company_repo.get_by_inn(company.inn)
    if existing:
        is_connected = company_repo.is_company_connected(existing.id)
        return CompanyResponse(
            **existing.__dict__,
            is_connected=is_connected
        )

    gnk_service = GNKAPIService()
    company_data = company.model_dump()

    try:
        gnk_info = gnk_service.get_company_info(company.inn)

        if not gnk_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not retrieve company information from GNK API for INN {company.inn}"
            )

        gnk_name = gnk_info.get('shortName')
        if gnk_name:
            gnk_name = str(gnk_name).strip() or None

        gnk_director = gnk_info.get('director') or gnk_info.get('name')
        if gnk_director:
            gnk_director = str(gnk_director).strip() or None

        provided_name = company_data.get('name')
        if provided_name:
            provided_name = str(provided_name).strip() or None

        if gnk_name:
            company_data['name'] = gnk_name
        elif provided_name:
            company_data['name'] = provided_name
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company name is required. Neither GNK API nor provided data contains a valid company name."
            )

        provided_director = company_data.get('director_name')
        if provided_director:
            provided_director = str(provided_director).strip() or None

        if gnk_director:
            company_data['director_name'] = gnk_director or gnk_info.get('name')
            if provided_director and provided_director != gnk_director:
                logger.warning(
                    f"Director name mismatch for INN {company.inn}: "
                    f"provided '{provided_director}' vs GNK '{gnk_director}'. Using GNK value."
                )
        elif provided_director:
            company_data['director_name'] = provided_director
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Director name is required. Neither GNK API nor provided data contains a valid director name."
            )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error fetching company info from GNK for INN {company.inn}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve company information from GNK API"
        )

    company = company_repo.create(**company_data)

    return CompanyResponse(
        **company.__dict__,
        is_connected=False
    )


@router.get("", response_model=List[CompanyListResponse])
def get_companies(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        db: Session = Depends(get_db)
):
    """Get all companies with pagination."""
    company_repo = CompanyRepository(db)
    return company_repo.get_all(skip=skip, limit=limit)


@router.get("/{company_id}", response_model=CompanyResponse)
def get_company(
        company_id: uuid.UUID,
        company_repo: CompanyRepository = Depends(get_company_repository),
):
    """Get a company by ID."""
    company = company_repo.get_by_id(company_id)
    is_connected = company_repo.is_company_connected(company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found"
        )
    return CompanyResponse(
        **company.__dict__,
        is_connected=is_connected
    )


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(
        company_id: uuid.UUID,
        company_repo: CompanyRepository = Depends(get_company_repository),

):
    """Delete a company."""
    success = company_repo.delete(company_id)
    redis_client = get_redis_client()
    redis_client.delete(f"kapitalbank:{company_id}:device")
    redis_client.delete(f"kapitalbank:{company_id}:tokens")
    redis_client.delete(f"kapitalbank:{company_id}:credentials")
    redis_client.delete(f"kapitalbank:{company_id}:business_info")
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found"
        )
    return None


__all__ = ['router']
