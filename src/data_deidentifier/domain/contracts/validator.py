from abc import ABC, abstractmethod


class EntityTypeValidatorContract(ABC):
    """Contract for validating entity types."""

    @abstractmethod
    def validate_entity_types(self, entity_types: list[str]) -> list[str]:
        """Validate entity types and return normalized valid types.

        Args:
            entity_types: List of entity types to validate

        Returns:
            Normalized list of valid entity types

        Raises:
            EntityTypeValidationError: If validation fails
        """
        raise NotImplementedError
