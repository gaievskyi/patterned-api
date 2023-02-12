from typing import List

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from crud.base import CRUD

from models.item import Item
from schemas.item import ItemCreate, ItemUpdate


class CRUDItem(CRUD[Item, ItemCreate, ItemUpdate]):

    def create_with_owner(
        self, session: Session, *, payload: ItemCreate, owner_id: int
    ) -> Item:
        encoded_payload = jsonable_encoder(payload)
        model = self.model(**encoded_payload, owner_id=owner_id)
        session.add(model)
        session.commit()
        session.refresh(model)
        return model

    def get_multi_by_owner(
        self, session: Session, *, owner_id: int, skip: int = 0, limit: int = 100
    ) -> List[Item]:
        return (
            session.query(self.model)
            .filter(Item.owner_id == owner_id)
            .offset(skip)
            .limit(limit)
            .all()
        )


item = CRUDItem(Item)
