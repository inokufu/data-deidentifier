import threading
from typing import Any, override

from logger import LoggerContract

from data_deidentifier.domain.contracts.pseudonymizer.method import (
    PseudonymizationMethodContract,
)
from data_deidentifier.domain.types.entity import Entity


class CounterPseudonymizationMethod(PseudonymizationMethodContract):
    """Counter pseudonymization method with intra-request consistency."""

    PARAM_START_NUMBER = "start_number"
    DEFAULT_START_NUMBER = 1

    def __init__(self, params: dict[str, Any], logger: LoggerContract) -> None:
        """Initialize the counter method.

        Args:
            params: Method parameters (start_number, etc.)
            logger: Logger for logging events
        """
        super().__init__(params=params, logger=logger)

        # Cache by entity type and text
        self._mapping: dict[str, dict[str, str]] = {}

        # Counters by entity_type
        self._counters: dict[str, int] = {}

        # Configuration
        self._start_number = self.params.get(
            self.PARAM_START_NUMBER,
            self.DEFAULT_START_NUMBER,
        )
        if self._start_number is not None and not isinstance(self._start_number, int):
            raise ValueError("start_number must be an integer")
        if self._start_number is not None and self._start_number < 0:
            raise ValueError("start_number must be positive")

        # Thread safety for concurrent access
        self._lock = threading.Lock()

    @override
    def generate_pseudonym(self, entity: Entity) -> str:
        if entity.text is None:
            return ""

        cache_key = entity.text
        entity_type = entity.type

        with self._lock:
            # Mapping by entity type
            if entity_type not in self._mapping:
                self._mapping[entity_type] = {}
                self._counters[entity_type] = self._start_number
            else:
                # Check if we already have a pseudonym for this entity
                entity_mapping_for_type = self._mapping[entity_type]
                if cache_key in entity_mapping_for_type:
                    return entity_mapping_for_type[cache_key]

            # Generate new pseudonym with current counter
            current_count = self._counters.get(entity_type)
            pseudonym = f"<{entity_type}_{current_count}>"

            # Store in cache
            self._mapping[entity_type][cache_key] = pseudonym
            self._counters[entity_type] += 1

            return pseudonym
