import logging
import uuid

from aiogram import types, Bot
from sqlalchemy.orm import Session

from app.admin import AdminUser
from app.db import SessionLocal
from app.models import GroupRole
from app.repo import UserRepository, GroupUserRepository

logger = logging.getLogger(__name__)


async def _check_group_member(bot: Bot, chat_id: int):
    db: Session = SessionLocal()

    query = db.query(AdminUser).filter(AdminUser.is_active == True)
    admin_ids = [int(a.telegram_id) for a in query.with_entities(AdminUser.telegram_id).all() if a.telegram_id]
    found_admins = []

    for admin_id in admin_ids:

        try:
            member = await bot.get_chat_member(chat_id, admin_id)

            if not isinstance(member, (types.ChatMemberLeft, types.ChatMemberBanned)):
                found_admins.append(member.user)

        except Exception as e:
            logger.warning(f"User {admin_id} ni tekshirishda xatolik: {e}")
            continue

    return found_admins


async def _save_admin_to_database(
        tg_user: types.user.User,
        group_id: uuid.UUID
):
    db: Session = SessionLocal()
    user_repo = UserRepository(db)
    group_user_repo = GroupUserRepository(db)

    try:
        user, _ = user_repo.get_or_create_by_telegram_id(
            telegram_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name,
        )

        group_user_repo.get_or_create(
            group_id=group_id,
            user_id=user.id,
            role=GroupRole.ADMIN
        )
        return True
    except Exception as e:
        logger.error(f"Bazaga saqlashda xatolik: {e}")
        return False


__all__ = [
    '_check_group_member',
    '_save_admin_to_database',
]
