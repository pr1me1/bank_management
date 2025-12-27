from app.models import BankTypes


class FileConfig:
    MAX_FILE_SIZE_MB = 10
    ALLOWED_MIME_TYPES = ["application/pdf"]
    STATIC_DIR = "uploads/documents"


REQUIRED_FIELDS = [
    'receiver_inn',
    'receiver_name',
    'receiver_account',
    'bank_code',
    'payment_amount',
    'payment_description',
    'payment_purpose_code',
]

BankTypesMapping = {
    BankTypes.KAPITALBANK: "Kapitalbank",
    BankTypes.IPAK_YULI: "Ipak yo'li bank",
}

__all__ = [
    "FileConfig",
    "REQUIRED_FIELDS",
    'BankTypesMapping'
]
