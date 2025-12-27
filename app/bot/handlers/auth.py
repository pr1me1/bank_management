import logging

from aiogram import Router, filters, types, F

from app.models import Actions, ActionCategory, AuthActions
from app.repo import AdminRepository
from app.repo import AuditLogRepository, UserRepository
from app.services import get_login_code_cache
from app.utils.translations import format_code_info, t, get_user_language

router = Router()
logger = logging.getLogger(__name__)


@router.message(filters.Command('login'))
async def login_handler(
        message: types.Message,
        log_repo: AuditLogRepository,
        user_repo: UserRepository,
        admin_repo: AdminRepository
):
    chat_type = message.chat.type
    telegram_id = message.from_user.id

    user, _ = user_repo.get_or_create(message)
    lang = get_user_language(user)

    if chat_type != 'private':
        await message.answer(t("private_command", lang))
        return

    if not admin_repo.check_admin(telegram_id):
        logger.warning(f"Telegram ID {telegram_id}, not an admin!")
        await message.answer(t("no_permission", lang))
        return

    try:
        cache = get_login_code_cache()
        code, is_new = cache.get_or_create_code(telegram_id)
        login_url = "https://aiadmin.grossbook.uz/"

        if is_new:
            msg = format_code_info(
                code=code,
                is_new=True,
                lang=lang,
                login_url=login_url
            )
            await message.answer(
                msg,
                parse_mode="HTML",
            )

            action = Actions(
                category=ActionCategory.AUTH,
                name=AuthActions.CREATED_OTP
            )

            log_repo.create(
                user=user,
                action=action,
                payload={
                    "user": str(user.id) if user else None,
                    "username": message.from_user.username,
                    "retried": False
                }
            )
            logger.info(f"✅ New login code created | Admin: {telegram_id} | Code: {code}")
        else:
            ttl = cache.get_code_ttl(code)
            minutes = ttl // 60 if ttl else 0
            seconds = ttl % 60 if ttl else 0

            msg = format_code_info(
                code=code,
                is_new=False,
                lang=lang,
                login_url=login_url,
                minutes=minutes,
                seconds=seconds
            )
            await message.answer(
                msg,
                parse_mode="HTML",
            )

            action = Actions(
                category=ActionCategory.AUTH,
                name=AuthActions.CREATED_OTP
            )

            log_repo.create(
                user=user,
                action=action,
                payload={
                    "user": str(user.id) if user else None,
                    "username": message.from_user.username,
                    "retried": True
                }
            )

    except Exception as e:
        logger.error(f"❌ Error creating login code | Admin: {telegram_id} | Error: {e}")
        await message.answer(t("code_creation_error", lang))


@router.callback_query(F.data.startswith('login_'))
async def login_query(
        callback: types.CallbackQuery,
        admin_repo: AdminRepository,
        user_repo: UserRepository
):
    user = user_repo.get_by_telegram_id(callback.from_user.id)
    lang = get_user_language(user)

    if callback.message.chat.type != 'private':
        await callback.answer(
            text=t("private_command", lang),
            show_alert=True
        )
        return

    telegram_id = callback.from_user.id

    if not admin_repo.check_admin(telegram_id):
        await callback.answer(
            text=t("no_permission", lang),
            show_alert=True
        )
        return

    try:
        cache = get_login_code_cache()
        existing_code = cache._find_existing_code(telegram_id)

        if existing_code:
            ttl = cache.get_code_ttl(existing_code)

            if ttl and ttl > 0:
                minutes = ttl // 60
                seconds = ttl % 60

                await callback.answer(
                    text=t("active_code_short", lang, minutes=minutes, seconds=seconds),
                    show_alert=True
                )
                return

        if existing_code:
            cache.delete_code(existing_code)

        code, _ = cache.get_or_create_code(telegram_id)
        login_url = "https://aiadmin.grossbook.uz/"

        msg = format_code_info(
            code=code,
            is_new=True,
            lang=lang,
            login_url=login_url
        )

        await callback.message.edit_text(
            msg,
            parse_mode="HTML",
        )

        await callback.answer(t("new_code_success", lang), show_alert=False)

    except Exception as e:
        logger.error(f"Error in login_query: {e}", exc_info=True)
        await callback.answer(
            text=t("general_error", lang),
            show_alert=True
        )


__all__ = ['router']
