from fastapi import APIRouter, HTTPException, Path
from starlette import status
from starlette.responses import JSONResponse

from app.schemas.responses import GNKCompanyInfoResponse, GNKErrorResponse
from app.services.gnk_api_service import GNKAPIService

router = APIRouter(prefix="/gnk-api", tags=["GNK API"])

_gnk_service = GNKAPIService()


@router.get(
    "/info/{inn}",
    response_model=GNKCompanyInfoResponse,
    responses={
        404: {"model": GNKErrorResponse, "description": "Company not found"},
        400: {"model": GNKErrorResponse, "description": "Invalid INN format"},
        500: {"model": GNKErrorResponse, "description": "Internal server error or API unavailable"},
    }
)
def get_company_info_by_inn(
        inn: str = Path(
            ...,
            description="9-digit INN/TAX_ID",
            pattern=r"^\d{9}$",
            example="123456789"
        )
):
    """
    Get company information by INN/TAX_ID from GNK API.
    
    Args:
        inn: 9-digit INN/TAX_ID
        
    Returns:
        Company information from GNK API
        
    Raises:
        400: If INN format is invalid
        404: If company not found
        500: If API is unavailable or internal error occurs
    """
    try:
        result = _gnk_service.get_company_info(inn)

        if result is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content=GNKErrorResponse(
                    success=False,
                    error="Company not found or API unavailable",
                    inn=inn
                ).model_dump()
            )

        return GNKCompanyInfoResponse(
            data=result,
            inn=inn,
            success=True
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching company information: {str(e)}"
        )


__all__ = ['router']
