from typing import override

from logger import LoggerContract

from data_deidentifier.adapters.presidio.engines import PresidioEngineFactory
from data_deidentifier.domain.contracts.validator import EntityTypeValidatorContract
from data_deidentifier.domain.exceptions import EntityTypeValidationError


class PresidioValidator(EntityTypeValidatorContract):
    """Validator for Presidio types."""

    def __init__(self, logger: LoggerContract) -> None:
        """Initialize the validator.

        Args:
            logger: Logger for logging events
        """
        self.logger = logger

        self.analyzer_engine = PresidioEngineFactory.get_analyzer_engine()
        self._supported_entities: set[str] | None = None  # Lazy loading

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

    @override
    def validate_entity_types(self, entity_types: list[str]) -> list[str]:
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
