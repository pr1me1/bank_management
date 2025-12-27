import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import desc, asc, or_
from sqlalchemy.orm import Session

from app.models.enums import TransactionStatus
from app.models.transaction.transaction import Transaction
from app.repo.base import BaseRepository


class TransactionRepository(BaseRepository[Transaction]):

    def __init__(self, db: Session):
        super().__init__(db, Transaction)

    def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            receiver_inn: Optional[str] = None,
            sender_inn: Optional[str] = None,
            date_from: Optional[date] = None,
            date_to: Optional[date] = None,
            status: Optional[TransactionStatus] = None
    ) -> list[type[Transaction]]:
        query = self.db.query(Transaction)
        if receiver_inn:
            query = query.filter(Transaction.receiver_inn == receiver_inn)
        if sender_inn:
            query = query.filter(Transaction.sender_inn == sender_inn)
        if date_from:
            query = query.filter(Transaction.document_date >= date_from)
        if date_to:
            if isinstance(date_to, date) and not isinstance(date_to, datetime):
                date_to = datetime.combine(date_to, datetime.max.time())
            query = query.filter(Transaction.document_date <= date_to)
        if status:
            query = query.filter(Transaction.status == status)
        return query.order_by(desc(Transaction.document_date)).offset(skip).limit(limit).all()

    def get_by_account(
            self,
            account: str,
            date_from: Optional[date] = None
    ):
        query = self.db.query(Transaction)
        query = query.filter(
            or_(
                Transaction.sender_account == account,
                Transaction.receiver_account == account
            )
        )
        if date_from:
            query = query.filter(Transaction.document_date >= date_from)
            return query.order_by(asc(Transaction.document_date)).all()
        return query.order_by(desc(Transaction.document_date)).all()

    def get_by_accounts(
            self,
            accounts: list,
            date_from: Optional[date] = None
    ) -> list[type[Transaction]]:
        query = self.db.query(Transaction)
        query = query.filter(
            or_(
                Transaction.sender_account.in_(accounts),
                Transaction.receiver_account.in_(accounts)
            )
        )
        if date_from:
            query = query.filter(Transaction.document_date >= date_from)
            return query.order_by(asc(Transaction.document_date)).all()
        return query.order_by(desc(Transaction.document_date)).all()

    def get_status(self, id: uuid.UUID) -> TransactionStatus:
        return self.db.query(Transaction).filter(Transaction.id == id).first().status

    def get_by_receiver_inn(self, receiver_inn: str) -> list[type[Transaction]]:
        return self.db.query(Transaction).filter(
            Transaction.receiver_inn == receiver_inn
        ).order_by(desc(Transaction.created_at)).all()

    def get_by_sender_inn(self, sender_inn: str) -> list[type[Transaction]]:
        return self.db.query(Transaction).filter(
            Transaction.sender_inn == sender_inn
        ).order_by(desc(Transaction.created_at)).all()

    def get_non_existing_transaction_ids(self, transaction_ids: list[str]) -> list[str]:
        existing = self.db.query(Transaction.transaction_id).filter(
            Transaction.transaction_id.in_(transaction_ids)
        ).all()
        existing_ids = {row[0] for row in existing}
        return [tid for tid in transaction_ids if tid not in existing_ids]

    def bulk_create(self, transactions_data: list[dict]) -> list[Transaction]:
        transactions = [Transaction(**data) for data in transactions_data]

        self.db.add_all(transactions)
        self.db.commit()

        return transactions


__all__ = [
    'TransactionRepository'
]
