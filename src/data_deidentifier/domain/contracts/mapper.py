from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from src.data_deidentifier.domain.types.entity import Entity
from src.data_deidentifier.domain.types.structured_analysis_result import (
    StructuredDataAnalysisField,
)

AdapterEntity = TypeVar("AdapterEntity")
AdapterField = TypeVar("AdapterField")


class EntityMapperContract(ABC, Generic[AdapterEntity]):
    """Contract for mapping between domain entities and external representations.

    This contract defines how domain entities are converted to and from
    presentation formats intended for external interfaces, regardless
    of their nature (API, CLI, UI, etc.).

    Type Parameters:
        AdapterEntity: The type of external representation
    """

    @staticmethod
    @abstractmethod
    def domain_to_adapter(entity: Entity) -> AdapterEntity:
        """Convert a domain Entity to an adapter entity.

        This method transforms an internal domain entity
        into the format expected in the domain response.

        Args:
            entity: The domain entity to convert

        Returns:
            The converted entity response object
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def adapter_to_domain(entity_response: AdapterEntity) -> Entity:
        """Convert an adapter entity to a domain entity.

        This method transforms an adapter Entity into the internal domain format.

        Args:
            entity_response: The adapter entity to convert

        Returns:
            The converted domain entity object
        """
        raise NotImplementedError


class StructuredFieldMapperContract(ABC, Generic[AdapterField]):
    """Contract for mapping between domain structured data and external representations.

    This contract defines how domain structured fields are converted to and from
    presentation formats intended for external interfaces.

    Type Parameters:
        AdapterField: The type of external representation
    """

    @staticmethod
    @abstractmethod
    def domain_to_adapter(field: StructuredDataAnalysisField) -> AdapterField:
        """Convert a domain StructuredDataAnalysisField to an adapter field.

        Args:
            field: The domain field to convert

        Returns:
            The converted adapter field object
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def adapter_to_domain(field_response: AdapterField) -> StructuredDataAnalysisField:
        """Convert an adapter field to a domain field.

        Args:
            field_response: The adapter field to convert

        Returns:
            The converted domain field object
        """
        raise NotImplementedError
