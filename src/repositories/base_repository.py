from typing import TypeVar, Generic, Type, List, Optional
from src.models import db
from sqlalchemy import select

T = TypeVar("T")

class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def get_by_id(self, id: str) -> Optional[T]:
        return db.session.get(self.model, id)

    def get_all(self) -> List[T]:
        return db.session.execute(select(self.model)).scalars().all()

    def create(self, obj_in) -> T:
        db_obj = self.model(**obj_in)
        db.session.add(db_obj)
        db.session.commit()
        db.session.refresh(db_obj)
        return db_obj
