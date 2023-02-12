from typing import Any, Dict, Generic, List, Optional, Type, TypeVar,  Union

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db.base import Base


ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUD(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    CRUD object with default methods to Create, Read, Update, Delete.

    Args:
        model: A SQLAlchemy model class
    """

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, session: Session, id: Any) -> Optional[ModelType]:
        return session.query(self.model).filter(self.model.id == id).first()

    def get_multi(
        self, session: Session, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        return session.query(self.model).offset(skip).limit(limit).all()

    def create(self, session: Session, *, payload: CreateSchemaType) -> ModelType:
        encoded_payload = jsonable_encoder(payload)
        model = self.model(**encoded_payload)  # type: ignore
        session.add(model)
        session.commit()
        session.refresh(model)
        return model

    def update(
        self,
        session: Session,
        *,
        model: ModelType,
        payload: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        encoded_model = jsonable_encoder(model)
        if isinstance(payload, dict):
            update_data = payload
        else:
            update_data = payload.dict(exclude_unset=True)
        for field in encoded_model:
            if field in update_data:
                setattr(model, field, update_data[field])
        session.add(model)
        session.commit()
        session.refresh(model)
        return model

    def remove(self, session: Session, *, id: int) -> ModelType:
        model = session.query(self.model).get(id)
        session.delete(model)
        session.commit()
        return model
