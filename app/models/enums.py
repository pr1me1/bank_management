from dataclasses import dataclass
from enum import Enum
from typing import Union


class Language(str, Enum):
    ENGLISH = "en"
    RUSSIAN = "ru"
    UZBEK_LATN = "uz_latn"
    UZBEK_CYRILLIC = "uz_cy"


class UserRole(str, Enum):
    CLIENT = "client"
    ACCOUNTANT = "accountant"


class GroupRole(str, Enum):
    USER = "user"
    CLIENT = "client"
    ACCOUNTANT = "accountant"
    ADMIN = "admin"


class TransactionStatus(str, Enum):
    UNFILLED = "unfilled"
    FILLED = "filled"
    REJECTED = "rejected"
    CONFIRMED = "confirmed"
    SENT = "sent"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class BankTypes(str, Enum):
    KAPITALBANK = "KAPITALBANK"
    IPAK_YULI = "IPAK_YULI"


class ActionCategory(str, Enum):
    AUTH = "auth"
    BANK = "bank"
    GROUP = "group"
    WEB = "web"


class AuthActions(str, Enum):
    CREATED_OTP = "created_otp"
    LOGGED_IN = "logged_in"
    LOGGED_OUT = "logged_out"


class BankActions(str, Enum):
    GET_BALANCE = "get_balance"
    GET_TRANSACTIONS = "get_transactions"


class GroupActions(str, Enum):
    ADDED = "added"
    KICKED = "kicked"
    ASSIGNED = "assigned"
    UNASSIGNED = "unassigned"


class WebActions(str, Enum):
    COMPANY_CREATE = "company_create"
    COMPANY_DELETE = "company_delete"
    CONNECT_BANK = "connect_bank"
    LINK_GROUP = "connect_group"
    UNLINK_GROUP = "unlink_group"


ActionType = Union[
    AuthActions,
    BankActions,
    GroupActions,
    WebActions,
]


@dataclass(frozen=True)
class Actions:
    category: ActionCategory
    name: ActionType

    def __str__(self) -> str:
        return f"{self.category}:{self.name.value}"


__all__ = [
    "Language",
    "UserRole",
    "GroupRole",
    "TransactionStatus",
    "BankTypes",
    "Actions",
    "ActionType",
    'AuthActions',
    "BankActions",
    "GroupActions",
    "ActionCategory",
]
