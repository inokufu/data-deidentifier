import secrets
from typing import Any, override

from logger import LoggerContract

from data_deidentifier.domain.contracts.pseudonymizer.method import (
    PseudonymizationMethodContract,
)
from data_deidentifier.domain.types.entity import Entity


class RandomNumberPseudonymizationMethod(PseudonymizationMethodContract):
    """Random number pseudonymization method with intra-request consistency."""

    RANDOM_BITS_NUMBER = 24

    def __init__(self, params: dict[str, Any], logger: LoggerContract) -> None:
        """Initialize the random number method.

        Args:
            params: Method parameters
            logger: Logger for logging events
        """
        super().__init__(params=params, logger=logger)

        # Cache by entity type and text
        self._mapping: dict[str, dict[str, str]] = {}

    @override
    def generate_pseudonym(self, entity: Entity) -> str:
        if entity.text is None:
            return ""

        cache_key = entity.text
        entity_type = entity.type

        # Mapping by entity type
        if entity_type not in self._mapping:
            self._mapping[entity_type] = {}

        # Check if we already have a pseudonym for this entity
        entity_mapping_for_type = self._mapping[entity_type]
        if cache_key in entity_mapping_for_type:
            return entity_mapping_for_type[cache_key]

        # Generate base random number
        random_number = secrets.randbits(self.RANDOM_BITS_NUMBER)

        # Format the pseudonym
        pseudonym = f"<{entity_type}_{random_number}>"

        # Store in cache
        self._mapping[entity_type][cache_key] = pseudonym
        return pseudonym
