from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.models import Language
from app.utils.translations import t


def get_languages_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(key="languages", lang=Language.UZBEK_LATN.value), callback_data="lang_uz_latn")],
        [InlineKeyboardButton(text=t(key="languages", lang=Language.UZBEK_CYRILLIC.value),
                              callback_data="lang_uz_cy")],
        [InlineKeyboardButton(text=t(key="languages", lang=Language.RUSSIAN.value), callback_data="lang_ru")],
        [InlineKeyboardButton(text=t(key="languages", lang=Language.ENGLISH.value), callback_data="lang_en")]
    ])

# def get_transaction_finalizers(lang: str, transaction_id):
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text=get_message(lang, 'edit_button'),
#                     callback_data=f"edit_{transaction_id}"
#                 )
#             ],
#             [
#                 InlineKeyboardButton(
#                     text=get_message(lang, 'confirm_button'),
#                     callback_data=f"confirm_{transaction_id}"
#                 ),
#                 InlineKeyboardButton(
#                     text=get_message(lang, 'cancel_button'),
#                     callback_data=f"reject_{transaction_id}"
#                 )
#             ]
#         ]
#     )


# def get_confirmation_updates(lang: str, field: str):
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text=get_message(lang, 'confirm_button'),
#                     callback_data=f"update_confirm_{field}"
#                 ),
#                 InlineKeyboardButton(
#                     text=get_message(lang, 'cancel_button'),
#                     callback_data=f"update_reject_{field}"
#                 )
#             ]
#         ]
#     )


# def get_login_keyboard(telegram_id: int):
#     return InlineKeyboardMarkup(
#         inline_keyboard=[
#             [
#                 InlineKeyboardButton(
#                     text="🔄 Yangi code olish",
#                     callback_data=f"login_{telegram_id}"
#                 )
#             ]
#         ]
#     )
