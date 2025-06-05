from logger import LoggerContract
from presidio_analyzer import AnalyzerEngine

from src.data_deidentifier.domain.contracts.validator import EntityTypeValidatorContract
from src.data_deidentifier.domain.exceptions import EntityTypeValidationError


class PresidioValidator(EntityTypeValidatorContract):
    """Validator for Presidio types."""

    def __init__(self, logger: LoggerContract) -> None:
        """Initialize the validator.

        Args:
            logger: Logger for logging events
        """
        self.logger = logger

        self.analyzer_engine = AnalyzerEngine()
        self._supported_entities = None  # Lazy loading

    @property
    def supported_entities(self) -> set[str]:
        """Get the supported entity types.

        Returns:
            Set of supported entity types
        """
        if self._supported_entities is None:
            self._supported_entities = set(
                self.analyzer_engine.get_supported_entities(),
            )
        return self._supported_entities

    def validate_entity_types(self, entity_types: list[str]) -> list[str]:
        """Validate and normalize entity types.

        Args:
            entity_types: List of entity types to validate

        Returns:
            List of validated and normalized entity types

        Raises:
            ValueError: If any entity type is not supported
        """
        if not entity_types:
            return []

        normalized_types = {e_type.upper() for e_type in entity_types}
        unsupported = normalized_types - self.supported_entities

        if unsupported:
            self.logger.warning(
                "Unsupported entity types provided",
                {"unsupported_entities": unsupported},
            )
            raise EntityTypeValidationError(
                f"Unsupported entity types: {', '.join(unsupported)}",
            )

        return list(normalized_types)
