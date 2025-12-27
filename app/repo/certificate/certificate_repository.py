from sqlalchemy.orm import Session

from app.models import Certificate
from app.repo.base import BaseRepository


class CertificateRepository(BaseRepository[Certificate]):
    """Repository for Didox File operations."""

    def __init__(self, db: Session):
        super().__init__(db, Certificate)


__all__ = ['CertificateRepository']
