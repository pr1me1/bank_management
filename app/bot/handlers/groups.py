import logging

from aiogram import Router
from aiogram import types, filters
from aiogram.exceptions import TelegramBadRequest

from app.bot.utils import (
    _check_group_member,
    _save_admin_to_database
)
from app.models import Actions, ActionCategory, GroupActions
from app.repo import (
    GroupRepository, AdminRepository, AuditLogRepository,
)
from app.utils.translations import t

router = Router()
logger = logging.getLogger(__name__)


@router.my_chat_member(
    filters.ChatMemberUpdatedFilter(
        member_status_changed=filters.IS_NOT_MEMBER >> filters.IS_MEMBER
    )
)
async def bot_added_to_group(
        event: types.ChatMemberUpdated,
        group_repo: GroupRepository,
        admin_repo: AdminRepository,
        log_repo: AuditLogRepository
):
    chat = event.chat

    if chat.type not in ['group', 'supergroup']:
        logger.info(f"")
        return

    group, _ = group_repo.get_or_create_by_telegram_id(
        telegram_id=chat.id,
        title=chat.title
    )

    adder = admin_repo.get_by_telegram_id(event.from_user.id)

    action = Actions(
        category=ActionCategory.GROUP,
        name=GroupActions.ADDED
    )

    log_repo.create(
        admin=adder,
        action=action,
        payload={
            "adder": str(adder.id) if adder else None,
            "added": "bot",
            "group": str(group.id) if group else None,
            "title": chat.title,
        }
    )

    try:
        found_admins = await _check_group_member(event.bot, chat.id)
    except TelegramBadRequest as e:
        logger.error(f"Failed to check group members for chat {chat.id}: {e}")
        return
    except Exception as e:
        logger.error(f"Unexpected error checking group members for chat {chat.id}: {e}")
        return

    if not found_admins:
        logger.debug(f"Admins not fount in group {chat.id}")
        try:
            await event.bot.send_message(
                chat_id=chat.id,
                text=t(key="bot_add_admin")
            )
        except TelegramBadRequest:
            logger.warning(f"Could not send message to group {chat.id} (Chat not found or bot kicked)")
        except Exception as e:
            logger.error(f"Error sending message to group {chat.id}: {e}")
        return

    success_count = 0

    if group:
        for admin in found_admins:
            if await _save_admin_to_database(tg_user=admin, group_id=group.id):
                success_count += 1

    try:
        await event.bot.send_message(
            chat_id=chat.id,
            text=t(key="group_added")
        )
    except TelegramBadRequest:
        logger.warning(f"Could not send success message to group {chat.id}")
    except Exception as e:
        logger.error(f"Error sending success message to group {chat.id}: {e}")

    logger.info(f"{success_count} ta admin bazaga saqlandi: {found_admins}")


@router.my_chat_member(
    filters.ChatMemberUpdatedFilter(
        member_status_changed=
        (filters.MEMBER | filters.ADMINISTRATOR) >> (filters.LEFT | filters.KICKED)
    )
)
async def bot_removed_from_group(
        event: types.ChatMemberUpdated,
        group_repo: GroupRepository,
        admin_repo: AdminRepository,
        log_repo: AuditLogRepository
):
    chat = event.chat

    if chat.type not in ['group', 'supergroup']:
        return

    try:
        group_repo.delete_by_telegram_id(chat.id)

        kicker = admin_repo.get_by_telegram_id(event.from_user.id)

        action = Actions(
            category=ActionCategory.GROUP,
            name=GroupActions.KICKED
        )

        log_repo.create(
            admin=kicker,
            action=action,
            payload={
                "kicker": str(kicker.id) if kicker else None,
                "kicked": "bot",
                "group": str(chat.id),
                "title": chat.title,
            }
        )

        logger.info(f"Guruh {chat.id} bazadan muvaffaqiyatli o'chirildi.")
    except Exception as e:
        logger.error(f"Guruhni o'chirishda xatolik: {e}")


__all__ = ['router']
