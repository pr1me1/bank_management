from datetime import datetime, UTC

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models import UUIDBase, TimestampMixin



class Certificate(UUIDBase, TimestampMixin):
    __tablename__ = "certificates"

    certificate_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    certificate_name: Mapped[str] = mapped_column(String(255),
                                                  nullable=False, unique=True, index=True)
    certificate_alias: Mapped[str] = mapped_column(Text, nullable=True)
    pkcs7_data: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime,
                                                 default=datetime.now(UTC), nullable=False)

    def __repr__(self):
        return (f"<Certificate(id={self.id}, "
                f"certificate_name={self.certificate_name})>")


__all__ = ["Certificate"]
