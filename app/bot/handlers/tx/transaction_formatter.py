from app.models import Transaction
from app.utils.translations import t


def format_transactions(transactions: list[Transaction], lang: str) -> list[str]:
    return [
        msg for i, transaction in enumerate(transactions, 1)
        if (msg := format_transaction(transaction, order=i, lang=lang)) is not None
    ]


def format_transaction(transaction: Transaction, lang: str, order: int = 1, ) -> str | None:
    direction = transaction.direction
    if not direction or direction.lower() not in ("in", "out"):
        return None

    direction = direction.lower()
    date = transaction.document_date.strftime("%d.%m.%Y %H:%M")

    if direction == "in":
        counterparty = transaction.sender_name
        flow_symbol = t("income", lang)
        amount_prefix = "+"
    else:
        counterparty = transaction.receiver_name
        flow_symbol = t("outgoings", lang)
        amount_prefix = "-"

    from app.utils.translations import format_currency
    formatted_amount = format_currency(
        amount=transaction.payment_amount,
        currency=transaction.currency if hasattr(transaction, 'currency') else "UZS",
        lang=lang
    )

    return (
        f"<b>№{order}</b>\n"
        f"{flow_symbol}: <b>{amount_prefix}{formatted_amount}</b>\n"
        f"⏰ {date}\n"
        f"🏢 <b>{counterparty}</b>\n"
        f"💬 {transaction.payment_description}\n\n"
    )
