from abc import ABC, abstractmethod
from typing import Any

from logger import LoggerContract

from data_deidentifier.domain.types.entity import Entity


class PseudonymEnricherContract(ABC):
    """Contract for pseudonym enrichment services.

    Defines the interface for services that provide additional contextual information
    for detected PII entities that enhance the output while maintaining privacy.
    """

    def __init__(self, params: dict[str, Any], logger: LoggerContract) -> None:
        """Initialize the enrichment method.

        Args:
            params: Optional parameters for the method configuration
            logger: Logger for logging events
        """
        self.params = params
        self.logger = logger

    @abstractmethod
    def get_enrichment(self, entity: Entity) -> str | None:
        """Get enrichment information for a detected entity.

        Analyzes the provided entity and returns contextual information that can
        be safely included with the result without compromising privacy.

        Args:
            entity: The detected PII entity to enrich. Contains the entity text,
                type, confidence score, and position information.

        Returns:
            str | None: Enrichment information as a string if available.

        Raises:
            PseudonymEnrichmentError: If an error while enriching occurs.
        """
        raise NotImplementedError
