from abc import ABC, abstractmethod


class Adapter(ABC):
    """Implements an Adapter pattern for converting between models and entities.

    An abstract base class for implementing an Adapter pattern for model-entity
    conversions. The Adapter pattern is a design pattern that provides a
    mechanism for converting data from one representation to another, which is
    useful for decoupling systems and avoiding tight coupling between
    components.
    """

    @abstractmethod
    @classmethod
    def to_model(cls, entity):
        """Converts an entity to a model.

        Args:
            entity (object): The domain entity to be converted.

        Returns:
            model: The model representation of the entity.
        """
        ...

    @abstractmethod
    @classmethod
    def to_entity(cls, model):
        """Converts a model to an entity.

        Args:
            model (object): The database model to be converted.

        Returns:
            entity: The entity representation of the model.
        """
        ...
