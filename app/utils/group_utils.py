import logging
from functools import wraps
from typing import Callable

from aiogram import types
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import GroupUser, GroupRole, User
from app.repo.telegram import GroupRepository

logger = logging.getLogger(__name__)


class GroupUtils:

    @staticmethod
    def has_admin_in_group(group_id):
        session: Session = SessionLocal()
        try:
            group_user = (
                session.query(GroupUser)
                .filter_by(group_id=group_id, role=GroupRole.ADMIN)
                .first()
            )
            return group_user is not None
        except Exception as e:
            logger.error(f"has_admin_in_group error: {e}")
            return False
        finally:
            session.close()

    @staticmethod
    async def ensure_user_in_group(message: types.Message):
        from app.repo import AdminRepository

        session: Session = SessionLocal()
        admin_repo = AdminRepository(session)
        try:
            user = session.query(User).filter(
                User.telegram_id == message.from_user.id,
            ).first()

            if not user:
                user = User(
                    telegram_id=message.from_user.id,
                    username=message.from_user.username,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name,
                )
                session.add(user)
                session.commit()
                session.refresh(user)
                logger.info(f"✅ Created new user: {user.id}")

            if message.chat.type in ['group', 'supergroup']:
                group_repo = GroupRepository(session)
                group = group_repo.get_by_telegram_id(message.chat.id)

                if not group:
                    logger.warning(f"Group not found for ensure_user: telegram_id={message.chat.id}")
                    return None

                is_member = group_repo.is_member(group.id, user.id)

                if not is_member:

                    if admin_repo.check_admin(message.from_user.id):
                        role = GroupRole.ADMIN
                        logger.info(
                            f"👑 Admin user added: {message.from_user.id} ({message.from_user.username}) "
                            f"to group {group.id}"
                        )
                    else:
                        role = GroupRole.USER

                    group_repo.add_member(
                        group_id=group.id,
                        user_id=user.id,
                        role=role
                    )
                    logger.info(f"✅ Added user {user.id} to group {group.id} with role {role.value}")
                else:
                    if admin_repo.check_admin(message.from_user.id):
                        from app.models.telegram.group_users import GroupUser
                        group_user = session.query(GroupUser).filter(
                            GroupUser.group_id == group.id,
                            GroupUser.user_id == user.id,
                            GroupUser.left_date.is_(None)
                        ).first()

                        if group_user and group_user.role != GroupRole.ADMIN:
                            group_repo.update_member_role(group.id, user.id, GroupRole.ADMIN)
                            logger.info(
                                f"👑 Updated user {user.id} role to ADMIN in group {group.id} "
                                f"(user is in admin.json)"
                            )

            return user.id
        except Exception as e:
            logger.error(f"ensure_user_in_group error: {e}")
            return False
        finally:
            session.close()


def require_role(*allowed_roles: GroupRole):
    def decorator(handler: Callable):

        @wraps(handler)
        async def wrapper(event: types.Update, *args, **kwargs):

            if isinstance(event, types.CallbackQuery):
                chat = event.message.chat
                tg_user = event.from_user
                send = event.message.answer
            elif isinstance(event, types.Message):
                chat = event.chat
                tg_user = event.from_user
                send = event.answer
            else:
                logger.warning(f"Unsupported event type: {type(event)}")
                return None

            if chat.type not in ['group', 'supergroup']:
                return await send("⚠️ Bu buyruq faqat guruh ichida ishlaydi.")

            session: Session = SessionLocal()
            try:
                group_repo = GroupRepository(session)
                group = group_repo.get_by_telegram_id(chat.id)

                if not group:
                    logger.warning(f"Group not found: telegram_id={chat.id}")
                    await send("❌ Bu guruh tizimda ro'yxatdan o'tmagan.")
                    return

                db_user = session.query(User).filter_by(telegram_id=tg_user.id).first()

                if not db_user:
                    logger.warning(f"User not found: telegram_id={tg_user.id}")
                    await send("❌ Siz tizimda ro'yxatdan o'tmagansiz. /start buyrug'ini yuboring.")
                    return

                group_user = (
                    session.query(GroupUser)
                    .filter_by(group_id=group.id, user_id=db_user.id)
                    .first()
                )

                if not group_user:
                    logger.warning(
                        f"User {db_user.id} not member of group {group.id} (telegram_id={chat.id})"
                    )
                    await send("❌ Siz bu guruhda ro'yxatdan o'tmagansiz. /start buyrug'ini yuboring.")
                    return

                logger.error(f"Allowed role: {allowed_roles}")
                logger.error(f"Group role: {group_user.role}")

                if group_user.role not in allowed_roles:
                    logger.warning(
                        f"⛔ Access Denied | User: {tg_user.id} ({tg_user.username}) | "
                        f"Required: {[r.value for r in allowed_roles]} | "
                        f"Actual: {group_user.role.value}"
                    )
                    await send(
                        f"⚠️ Sizda bu amalni bajarish uchun ruxsat yo'q. "
                    )
                    return

                logger.info(
                    f"✅ Permission granted | User: {tg_user.id} | "
                    f"Role: {group_user.role.value} | Group: {group.id}"
                )
                return await handler(event, *args, **kwargs)

            except Exception as e:
                logger.error(f"❌ require_role error: {e}", exc_info=True)
                await send("❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.")
            finally:
                session.close()

        return wrapper

    return decorator


def require_admin(handler: Callable):
    """Shortcut decorator for login-only commands."""
    return require_role(GroupRole.ADMIN)(handler)


__all__ = ["GroupUtils", "require_role", "require_admin"]
