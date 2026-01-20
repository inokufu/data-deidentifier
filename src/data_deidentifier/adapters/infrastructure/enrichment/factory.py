from typing import Any, ClassVar, override

from logger import LoggerContract

from data_deidentifier.adapters.infrastructure.config.contract import ConfigContract
from data_deidentifier.domain.contracts.enricher.enricher import (
    PseudonymEnricherContract,
)
from data_deidentifier.domain.contracts.enricher.manager import (
    PseudonymEnrichmentManagerContract,
)
from data_deidentifier.domain.exceptions import PseudonymEnrichmentError
from data_deidentifier.domain.types.enrichment_type import EnrichmentType

from .http_service import HttpPseudonymEnricher


class EnrichmentFactory(PseudonymEnrichmentManagerContract):
    """Factory for creating enrichment service instances.

    This factory creates appropriate enricher instances based on the enrichment
    configuration type and parameters. It implements the EnrichmentManagerContract
    to integrate with the domain layer.
    """

    # Mapping between enrichment types and implementation classes
    _TYPE_MAPPING: ClassVar[dict[EnrichmentType, type[PseudonymEnricherContract]]] = {
        EnrichmentType.HTTP: HttpPseudonymEnricher,
    }

    def __init__(self, config: ConfigContract, logger: LoggerContract) -> None:
        """Initialize the enrichment factory.

        Args:
            config: Application configuration
            logger: Logger instance
        """
        self.config = config
        self.logger = logger

    @override
    def get_enricher_for_entity(
        self,
        entity_type: str,
    ) -> PseudonymEnricherContract | None:
        """Get an enricher instance for a specific entity type.

        Args:
            entity_type: The type of entity to get an enricher for

        Returns:
            An enricher instance if configuration exists for this entity type,
            None otherwise.

        Raises:
            PseudonymEnrichmentError: If enrichment configuration is invalid
        """
        enrichment_configs = self.config.get_enrichment_configurations()
        if entity_type not in enrichment_configs:
            return None

        entity_config = enrichment_configs.get(entity_type)
        if not entity_config:
            return None

        try:
            return self.create(
                entity_type=entity_type,
                enrichment_config=entity_config,
                logger=self.logger,
            )
        except PseudonymEnrichmentError as e:
            self.logger.exception("Enrichment error", e)
            raise

    @classmethod
    def create(
        cls,
        entity_type: str,
        enrichment_config: dict[str, Any],
        logger: LoggerContract,
    ) -> PseudonymEnricherContract:
        """Create an enricher instance based on configuration.

        Args:
            entity_type: The type of entity to enrich
            enrichment_config: Configuration for this entity type's enrichment
            logger: Logger instance

        Returns:
            An enricher instance implementing PseudonymEnricherContract

        Raises:
            PseudonymEnrichmentError: If enrichment type is not supported
        """
        enrichment_type_str = enrichment_config.get("type")
        if not enrichment_type_str:
            raise PseudonymEnrichmentError(
                f"Missing 'type' in enrichment config for entity type '{entity_type}'",
            )

        try:
            enrichment_type = EnrichmentType(enrichment_type_str.lower())
        except ValueError as e:
            raise PseudonymEnrichmentError("Unsupported enrichment type") from e

        if enrichment_type not in cls._TYPE_MAPPING:
            raise PseudonymEnrichmentError(
                f"No implementation available for enrichment type '{enrichment_type}'",
            )

        enrichment_cls = cls._TYPE_MAPPING[enrichment_type]

        return enrichment_cls(params=enrichment_config, logger=logger)

    @classmethod
    def get_supported_types(cls) -> list[EnrichmentType]:
        """Get list of supported enrichment types.

        Returns:
            List of supported enrichment types
        """
        return list(cls._TYPE_MAPPING.keys())
