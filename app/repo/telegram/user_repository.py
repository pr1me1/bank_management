import logging
from typing import Optional

from aiogram import types
from sqlalchemy.orm import Session

from app.models import Language
from app.models.telegram.user import User
from app.repo.base import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[User]):
    def __init__(self, db: Session):
        super().__init__(db, User)

    def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:

        return self.db.query(User).filter(User.telegram_id == telegram_id).first()

    def get_or_create(
            self,
            message: types.Message,
            language: Language = Language.RUSSIAN
    ) -> tuple[User, bool]:
        user = self.get_by_telegram_id(message.from_user.id)
        if user:
            updated = False

            if message.from_user.username and user.username != message.from_user.username:
                user.username = message.from_user.username
                updated = True

            if message.from_user.first_name and user.first_name != message.from_user.first_name:
                user.first_name = message.from_user.first_name
                updated = True

            if message.from_user.last_name and user.last_name != message.from_user.last_name:
                user.last_name = message.from_user.last_name
                updated = True

            if updated:
                self.db.commit()
                self.db.refresh(user)

            return user, False

        user = self.create(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language=language,
        )
        return user, True

    def get_or_create_by_telegram_id(
            self,
            telegram_id: int,
            username: Optional[str] = None,
            first_name: Optional[str] = None,
            last_name: Optional[str] = None,
            language: Optional[Language] = None,
    ) -> tuple[User, bool]:
        user = self.get_by_telegram_id(telegram_id)

        if user:
            updated = False
            if username is not None and user.username != username:
                user.username = username
                updated = True

            if first_name is not None and user.first_name != first_name:
                user.first_name = first_name
                updated = True

            if last_name is not None and user.last_name != last_name:
                user.last_name = last_name
                updated = True

            if language is not None and user.language != language:
                user.language = language
                updated = True

            if updated:
                self.db.commit()
                self.db.refresh(user)
                logger.debug(f"Updated user {telegram_id} info")

            return user, False

        user = self.create(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            language=language if language is not None else Language.RUSSIAN,
        )

        logger.info(f"Created new user {telegram_id} with language {user.language.value}")
        return user, True

    def get_by_username(self, username: str) -> Optional[User]:

        return self.db.query(User).filter(User.username == username).first()

    def search_by_name(self, search_term: str, limit: int = 10) -> list[type[User]]:
        pattern = f"%{search_term}%"
        return self.db.query(User).filter(
            (User.first_name.ilike(pattern)) |
            (User.last_name.ilike(pattern))
        ).limit(limit).all()

    def get_or_create_from_telegram_user(
            self,
            telegram_user: types.User,
            language: Optional[Language] = None
    ) -> tuple[User, bool]:
        return self.get_or_create_by_telegram_id(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
            language=language
        )

    def update_language(self, telegram_id: int, language: Language) -> Optional[User]:
        user = self.get_by_telegram_id(telegram_id)
        if user:
            user.language = language
            self.db.commit()
            self.db.refresh(user)
            logger.info(f"Updated user {telegram_id} language to {language.value}")
            return user

        logger.warning(f"User {telegram_id} not found for language update")
        return None

    def get_user_language(self, telegram_id: int) -> Language:
        user = self.get_by_telegram_id(telegram_id)
        if user and user.language:
            return user.language
        return Language.RUSSIAN

    def exists(self, telegram_id: int) -> bool:
        return self.db.query(User).filter(User.telegram_id == telegram_id).count() > 0

    def get_all_users_by_language(self, language: Language) -> list[User]:
        return self.db.query(User).filter(User.language == language).all()

    def count_by_language(self) -> dict[Language, int]:
        from sqlalchemy import func

        results = (
            self.db.query(User.language, func.count(User.id))
            .group_by(User.language)
            .all()
        )

        return {lang: count for lang, count in results if lang is not None}


__all__ = [
    'UserRepository'
]