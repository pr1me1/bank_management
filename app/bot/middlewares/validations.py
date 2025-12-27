import logging
from typing import Callable, Dict, Awaitable, Any

from aiogram import BaseMiddleware, types

from app.repo import GroupRepository

logger = logging.getLogger(__name__)


class GroupValidationMiddleware(BaseMiddleware):
    """
        Guruhni tekshiradi va admin bo'lmasa xabar yuboradi.
        Handler ishlamagunga filter bilan tekshirish oson bo'lsa,
        bu middleware xabar yuborishni boshqaradi.
    """
    async def __call__(
            self,
            handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[None]],
            event: types.TelegramObject,
            data: Dict[str, Any]
    ):
        if isinstance(event, types.Message):
            message = event
        elif isinstance(event, types.CallbackQuery):
            message = event.message
        else:
            return await handler(event, data)

        if not message or message.chat.type == "private":
            return await handler(event, data)

        group_repo: GroupRepository = data.get('group_repo')
        try:
            group = group_repo.get_by_telegram_id(message.chat.id)
            if not group:
                return await handler(event, data)

            admins = group_repo.get_admins(group.id)

            if not admins:
                if message.text and message.text.startswith('/'):
                    try:
                        await message.answer(
                            text="❌ Botdan foydalanish uchun avval adminni guruhga qo'shing!\n\n"
                                 "Masalan: /balance, /set_role, /rm_role",
                            parse_mode="HTML"
                        )
                    except Exception as e:
                        logger.error(f"Xabar yuborishda xatolik: {e}")
                return

        except Exception as e:
            logger.error(f"Guruh validatsiyasida xatolik: {e}")

        return await handler(event, data)


__all__ = [
    'GroupValidationMiddleware',
]
