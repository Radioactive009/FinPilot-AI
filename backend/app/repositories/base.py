from typing import Generic, TypeVar, Type, List, Optional
from sqlalchemy.orm import Session
from app.database.session import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get(self, id: any) -> Optional[ModelType]:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def list(self) -> List[ModelType]:
        return self.db.query(self.model).all()

    def create(self, obj: ModelType) -> ModelType:
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self) -> ModelType:
        self.db.commit()
        return self.db

    def delete(self, id: any) -> Optional[ModelType]:
        obj = self.get(id)
        if obj:
            self.db.delete(obj)
            self.db.commit()
        return obj
