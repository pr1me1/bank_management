import logging

from aiogram import Router, F, types
from aiogram.filters import Command

from app.bot.keyboards.inline import get_languages_keyboard
from app.models import Language
from app.repo import UserRepository
from app.utils.translations import t, get_user_language

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "show_lang_menu")
async def show_lang_menu_handler(
        callback_query: types.CallbackQuery,
        user_repo: UserRepository
):
    try:
        user = user_repo.get_by_telegram_id(callback_query.from_user.id)
        lang = get_user_language(user)

        await callback_query.message.edit_text(
            t('choose_language', lang),
            reply_markup=get_languages_keyboard(),
            parse_mode="HTML"
        )
        await callback_query.answer()

    except Exception as e:
        logger.error(f"Error in show_lang_menu_handler: {e}", exc_info=True)
        await callback_query.answer(
            t('general_error', Language.RUSSIAN.value),
            show_alert=True
        )


@router.callback_query(F.data.startswith("lang_"))
async def language_selection_handler(
        callback_query: types.CallbackQuery,
        user_repo: UserRepository
):
    try:
        lang_code = callback_query.data.replace("lang_", "")

        valid_languages = [lang.value for lang in Language]
        if lang_code not in valid_languages:
            await callback_query.answer(
                t('invalid_language', Language.RUSSIAN.value),
                show_alert=True
            )
            return
        user, created = user_repo.get_or_create_from_telegram_user(
            callback_query.from_user
        )
        user_repo.update(
            id=user.id,
            language=Language(lang_code)
        )
        await callback_query.message.edit_text(
            t('language_changed', lang_code),
            parse_mode="HTML"
        )
        await callback_query.answer(
            t('language_changed_short', lang_code),
            show_alert=False
        )

        logger.info(f"User {user.telegram_id} changed language to {lang_code}")

    except Exception as e:
        logger.error(f"Error in language_selection_handler: {e}", exc_info=True)
        await callback_query.answer(
            t('general_error', Language.RUSSIAN.value),
            show_alert=True
        )


@router.message(Command("lang"))
async def lang_command_handler(
        message: types.Message,
        user_repo: UserRepository
):
    try:
        user = user_repo.get_by_telegram_id(message.from_user.id)
        lang = get_user_language(user)

        await message.answer(
            t('choose_language', lang),
            reply_markup=get_languages_keyboard(),
            parse_mode="HTML"
        )

    except Exception as e:
        logger.error(f"Error in lang_command_handler: {e}", exc_info=True)
        await message.answer(t('general_error', Language.RUSSIAN.value))


__all__ = ['router']
