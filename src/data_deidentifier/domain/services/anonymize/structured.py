from src.data_deidentifier.domain.contracts.anonymizer.structured import (
    StructuredDataAnonymizerContract,
)
from src.data_deidentifier.domain.contracts.validator import EntityTypeValidatorContract
from src.data_deidentifier.domain.types.operators import AnonymizationOperator
from src.data_deidentifier.domain.types.structured_analysis_result import (
    StructuredDataAnalysisField,
)
from src.data_deidentifier.domain.types.structured_anonymization_result import (
    StructuredDataAnonymizationResult,
)
from src.data_deidentifier.domain.types.structured_data import StructuredData


class StructuredDataAnonymizationService:
    """Service for anonymizing personally identifiable information in structured data.

    This service orchestrates the text anonymization process, manages default values,
    and produces structured anonymization results.
    """

    def __init__(
        self,
        anonymizer: StructuredDataAnonymizerContract,
        validator: EntityTypeValidatorContract,
        default_operator: AnonymizationOperator,
    ) -> None:
        """Initialize the structured data anonymization service.

        Args:
            anonymizer: Implementation of the structured data anonymization contract
            validator: Implementation of the validator contract
            default_operator: Default anonymization operator if not specified
        """
        self.anonymizer = anonymizer
        self.validator = validator
        self.default_operator = default_operator

    def anonymize(
        self,
        data: StructuredData,
        fields: list[StructuredDataAnalysisField],
        operator: AnonymizationOperator | None = None,
    ) -> StructuredDataAnonymizationResult:
        """Anonymize PII entities in structured data.

        Args:
            data: The structured data to anonymize
            fields: Pre-detected fields with their entity types
            operator: Anonymization method to use (defaults to configured default)

        Returns:
            A StructuredDataAnonymizationResult containing anonymized data and metadata
        """
        effective_operator = operator or self.default_operator

        # Validate entity types
        entity_types = [field.entity_type for field in fields]
        effective_entity_types = self.validator.validate_entity_types(
            entity_types=entity_types,
        )

        # Filter fields to only include validated entity types
        effective_fields = [
            field for field in fields if field.entity_type in effective_entity_types
        ]

        # Anonymize the data
        anonymized_data = self.anonymizer.anonymize(
            data=data,
            fields=effective_fields,
            operator=effective_operator,
        )

        # Build stats
        entity_stats = {}
        for field in effective_fields:
            entity_type = field.entity_type
            entity_stats[entity_type] = entity_stats.get(entity_type, 0) + 1

        return StructuredDataAnonymizationResult(
            anonymized_data=anonymized_data,
            operator=effective_operator,
            entity_stats=entity_stats,
        )
