import logging

from aiogram import Router, filters, types

from app.models import GroupRole, Actions, ActionCategory, GroupActions
from app.repo import (
    UserRepository,
    GroupRepository,
    GroupUserRepository, AuditLogRepository, AdminRepository,
)
from app.utils import require_admin
from app.utils.translations import get_user_language, t, format_role_message

router = Router()
logger = logging.getLogger(__name__)


@router.message(filters.Command("set_role"))
@require_admin
async def set_role_handler(
        message: types.Message,
        command: filters.CommandObject,
        user_repo: UserRepository,
        admin_repo: AdminRepository,
        group_repo: GroupRepository,
        group_user_repo: GroupUserRepository,
        log_repo: AuditLogRepository
):
    admin_user = user_repo.get_by_telegram_id(message.from_user.id)
    lang = get_user_language(admin_user)

    try:
        args = command.args.split() if command.args else []
        target_user = None
        new_role = None
        promoter = admin_repo.get_by_telegram_id(message.from_user.id)

        if message.reply_to_message:
            target_user_tg = message.reply_to_message.from_user
            new_role = args[0] if len(args) > 0 else None
            target_user = user_repo.get_by_telegram_id(target_user_tg.id)
        elif len(args) >= 2:
            username = args[0].replace("@", "")
            new_role = args[1]
            target_user = user_repo.get_by_username(username)

        if not new_role:
            example = "/set_role @username client" if lang == "en" else "/set_role @username client"
            return await message.answer(
                t("warning_specify", lang, item="role", example=example),
                parse_mode="Markdown"
            )

        if new_role.upper() not in [GroupRole.CLIENT.value.upper(), GroupRole.ACCOUNTANT.value.upper()]:
            return await message.answer(t("invalid_role", lang))

        if not target_user:
            return await message.answer(
                t("error_not_found_in_db", lang, item=t("user_text", lang))
            )

        group = group_repo.get_by_telegram_id(message.chat.id)
        if not group:
            return await message.answer(t("error_not_found_in_db", lang, item=t("group_text", lang)))

        group_user = group_user_repo.get_by_group_and_user(
            user_id=target_user.id,
            group_id=group.id
        )

        if not group_user:
            return await message.answer(
                t("warning_not_member", lang, name=target_user.first_name)
            )

        group_user_repo.update(
            id=group_user.id,
            role=new_role.lower()
        )

        action = Actions(
            category=ActionCategory.GROUP,
            name=GroupActions.ASSIGNED
        )

        log_repo.create(
            user=target_user,
            admin=promoter,
            action=action,
            payload={
                "target_user": str(target_user.id) if target_user else None,
                "target_username": target_user.username,
                "promoter_user": str(promoter.id) if promoter else None,
                "new_role": new_role
            }
        )

        logger.info(f"Role changed: User {target_user.id} -> {new_role} (Group: {group.id})")

        msg = format_role_message(
            is_assigned=True,
            user_name=target_user.first_name,
            status=new_role,
            lang=lang
        )
        await message.answer(msg, parse_mode="HTML")

    except IndexError:
        await message.answer(t("invalid_set_role", lang), parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error in set_role_handler: {e}", exc_info=True)
        await message.answer(t("general_error", lang))


@router.message(filters.Command("rm_role"))
@require_admin
async def rm_role_handler(
        message: types.Message,
        command: filters.CommandObject,
        user_repo: UserRepository,
        admin_repo: AdminRepository,
        group_repo: GroupRepository,
        group_user_repo: GroupUserRepository,
        log_repo: AuditLogRepository
):
    admin_user = user_repo.get_by_telegram_id(message.from_user.id)
    lang = get_user_language(admin_user)

    try:
        args = command.args.split() if command.args else []
        promoter = admin_repo.get_by_telegram_id(message.from_user.id)

        if message.reply_to_message:
            target_user_tg = message.reply_to_message.from_user
            target_user = user_repo.get_by_telegram_id(target_user_tg.id)
        elif len(args) >= 1:
            username = args[0].replace("@", "")
            target_user = user_repo.get_by_username(username)
        else:
            example = "/rm_role @username" if lang == "en" else "/rm_role @username"
            return await message.answer(
                t("warning_specify", lang, item=t("user_text", lang), example=example),
                parse_mode="HTML"
            )

        if not target_user:
            return await message.answer(
                t("error_not_found_in_db", lang, item=t("user_text", lang))
            )

        group = group_repo.get_by_telegram_id(message.chat.id)
        if not group:
            return await message.answer(
                t("error_not_found_in_db", lang, item=t("group_text", lang))
            )

        group_user = group_user_repo.get_by_group_and_user(
            user_id=target_user.id,
            group_id=group.id
        )

        if not group_user:
            return await message.answer(
                t("warning_not_member", lang, name=target_user.first_name)
            )

        old_role = group_user.role
        group_user_repo.update(
            id=group_user.id,
            role=GroupRole.USER
        )

        action = Actions(
            category=ActionCategory.GROUP,
            name=GroupActions.UNASSIGNED
        )

        log_repo.create(
            user=target_user,
            admin=promoter,
            action=action,
            payload={
                "target_user": str(target_user.id) if target_user else None,
                "target_username": target_user.username,
                "promoter_user": str(promoter.id) if promoter else None,
                "old_role": old_role
            }
        )

        logger.info(
            f"Role removed: User {target_user.id} (Old role: {old_role}) | "
            f"Group: {group.id} | Admin: {message.from_user.id}"
        )

        msg = format_role_message(
            is_assigned=False,
            user_name=target_user.first_name,
            status=t("regular_member", lang),
            lang=lang
        )
        await message.answer(msg, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error in rm_role_handler: {e}", exc_info=True)
        await message.answer(t("general_error", lang))


__all__ = [
    "router"
]
