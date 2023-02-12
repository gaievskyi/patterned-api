from typing import Any, Dict, Generic, Type, TypeVar

from pydantic import BaseModel
from adapter import Adapter

from src.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
# A sentinel value for keeping track of entities removed from the repository
removed = object()


class Repository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Provides a simplified, abstract interface to data sources, such as
    databases, and encapsulates the underlying data access mechanism.

    Args:
        session (Session): SQLAlchemy session object.
        identity_map (dict[Any, ModelType], optional): Identity map stores db entities.

    Methods:
        persist(): Merge all the changes in the entities stored in the
            identity map to the database.
    """

    def __init__(self, model: Type[ModelType], adapter: Adapter, identity_map: Dict[Any, ModelType] = None):
        self._model = model
        self._adapter = adapter
        self._identity_map = identity_map or dict()

    def __getitem__(self, index):
        return self.get(index)

    @property
    def model(self):
        return self._model

    @property
    def adapter(self):
        return self._adapter

    @property
    def identity_map(self):
        return self._identity_map

    def persist(self):
        persisted_entities = set()
        for entity in self.identity_map:
            if entity is not removed and entity not in persisted_entities:
                self.__persist(entity)
                persisted_entities.add(entity)

    def __persist(self, instance):
        self.__assert_already_removed(instance)
        assert instance.id in self.identity_map, "Cannot persist entity which is unknown to the repo. Did you forget to call repo.create() for this entity?"
        entity = self.adapter.to_entity(instance)
        merged = self.session.merge(entity)
        self.session.add(merged)

    def __retrieve(self, model):
        if model is None:
            return None

        entity = self.adapter.to_entity(model)
        self.__assert_already_removed(entity)

        if entity.id in self.identity_map:
            return self.identity_map[entity.id]

        self.identity_map[entity.id] = entity
        return entity

    def __assert_already_removed(self, entity):
        fallback = f"Entity with given {entity.id=} has been already removed"
        assert self.identity_map.get(entity.id, None), fallback
