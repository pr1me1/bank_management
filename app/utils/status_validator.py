from typing import Dict, Any, List


class StatusValidator:

    @staticmethod
    def is_field_empty(value: Any, field_name: str = None) -> bool:
        if value is None:
            return True
        if isinstance(value, str) and value.strip() == "":
            return True

        if field_name == 'payment_amount':
            try:
                num_value = float(value) if isinstance(value, str) else value
                if num_value == 0.0 or num_value == 0:
                    return True
            except (ValueError, TypeError):
                pass
        return False

    @staticmethod
    def get_missing_fields(transaction_data: Dict[str, Any]) -> List[str]:
        missing = []
        receiver_inn = transaction_data.get('receiver_inn')
        has_inn = receiver_inn is not None and not StatusValidator.is_field_empty(receiver_inn, 'receiver_inn')

        from app.utils import REQUIRED_FIELDS
        for field in REQUIRED_FIELDS:
            if field == 'receiver_name' and has_inn:
                continue

            value = transaction_data.get(field)
            if StatusValidator.is_field_empty(value, field_name=field):
                missing.append(field)
        return missing

    @staticmethod
    def should_be_completed(transaction_data: Dict[str, Any]) -> bool:
        return len(StatusValidator.get_missing_fields(transaction_data)) == 0

    @staticmethod
    def validate_status_transition(
            current_status,
            new_status,
            transaction_data: Dict[str, Any]
    ) -> tuple[bool, str]:
        from app.models.transaction.transaction import TransactionStatus

        if new_status == TransactionStatus.COMPLETED:
            missing = StatusValidator.get_missing_fields(transaction_data)
            if missing:
                return False, f"Cannot set status to completed. Missing fields: {', '.join(missing)}"

        return True, ""


__all__ = (
    'StatusValidator',
)
