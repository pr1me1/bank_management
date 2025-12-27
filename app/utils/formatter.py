from decimal import Decimal
from typing import Any


class Formatter:
    @staticmethod
    def format_amount(amount: Any) -> str:
        try:
            if not amount:
                return "0.00"
            if isinstance(amount, str):
                cleaned = amount.replace(",", "").replace(" ", "").strip()
                if not cleaned:
                    return "0.00"
                amount_decimal = Decimal(cleaned)
            elif isinstance(amount, (int, float)):
                amount_decimal = Decimal(str(amount))
            elif isinstance(amount, Decimal):
                amount_decimal = amount
            else:
                return f"{amount}"

            formatted = f"{amount_decimal:,.2f}"

            formatted = formatted.replace(",", " ")
            return f"{formatted}"
        except Exception:
            return f"{amount}"


__all__ = ["Formatter"]
