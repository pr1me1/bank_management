import logging

from aiogram import types, Router, filters

from app.repo import UserRepository
from app.utils.group_utils import GroupUtils
from app.utils.translations import get_user_language, t

router = Router()
logger = logging.getLogger(__name__)


@router.message(filters.CommandStart())
async def start_command_handler(message: types.Message, user_repo: UserRepository):
    try:
        if message.chat.type in ['group', 'supergroup']:
            await GroupUtils.ensure_user_in_group(message)

        user, _ = user_repo.get_or_create(message)
        lang = get_user_language(user)

        await message.answer(t("start", lang))

    except Exception as e:
        logger.error(f"Error in start_command_handler: {e}", exc_info=True)
        user = user_repo.get_by_telegram_id(message.from_user.id)
        lang = get_user_language(user)
        await message.answer(t("general_error", lang))


__all__ = ['router']
