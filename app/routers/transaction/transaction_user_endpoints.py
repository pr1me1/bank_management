from typing import List

from starlette import status
from sqlalchemy.orm import Session
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query
)

from app.db import get_db
from app.dependencies import current_user_dep
from app.models import UserRole
from app.repo import TransactionUserRepository
from app.schemas.responses import TransactionUserResponse

router = APIRouter(prefix="/transaction-users", tags=["Transaction Users"])


@router.post("/transaction/{transaction_id}/user/{user_id}", response_model=TransactionUserResponse,
             status_code=status.HTTP_201_CREATED)
def assign_user_to_transaction(
        transaction_id: int,
        user_id: int,
        role: UserRole = Query(..., description="Role for the user in the transaction"),
        db: Session = Depends(get_db)
):
    """Assign a user to a transaction with a role."""
    tx_user_repo = TransactionUserRepository(db)
    transaction_user = tx_user_repo.assign_user(transaction_id, user_id, role)
    return transaction_user


@router.get("/", response_model=List[TransactionUserResponse])
def get_transaction_users(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db)
):
    """Get all transaction users with pagination."""
    tx_user_repo = TransactionUserRepository(db)
    return tx_user_repo.get_all(skip=skip, limit=limit)


@router.get("/{transaction_user_id}", response_model=TransactionUserResponse)
def get_transaction_user(
        transaction_user_id: int,
        db: Session = Depends(get_db)
):
    """Get a transaction user by ID."""
    tx_user_repo = TransactionUserRepository(db)
    transaction_user = tx_user_repo.get_by_id(transaction_user_id)
    if not transaction_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction user with ID {transaction_user_id} not found"
        )
    return transaction_user


@router.get("/transaction/{transaction_id}", response_model=List[TransactionUserResponse])
def get_transaction_users_by_transaction(
        transaction_id: int,
        db: Session = Depends(get_db)
):
    """Get all users for a transaction."""
    tx_user_repo = TransactionUserRepository(db)
    return tx_user_repo.get_by_transaction_id(transaction_id)


@router.get("/user/{user_id}", response_model=List[TransactionUserResponse])
def get_transaction_users_by_user(
        user_id: int,
        db: Session = Depends(get_db)
):
    """Get all transactions for a user."""
    tx_user_repo = TransactionUserRepository(db)
    return tx_user_repo.get_by_user_id(user_id)


@router.get("/transaction/{transaction_id}/role/{role}", response_model=List[TransactionUserResponse])
def get_transaction_users_by_role(
        transaction_id: int,
        role: UserRole,
        db: Session = Depends(get_db)
):
    """Get all users with a specific role for a transaction."""
    tx_user_repo = TransactionUserRepository(db)
    return tx_user_repo.get_by_role(transaction_id, role)


@router.delete("/transaction/{transaction_id}/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user_from_transaction(
        transaction_id: int,
        user_id: int,
        db: Session = Depends(get_db)
):
    """Remove a user from a transaction."""
    tx_user_repo = TransactionUserRepository(db)
    success = tx_user_repo.remove_user(transaction_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not assigned to this transaction"
        )
    return None


@router.delete("/{transaction_user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction_user(
        transaction_user_id: int,
        db: Session = Depends(get_db)
):
    """Delete a transaction user relationship."""
    tx_user_repo = TransactionUserRepository(db)
    success = tx_user_repo.delete(transaction_user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction user with ID {transaction_user_id} not found"
        )
    return None


__all__ = ['router']
