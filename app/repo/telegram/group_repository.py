import uuid
from typing import Optional, List

from sqlalchemy.orm import Session, joinedload

from app.models.telegram.group import Group
from app.models.telegram.group_users import GroupUser, GroupRole
from app.repo.base import BaseRepository


class GroupRepository(BaseRepository[Group]):
    """Repository for Group operations."""

    def __init__(self, db: Session):
        super().__init__(db, Group)

    def get_by_telegram_id(self, telegram_id: int) -> Optional[Group]:
        """Get group by Telegram ID."""
        return self.db.query(Group).filter(Group.telegram_id == telegram_id).first()

    def get_or_create_by_telegram_id(
            self,
            telegram_id: int,
            title: str
    ) -> tuple[Group, bool]:
        """Get existing group or create new one."""
        group = self.get_by_telegram_id(telegram_id)
        if group:
            if title and group.title != title:
                group.title = title
                self.db.commit()
                self.db.refresh(group)
            return group, False

        group = self.create(telegram_id=telegram_id, title=title)
        return group, True

    def get_with_users(self, group_id: uuid.UUID) -> Optional[Group]:
        """Get group with users loaded."""
        return self.db.query(Group).options(
            joinedload(Group.users),
            joinedload(Group.group_users)
        ).filter(Group.id == group_id).first()

    def get_with_companies(self, group_id: uuid.UUID) -> Optional[Group]:
        """Get group with companies loaded."""
        return self.db.query(Group).options(
            joinedload(Group.companies),
            joinedload(Group.company_groups)
        ).filter(Group.id == group_id).first()

    def get_user_role(self, group_id: uuid.UUID, user_id: uuid.UUID) -> Optional[GroupRole]:
        """Get user's role in a group."""
        group_user = self.db.query(GroupUser).filter(
            GroupUser.group_id == group_id,
            GroupUser.user_id == user_id
        ).first()
        return group_user.role if group_user else None

    def add_member(
            self,
            group_id: uuid.UUID,
            user_id: uuid.UUID,
            role: GroupRole = GroupRole.USER
    ) -> GroupUser:
        """Add user to group."""

        existing = self.db.query(GroupUser).filter(
            GroupUser.group_id == group_id,
            GroupUser.user_id == user_id
        ).first()

        if existing:
            if existing.left_date is not None:
                existing.left_date = None
                existing.ban_date = None
                existing.role = role
                self.db.commit()
                self.db.refresh(existing)
            return existing

        group_user = GroupUser(
            group_id=group_id,
            user_id=user_id,
            role=role
        )
        self.db.add(group_user)
        self.db.commit()
        self.db.refresh(group_user)
        return group_user

    def remove_member(self, group_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Remove user from group."""
        group_user = self.db.query(GroupUser).filter(
            GroupUser.group_id == group_id,
            GroupUser.user_id == user_id
        ).first()

        if not group_user:
            return False

        self.db.delete(group_user)
        self.db.commit()
        return True

    def is_member(self, group_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """Check if user is an active member of the group."""
        group_user = self.db.query(GroupUser).filter(
            GroupUser.group_id == group_id,
            GroupUser.user_id == user_id,
            GroupUser.left_date.is_(None)
        ).first()
        return group_user is not None

    def get_member_count(
            self,
            group_id: uuid.UUID,
            status: Optional[str] = None
    ) -> int:
        """
        Get count of members in a group.
        
        Args:
            group_id: Group ID
            status: If 'active', only count members with left_date is None
        
        Returns:
            Count of members
        """
        query = self.db.query(GroupUser).filter(
            GroupUser.group_id == group_id
        )

        if status == "active":
            query = query.filter(GroupUser.left_date.is_(None))

        return query.count()

    def get_admins(self, group_id: uuid.UUID) -> list[type[GroupUser]]:
        """Get all admin members of a group."""
        return self.db.query(GroupUser).filter(
            GroupUser.group_id == group_id,
            GroupUser.role == GroupRole.ADMIN,
            GroupUser.left_date.is_(None)
        ).options(joinedload(GroupUser.user)).all()

    def get_members(
            self,
            group_id: uuid.UUID,
            role: Optional[GroupRole] = None,
            status: Optional[str] = None
    ) -> List[GroupUser]:
        """
        Get members of a group with optional filtering.
        
        Args:
            group_id: Group ID
            role: Filter by role (optional)
            status: If 'active', only return members with left_date is None
        
        Returns:
            List of GroupUser objects
        """
        query = self.db.query(GroupUser).filter(
            GroupUser.group_id == group_id
        )

        if role is not None:
            query = query.filter(GroupUser.role == role)

        if status == "active":
            query = query.filter(GroupUser.left_date.is_(None))

        return query.options(joinedload(GroupUser.user)).all()

    def update_member_role(
            self,
            group_id: uuid.UUID,
            user_id: uuid.UUID,
            role: GroupRole
    ) -> Optional[GroupUser]:
        """Update member's role in group."""
        group_user = self.db.query(GroupUser).filter(
            GroupUser.group_id == group_id,
            GroupUser.user_id == user_id
        ).first()

        if not group_user:
            return None

        group_user.role = role
        self.db.commit()
        self.db.refresh(group_user)
        return group_user

    def delete_by_telegram_id(self, telegram_id: int):
        """Delete group by Telegram ID."""
        group = self.get_by_telegram_id(telegram_id)
        self.db.delete(group)
        self.db.commit()
        return True


__all__ = [
    'GroupRepository'
]
