from typing import Optional, List

from pydantic import BaseModel


class CurrencyInfo(BaseModel):
    alphaCode: str
    name: str
    numericCode: str
    scale: int


class AccountItem(BaseModel):
    branch: str
    branchName: str
    number: str
    name: str
    currency: CurrencyInfo
    dayEndBalance: float
    dayStartBalance: float
    volumeDebit: float
    volumeCredit: float
    state: int
    stateName: str
    performer: str
    canPayGenerally: int
    lastOperationDate: Optional[str]
    openDate: str
    closeDate: Optional[str]
    accountNameShort: str
    currentBalance: float


class KapitalAccountsResponse(BaseModel):
    success: bool
    message: str
    items: Optional[List[AccountItem]] = None
    total_count: Optional[int] = None


__all__ = ["KapitalAccountsResponse", "CurrencyInfo", "AccountItem"]
