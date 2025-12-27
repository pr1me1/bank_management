import logging
from typing import Annotated

from jose import jwt
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app import repo
from .db import get_db
from .models import User
from app.core.configs import settings

security = HTTPBearer()
logger = logging.getLogger(__name__)


def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
) -> type[User]:
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        telegram_id: int = int(payload.get('sub'))
        token_type: str = payload.get('type')

        if telegram_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token'
            )

        if token_type != 'access':
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token type'
            )
    except jwt.ExpiredSignatureError as e:
        logger.error(f"❌ Expired: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token has expired'
        )
    except jwt.JWTError as e:
        logger.error(f"❌ JWT Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token invalid: {str(e)}"
        )

    user = db.query(User).filter(User.telegram_id == telegram_id).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


current_user_dep = Annotated[User, Depends(get_current_user)]


def get_transaction_repository(db: Session = Depends(get_db)) -> repo.TransactionRepository:
    return repo.TransactionRepository(db)


def get_user_repository(db: Session = Depends(get_db)) -> repo.UserRepository:
    return repo.UserRepository(db)


def get_group_repository(db: Session = Depends(get_db)) -> repo.GroupRepository:
    return repo.GroupRepository(db)


def get_audit_log_repository(db: Session = Depends(get_db)) -> repo.AuditLogRepository:
    return repo.AuditLogRepository(db)


def get_company_repository(db: Session = Depends(get_db)) -> repo.CompanyRepository:
    return repo.CompanyRepository(db)


def get_transaction_user_repository(db: Session = Depends(get_db)) -> repo.TransactionUserRepository:
    return repo.TransactionUserRepository(db)


def get_bank_account_repository(db: Session = Depends(get_db)) -> repo.BankAccountRepository:
    return repo.BankAccountRepository(db)




def get_company_counteragent_repository(db: Session = Depends(get_db)) -> repo.CompanyCounteragentRepository:
    return repo.CompanyCounteragentRepository(db)


def get_company_group_repository(db: Session = Depends(get_db)) -> repo.CompanyGroupRepository:
    return repo.CompanyGroupRepository(db)


def get_group_user_repository(db: Session = Depends(get_db)) -> repo.GroupUserRepository:
    return repo.GroupUserRepository(db)


def get_certificate_repository(db: Session = Depends(get_db)) -> repo.CertificateRepository:
    return repo.CertificateRepository(db)


def get_audit_repository(db: Session = Depends(get_db)) -> repo.AuditLogRepository:
    return repo.AuditLogRepository(db)


def get_admin_repository(db: Session = Depends(get_db)) -> repo.AdminRepository:
    return repo.AdminRepository(db)


__all__ = [
    'current_user_dep',
    'get_user_repository',
    'get_group_repository',
    'get_admin_repository',
    'get_company_repository',
    'get_audit_log_repository',
    'get_group_user_repository',
    'get_transaction_repository',
    'get_bank_account_repository',
    'get_company_group_repository',
    'get_transaction_user_repository',
    'get_company_counteragent_repository',
    'get_certificate_repository'
]
