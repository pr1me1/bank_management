import uuid
from abc import ABC
from typing import Generic, TypeVar, Optional, List

from sqlalchemy.orm import Session

from app.models.abstract import Base

T = TypeVar('T', bound=Base)


class BaseRepository(ABC, Generic[T]):
    def __init__(self, db: Session, model: type[T]):
        self.db = db
        self.model = model

    def create(self, **kwargs) -> T:
        instance = self.model(**kwargs)
        self.db.add(instance)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def get_by_id(self, id: uuid.UUID) -> Optional[T]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        return self.db.query(self.model).offset(skip).limit(limit).all()

    def update(self, id: uuid.UUID, **kwargs) -> Optional[T]:
        instance = self.get_by_id(id)
        if not instance:
            return None
        for key, value in kwargs.items():
            setattr(instance, key, value)
        self.db.commit()
        self.db.refresh(instance)
        return instance

    def delete(self, id: uuid.UUID) -> bool:
        instance = self.get_by_id(id)
        if not instance:
            return False
        self.db.delete(instance)
        self.db.commit()
        return True

    def count(self) -> int:
        return self.db.query(self.model).count()

    def exists(self, id: uuid.UUID) -> bool:
        return self.get_by_id(id) is not None


__all__ = ['BaseRepository']
