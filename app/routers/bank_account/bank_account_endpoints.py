import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

from app.dependencies import get_bank_account_repository
from app.repo import BankAccountRepository
from app.schemas.responses import BankAccountResponse

router = APIRouter(prefix="/bank-accounts", tags=["Bank Accounts"])


@router.get("", response_model=List[BankAccountResponse])
def get_bank_accounts(
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=500),
        bank_account_repo: BankAccountRepository = Depends(get_bank_account_repository),
):
    return bank_account_repo.get_all(skip=skip, limit=limit)


@router.get("/{bank_account_id}", response_model=BankAccountResponse)
def get_bank_account(
        bank_account_id: uuid.UUID,
        bank_account_repo: BankAccountRepository = Depends(get_bank_account_repository),
):
    bank_account = bank_account_repo.get_by_id(bank_account_id)
    if not bank_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bank account with ID {bank_account_id} not found"
        )
    return bank_account


@router.get("/type/{bank_type}", response_model=List[BankAccountResponse])
def get_bank_accounts_by_type(
        bank_type: str,
        bank_account_repo: BankAccountRepository = Depends(get_bank_account_repository),
):
    return bank_account_repo.get_by_bank_type(bank_type)


@router.delete("/{bank_account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bank_account(
        bank_account_id: uuid.UUID,
        bank_account_repo: BankAccountRepository = Depends(get_bank_account_repository),
):
    success = bank_account_repo.delete(bank_account_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bank account with ID {bank_account_id} not found"
        )
    return None


__all__ = ['router']
