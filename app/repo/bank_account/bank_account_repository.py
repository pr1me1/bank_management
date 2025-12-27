import uuid
from typing import Optional

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session, joinedload

from app.models.bank_account.bank_account import BankAccount
from app.repo.base import BaseRepository


class BankAccountRepository(BaseRepository[BankAccount]):
    def __init__(self, db: Session):
        super().__init__(db, BankAccount)

    def get_by_bank_type(self, bank_type: str) -> list[BankAccount]:
        return self.db.query(BankAccount).filter(
            BankAccount.bank_type == bank_type
        ).all()

    def get_by_account_number(self, account_number: str) -> Optional[BankAccount]:
        return self.db.query(BankAccount).filter(
            BankAccount.account_number == account_number
        ).first()

    def get_by_company_id(self, company_id: uuid.UUID) -> list[BankAccount]:
        return self.db.query(BankAccount).filter(
            BankAccount.company_id == company_id
        ).all()

    def get_or_create(self, company_id: uuid.UUID, account_number: str, defaults: dict = None) -> BankAccount:
        account = self.db.query(BankAccount).filter(
            BankAccount.company_id == company_id,
            BankAccount.account_number == account_number
        ).first()

        if account:
            if defaults:
                for key, value in defaults.items():
                    if key not in ['company_id', 'account_number']:
                        setattr(account, key, value)
                self.db.commit()
                self.db.refresh(account)
            return account

        data = defaults or {}
        data.update({'company_id': company_id, 'account_number': account_number})
        account = BankAccount(**data)
        self.db.add(account)
        self.db.commit()
        self.db.refresh(account)
        return account

    def update_balance(self, bank_account_id: uuid.UUID, new_balance: float) -> Optional[BankAccount]:
        bank_account = self.get_by_id(bank_account_id)
        if bank_account:
            bank_account.balance = new_balance
            self.db.commit()
            self.db.refresh(bank_account)
        return bank_account

    def get_total_balance_by_company(self, company_id: uuid.UUID) -> float:
        result = self.db.query(func.sum(BankAccount.balance)).filter(
            BankAccount.company_id == company_id
        ).scalar()
        return float(result) if result else 0.0

    def bulk_create(self, results: list[dict]) -> list[BankAccount]:
        bank_accounts = [BankAccount(**data) for data in results]
        self.db.add_all(bank_accounts)
        self.db.commit()
        return bank_accounts

    def bulk_create_or_update(self, results: list[dict]) -> list[BankAccount]:
        if not results:
            return []

        for item in results:
            if 'account_number' not in item:
                raise ValueError("account_number is required for bulk_create_or_update")

        statement = insert(BankAccount).values(results)

        statement = statement.on_conflict_do_update(
            index_elements=['account_number'],
            set_={
                'bank_type': statement.excluded.bank_type,
                'currency': statement.excluded.currency,
                'balance': statement.excluded.balance,
                'mfo_number': statement.excluded.mfo_number,
                'company_id': statement.excluded.company_id,
                'updated_at': func.now()
            }
        ).returning(BankAccount)

        result = self.db.execute(statement)

        bank_accounts = list(result.scalars().all())

        self.db.commit()

        for account in bank_accounts:
            self.db.refresh(account)

        return bank_accounts


__all__ = ['BankAccountRepository']
