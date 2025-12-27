from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

from app.core.configs import settings
from app.models import BankAccount, Language
from app.utils.translations import t, format_balance_time, format_currency


async def balance_formatter(
        company: str,
        accounts: list[BankAccount],
        lang: str = Language.UZBEK_LATN.value
) -> str:
    now = datetime.now(ZoneInfo(settings.TIMEZONE))
    time_str = f"{now.hour}:{now.minute:02d}"
    date_str = now.strftime("%d.%m.%y")

    messages = format_balance_time(time_str, date_str, company, lang)

    currency_totals = defaultdict(Decimal)

    for account in accounts:
        formatted_balance = format_currency(
            amount=account.balance,
            currency=account.currency.upper(),
            lang=lang
        )
        messages += f"💳 {account.account_number} — {formatted_balance}\n\n"

        currency_totals[account.currency.upper()] += Decimal(str(account.balance))

    if len(accounts) > 1:
        total_label = t("total", lang)
        messages += f"\n<b>{total_label}:</b>\n"

        sorted_currencies = sorted(
            currency_totals.items(),
            key=lambda x: (x[0] != "UZS", x[0])
        )

        for currency_code, total_amount in sorted_currencies:
            if total_amount > 0:
                formatted_total = format_currency(
                    amount=total_amount,
                    currency=currency_code,
                    lang=lang
                )
                messages += f"💰 {formatted_total}\n"

    return messages
