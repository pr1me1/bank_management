import uuid
from typing import List

from fastapi import APIRouter, HTTPException, Depends
from starlette import status

from app.core.configs import settings
from app.dependencies import (
    get_bank_account_repository,
    get_transaction_repository, get_company_repository
)
from app.repo import BankAccountRepository, TransactionRepository, CompanyRepository
from app.schemas import KapitalAuthRequest, KapitalConfirmOtpRequest
from app.schemas.responses import BankAccountListResponse
from app.services import Kapitalbank

router = APIRouter(prefix="/integrate/kapital", tags=["integrate_bank"])


@router.post('/auth', status_code=status.HTTP_200_OK)
async def auth_kapital(
        payload: KapitalAuthRequest,
        bank_account_repo: BankAccountRepository = Depends(get_bank_account_repository)
):
    if not settings.KAPITALBANK_URL:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="KAPITALBANK_URL is not configured. Please set it in environment variables."
        )

    try:
        service = Kapitalbank(payload.company_id, db=bank_account_repo.db)
        result = await service.auth(payload.login, payload.password)

        if result.get("success") is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.get("message", "Failed to authenticate with Kapitalbank")
            )

        if result.get("next_step") != "otp":
            await service.accounts()

        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Bu bank hisob oldin ro'yxatdan o'tgan yoki mavjud emas."
        )


@router.post('/confirm-otp', status_code=status.HTTP_200_OK)
async def confirm_kapital(
        payload: KapitalConfirmOtpRequest,
        bank_account_repo: BankAccountRepository = Depends(get_bank_account_repository)
):
    if not settings.KAPITALBANK_URL:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="KAPITALBANK_URL is not configured. Please set it in environment variables."
        )

    try:
        service = Kapitalbank(payload.company_id, db=bank_account_repo.db)
        result = await service.confirm_by_otp(session_id=payload.session_id, code=payload.code)

        if result.get("success") is False:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=result.get("message", f"Something gine wrong with Kapitalbank: {result.get('message')}")
            )

        accounts = await service.accounts()
        if accounts.get("success"):
            bank_account_repo.bulk_create(accounts.get("items"))

        return result
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during authentication: {str(e)}"
        )


@router.get('/{company_id}/accounts', status_code=status.HTTP_200_OK, response_model=List[BankAccountListResponse])
async def get_accounts(
        company_id: uuid.UUID,
        bank_account_repo: BankAccountRepository = Depends(get_bank_account_repository),
        company_repo: CompanyRepository = Depends(get_company_repository)
):
    if not settings.KAPITALBANK_URL:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="KAPITALBANK_URL is not configured. Please set it in environment variables."
        )

    try:
        company = company_repo.get_by_id(company_id)
        if not company:
            raise ValueError(f"Company {company_id} not found")

        has_bank_account = company_repo.has_bank_accounts(company_id)
        if not has_bank_account:
            print(f"Company with id: {company_id} doesn't have bank accounts")

        service = Kapitalbank(company_id, db=bank_account_repo.db)
        result = await service.accounts()

        if result.get("success") is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Failed to fetch accounts from Kapitalbank")
            )
        return result.get('items', [])

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching accounts: {str(e)}"
        )


@router.get('/{company_id}/transactions', status_code=status.HTTP_200_OK)
async def get_transactions(
        company_id: uuid.UUID,
        transaction_repo: TransactionRepository = Depends(get_transaction_repository),
):
    if not settings.KAPITALBANK_URL:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="KAPITALBANK_URL is not configured. Please set it in environment variables."
        )

    try:
        service = Kapitalbank(company_id, db=transaction_repo.db)
        result = await service.transactions()

        if result.get("success") is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("message", "Failed to fetch transactions from Kapitalbank")
            )
        return result
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching transactions: {str(e)}"
        )


__all__ = ['router']
