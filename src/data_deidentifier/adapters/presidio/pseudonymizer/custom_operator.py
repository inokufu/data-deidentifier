from typing import TYPE_CHECKING, override

from presidio_anonymizer.operators import Operator, OperatorType

from src.data_deidentifier.domain.exceptions import PseudonymEnrichmentError
from src.data_deidentifier.domain.types.anonymization_operator import (
    AnonymizationOperator,
)
from src.data_deidentifier.domain.types.entity import Entity

if TYPE_CHECKING:
    from src.data_deidentifier.adapters.infrastructure.config.contract import (
        ConfigContract,
    )
    from src.data_deidentifier.domain.contracts.enricher.manager import (
        PseudonymEnrichmentManagerContract,
    )
    from src.data_deidentifier.domain.contracts.pseudonymizer.method import (
        PseudonymizationMethodContract,
    )


class PseudonymizeOperator(Operator):
    """Custom Presidio operator for pseudonymization with optional enrichment.

    This operator extends Presidio's anonymization capabilities by providing
    pseudonymization instead of simple redaction or masking. It generates
    consistent pseudonyms for entities and optionally enriches them with
    contextual information.

    Attributes:
        PARAM_METHOD: Parameter key for the pseudonymization method.
        PARAM_ENRICHER: Parameter key for the optional pseudonym enricher.

    Examples:
        Input text: "John lives in London"
        Output: "<PERSON_123> lives in <LOCATION_456> (United Kingdom)"
    """

    PARAM_METHOD: str = "method"
    PARAM_ENRICHER: str = "enricher"
    PARAM_CONFIG: str = "config"

    @override
    def operate(self, text: str, params: dict | None = None) -> str:
        """Generate a pseudonym for the entity, using a PseudonymizationMethodContract.

        Args:
            text: The original entity text
            params: Parameters containing method, entity_type, enrichment infos, etc.

        Returns:
            The pseudonymized text
        """
        if params is None or "entity_type" not in params:
            raise ValueError("Parameters dictionary is required")

        entity = Entity(
            text=text,
            type=params["entity_type"],
            start=params.get("start", 0),
            end=params.get("end", len(text)),
            score=params.get("score", 1.0),
        )

        # Generate the base pseudonym
        pseudonym = self._generate_pseudonym(entity=entity, params=params)

        # Get enrichment if available
        enrichment = self._get_enrichment(entity=entity, params=params)

        # Combine pseudonym and enrichment
        if enrichment:
            return f"{pseudonym} ({enrichment})"

        return pseudonym

    def _generate_pseudonym(self, entity: Entity, params: dict) -> str:
        """Generate the base pseudonym for an entity.

        Args:
            entity: The entity to pseudonymize
            params: Parameters containing the pseudonymization method

        Returns:
            The base pseudonym
        """
        method: PseudonymizationMethodContract = params.get(self.PARAM_METHOD)
        return method.generate_pseudonym(entity=entity)

    def _get_enrichment(self, entity: Entity, params: dict) -> str | None:
        """Get enrichment information for an entity if available.

        Args:
            entity: The entity being pseudonymized
            params: Parameters containing enrichment configuration

        Returns:
            The enrichment text if available, None otherwise
        """
        config: ConfigContract = params.get(self.PARAM_CONFIG)
        enricher: PseudonymEnrichmentManagerContract | None = params.get(
            self.PARAM_ENRICHER,
        )

        # Check if enrichment is available and configured for this entity type
        if not enricher or not config:
            return None

        enrichable_types = config.get_enrichment_configurations()
        if not enrichable_types or entity.type not in enrichable_types:
            return None

        try:
            # Get method for this entity type
            enrichment_method = enricher.get_enricher_for_entity(entity.type)
            if not enrichment_method:
                return None

            # Get enrichment
            return enrichment_method.get_enrichment(entity)

        except PseudonymEnrichmentError:
            # If enrichment fails, return None
            return None

    @override
    def validate(self, params: dict | None = None) -> None:
        """Validate operator parameters."""
        if not params:
            raise ValueError("Parameters are required")

        if self.PARAM_METHOD not in params:
            raise ValueError("A 'method' parameter is required")

        if self.PARAM_CONFIG not in params:
            raise ValueError("A 'config' parameter is required")

        if "entity_type" not in params:
            raise ValueError("A 'entity_type' parameter is required")

    @override
    def operator_name(self) -> str:
        """Return operator name."""
        return AnonymizationOperator.PSEUDONYMIZE.value

    @override
    def operator_type(self) -> OperatorType:
        """Return operator type."""
        return OperatorType.Anonymize
