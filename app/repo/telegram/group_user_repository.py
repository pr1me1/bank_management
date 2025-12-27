import uuid
from typing import Optional, Any
from sqlalchemy.orm import Session, joinedload, Query

from app.models import GroupUser, GroupRole
from app.repo.base import BaseRepository


class GroupUserRepository(BaseRepository[GroupUser]):
    """Repository for GroupUser operations."""

    def __init__(self, db: Session):
        super().__init__(db, GroupUser)

    def get_or_create(
            self,
            group_id: uuid.UUID,
            user_id: uuid.UUID,
            role: GroupRole
    ) -> tuple[type[GroupUser], bool] | tuple[GroupUser, bool]:
        """Get or create group-user relationship."""
        group_user = self.db.query(GroupUser).filter(
            GroupUser.group_id == group_id,
            GroupUser.user_id == user_id,
            GroupUser.role == role
        ).first()

        if group_user:
            return group_user, False
        group_user = self.create(group_id=group_id, user_id=user_id, role=role)
        return group_user, True

    def get_by_group_and_user(self, group_id: uuid.UUID, user_id: uuid.UUID) -> Optional[GroupUser]:
        """Get group-user relationship."""
        return self.db.query(GroupUser).filter(
            GroupUser.group_id == group_id,
            GroupUser.user_id == user_id
        ).first()

    def get_by_group_id(self, group_id: uuid.UUID) -> list[type[GroupUser]]:
        """Get all users in a group."""
        return self.db.query(GroupUser).filter(
            GroupUser.group_id == group_id
        ).options(joinedload(GroupUser.user)).all()

    def get_by_user_id(self, user_id: uuid.UUID) -> list[type[GroupUser]]:
        """Get all groups for a user."""
        return self.db.query(GroupUser).filter(
            GroupUser.user_id == user_id
        ).options(joinedload(GroupUser.group)).all()

    def get_by_role(self, group_id: uuid.UUID, role: GroupRole) -> list[type[GroupUser]]:
        """Get all users with a specific role in a group."""
        return self.db.query(GroupUser).filter(
            GroupUser.group_id == group_id,
            GroupUser.role == role
        ).options(joinedload(GroupUser.user)).all()


__all__ = [
    'GroupUserRepository'
]
