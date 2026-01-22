from abc import ABC, abstractmethod

from data_deidentifier.domain.contracts.enricher.enricher import (
    PseudonymEnricherContract,
)


class PseudonymEnrichmentManagerContract(ABC):
    """Contract for managing enrichment services.

    Defines the interface for services that coordinate the creation and
    management of enrichers for different entity types.
    """

    @abstractmethod
    def get_enricher_for_entity(
        self,
        entity_type: str,
    ) -> PseudonymEnricherContract | None:
        """Get an enricher instance for a specific entity type.

        Args:
            entity_type: The type of entity to get an enricher for

        Returns:
            PseudonymEnricherContract | None: An enricher instance if available
                for this entity type, None otherwise.

        Raises:
            PseudonymEnrichmentError: If an error occurs while creating the enricher.
        """
        raise NotImplementedError
