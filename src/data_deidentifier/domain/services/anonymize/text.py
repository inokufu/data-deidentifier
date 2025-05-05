from src.data_deidentifier.domain.contracts.anonymizer.text import (
    TextAnonymizerContract,
)
from src.data_deidentifier.domain.contracts.validator import EntityTypeValidatorContract
from src.data_deidentifier.domain.types.anonymization_result import AnonymizationResult
from src.data_deidentifier.domain.types.entity import Entity
from src.data_deidentifier.domain.types.operators import AnonymizationOperator


class TextAnonymizationService:
    """Service for anonymizing personally identifiable information in text.

    This service orchestrates the text anonymization process, manages default values,
    and produces structured anonymization results.
    """

    def __init__(
        self,
        anonymizer: TextAnonymizerContract,
        validator: EntityTypeValidatorContract,
        default_operator: AnonymizationOperator,
    ) -> None:
        """Initialize the anonymizer service.

        Args:
            anonymizer: Implementation of the anonymizer contract
            validator: Implementation of the validator contract
            default_operator: Default anonymization operator if not specified
        """
        self.anonymizer = anonymizer
        self.validator = validator
        self.default_operator = default_operator

    def anonymize(
        self,
        text: str,
        entities: list[Entity],
        operator: AnonymizationOperator | None = None,
    ) -> AnonymizationResult:
        """Anonymize PII entities in text.

        Args:
            text: The text to anonymize
            entities: Pre-detected entities
            operator: Anonymization method to use (defaults to configured default)

        Returns:
            An AnonymizationResult containing the anonymized text and metadata
        """
        effective_operator = operator or self.default_operator

        # Validate data
        entity_types = [entity.type for entity in entities]
        effective_entity_types = self.validator.validate_entity_types(
            entity_types=entity_types,
        )

        # Anonymize the text
        anonymized_text = self.anonymizer.anonymize(
            text=text,
            entities=entities,
            operator=effective_operator,
        )

        # Build stats
        entity_stats = {}
        for entity_type in effective_entity_types:
            entity_stats[entity_type] = entity_stats.get(entity_type, 0) + 1

        return AnonymizationResult(
            anonymized_text=anonymized_text,
            operator=effective_operator,
            entity_stats=entity_stats,
        )
