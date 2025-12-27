from typing import Optional

from app.models import User, Language
from app.utils.translations.translator import get_translator


def get_user_language(user: Optional[User] = None):
    if not user or not user.language:
        return Language.RUSSIAN.value
    return user.language.value


def format_success(key: str, lang: str, **kwargs):
    key = f"success_{key}"
    return get_translator().get(key, lang, **kwargs)


def format_error(key: str, lang: str, **kwargs):
    key = f"error_{key}"
    return get_translator().get(key, lang, **kwargs)


def format_role_message(
        is_assigned: bool,
        user_name: str,
        status: str,
        lang: str,
) -> str:
    translator = get_translator()
    if is_assigned:
        action = translator.get("success_assigned", lang=lang,
                                item=translator.get("role_text", lang=lang, default="Role"))
    else:
        action = translator.get("success_removed", lang=lang,
                                item=translator.get("role_text", lang=lang, default="Role"))

    return translator.get(
        'role_details',
        lang=lang,
        action=action,
        user_name=user_name,
        status=status,
    )


def format_code_info(
        code: str,
        lang: str,
        is_new: bool,
        login_url: str,
        minutes: Optional[int] = None,
        seconds: Optional[int] = None
):
    translator = get_translator()

    title = translator.get("code_title_new" if is_new else "code_title_active", lang=lang)
    validity_label = translator.get("code_validity_label" if is_new else "code_remaining_label", lang=lang)

    if is_new:
        validity = translator.get("code_validity_duration", lang=lang)
    else:
        validity = translator.get("code_validity_remaining", lang=lang, minutes=minutes or 0, seconds=seconds or 0)

    return translator.get(
        "code_info",
        lang,
        title=title,
        code=code,
        validity_label=validity_label,
        validity=validity,
        login_url=login_url
    )


def format_currency(
        currency: str,
        lang: str,
        amount: float,
):
    from decimal import Decimal

    translator = get_translator()
    currency_name = translator.get(currency.upper(), lang)

    amount_decimal = Decimal(str(amount))
    amount_str = f"{amount_decimal:.2f}"

    if "." in amount_str:
        integer_part, decimal_part = amount_str.split(".")
    else:
        integer_part = amount_str
        decimal_part = "00"

    reversed_digits = integer_part[::-1]
    groups = []
    for i in range(0, len(reversed_digits), 3):
        groups.append(reversed_digits[i:i + 3])

    formatted_integer = " ".join(group[::-1] for group in reversed(groups))

    return f"{formatted_integer}.{decimal_part} {currency_name}"


def format_balance_time(
        time_str: str,
        date_str: str,
        company: str,
        lang: str,
):
    return get_translator().get("time", lang=lang, time_str=time_str, date_str=date_str, company=company)
