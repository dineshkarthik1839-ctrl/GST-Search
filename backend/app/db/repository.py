from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.db.base_class import BaseEntity
import uuid

T = TypeVar("T", bound=BaseEntity)

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: uuid.UUID) -> Optional[T]:
        return self.db.execute(
            select(self.model).filter(self.model.id == id, self.model.is_deleted == False)
        ).scalar_one_or_none()

    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        return self.db.execute(
            select(self.model).filter(self.model.is_deleted == False).offset(skip).limit(limit)
        ).scalars().all()

    def get_by_field(self, field_name: str, value: any) -> Optional[T]:
        field = getattr(self.model, field_name)
        return self.db.execute(
            select(self.model).filter(field == value, self.model.is_deleted == False)
        ).scalar_one_or_none()

    def create(self, obj_in: dict) -> T:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: T, obj_in: dict) -> T:
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def soft_delete(self, id: uuid.UUID) -> bool:
        obj = self.get_by_id(id)
        if not obj:
            return False
        
        from datetime import datetime, timezone
        obj.is_deleted = True
        obj.deleted_at = datetime.now(timezone.utc)
        self.db.add(obj)
        self.db.commit()
        return True
