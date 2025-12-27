import logging

from aiogram import types
from aiogram.filters import BaseFilter

from app.repo import GroupRepository

logger = logging.getLogger(__name__)


class AdminRequiredFilter(BaseFilter):
    """
        Guruhda hech bo'lmaganda bitta admin bo'rligini tekshiradi.
        Private chatda har doim ruxsat beradi.
    """

    async def __call__(
            self,
            message: types.Message,
            group_repo: GroupRepository
    ) -> bool:


        if message.chat.type == "private":
            return True

        if message.chat.type in ['group', 'supergroup']:
            try:
                group = group_repo.get_by_telegram_id(message.chat.id)

                if not group:
                    logger.warning(
                        f"Guruhi bazada topilmadi: {message.chat.id} ({message.chat.title})"
                    )
                    return False

                admins = group_repo.get_admins(group.id)
                if not admins:
                    logger.debug(
                        f"Guruh {group.id} da admin topilmadi. "
                        f"Buyruq: {message.text}"
                    )
                    return False
                return True
            except Exception as e:
                logger.error(f"Admin tekshirishda xatolik: {e}")
                return False

        return False


__all__ = [
    'AdminRequiredFilter'
]
