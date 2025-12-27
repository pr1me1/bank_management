import logging
from typing import Dict, Callable, Any, Awaitable

from aiogram import types, BaseMiddleware

from app.repo import GroupRepository

logger = logging.getLogger(__name__)


class AdminCacheMiddleware(BaseMiddleware):
    """
        Admin ma'lumotlarini keshlaymiz (performance uchun).
        Har 5 minutda yangilaydi.
    """

    def __init__(self, cache_ttl: int = 300):
        self.cache: Dict[int, tuple] = {}  # {group_id: (admins_count, timestamp)}
        self.cache_ttl = cache_ttl

    async def __call__(
            self,
            handler: Callable[[types.TelegramObject, Dict[str, Any]], Awaitable[None]],
            event: types.TelegramObject,
            data: Dict[str, Any]
    ):
        if isinstance(event, types.Message) and event.chat.type in ["group", "supergroup"]:
            group_repo: GroupRepository = data.get("group_repo")
            if group_repo:
                try:
                    group = group_repo.get_by_telegram_id(event.chat.id)
                    if group:
                        admins = group_repo.get_admins(group.id)
                        data["group_admins_count"] = len(admins)
                except Exception as e:
                    logger.debug(f"Kesh xatosi: {e}")
        return await handler(event, data)


__all__ = [
    'AdminCacheMiddleware'
]
