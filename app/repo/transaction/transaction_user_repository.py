import uuid
from typing import Optional
from sqlalchemy.orm import Session, joinedload

from app.models.enums import UserRole
from app.models import TransactionUser
from app.repo.base import BaseRepository


class TransactionUserRepository(BaseRepository[TransactionUser]):

    def __init__(self, db: Session):
        super().__init__(db, TransactionUser)

    def get_by_transaction_id(self, transaction_id: uuid.UUID) -> list[type[TransactionUser]]:
        return self.db.query(TransactionUser).filter(
            TransactionUser.transaction_id == transaction_id
        ).options(joinedload(TransactionUser.user_relation)).all()

    def get_by_user_id(self, user_id: uuid.UUID) -> list[type[TransactionUser]]:
        return self.db.query(TransactionUser).filter(
            TransactionUser.user_id == user_id
        ).options(joinedload(TransactionUser.transaction)).all()

    def get_by_role(
            self,
            transaction_id: uuid.UUID,
            role: UserRole
    ) -> list[type[TransactionUser]]:
        return self.db.query(TransactionUser).filter(
            TransactionUser.transaction_id == transaction_id,
            TransactionUser.role == role
        ).options(joinedload(TransactionUser.user_relation)).all()

    def get_by_transaction_and_user(
            self,
            transaction_id: uuid.UUID,
            user_id: uuid.UUID
    ) -> Optional[TransactionUser]:
        return self.db.query(TransactionUser).filter(
            TransactionUser.transaction_id == transaction_id,
            TransactionUser.user_id == user_id
        ).first()

    def assign_user(
            self,
            transaction_id: uuid.UUID,
            user_id: uuid.UUID,
            role: UserRole
    ) -> TransactionUser:
        existing = self.get_by_transaction_and_user(transaction_id, user_id)

        if existing:
            existing.role = role
            self.db.commit()
            self.db.refresh(existing)
            return existing

        return self.create(
            transaction_id=transaction_id,
            user_id=user_id,
            role=role
        )

    def remove_user(self, transaction_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        relation = self.get_by_transaction_and_user(transaction_id, user_id)
        if not relation:
            return False

        self.db.delete(relation)
        self.db.commit()
        return True


__all__ = [
    'TransactionUserRepository'
]
