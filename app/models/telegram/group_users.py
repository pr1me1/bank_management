import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, Enum as SQLEnum, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, mapped_column, Mapped

from app.models import UUIDBase
from app.models.enums import GroupRole


class GroupUser(UUIDBase):
    __tablename__ = "group_users"

    group_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("groups.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    role: Mapped[GroupRole] = mapped_column(
        SQLEnum(GroupRole, name="group_role"), nullable=False, default=GroupRole.USER
    )

    join_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    left_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    ban_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    group: Mapped["Group"] = relationship(
        "Group", back_populates="group_users", lazy="joined"
    )
    user: Mapped["User"] = relationship(
        "User", back_populates="group_users", lazy="joined"
    )

    def __str__(self) -> str:
        try:
            user_str = str(self.user) if self.user else f"User #{self.user_id}"
            group_title = self.group.title if self.group else f"Group #{self.group_id}"
            return f"{user_str} in {group_title} ({self.role.value})"
        except Exception:
            return f"GroupUser #{self.id}"

    def __repr__(self):
        return f"<GroupUser id={self.id} group_id={self.group_id} user_id={self.user_id} role={self.role}>"
