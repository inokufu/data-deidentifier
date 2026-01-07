from typing import Any

from data_deidentifier.domain.contracts.anonymizer.structured import (
    StructuredDataAnonymizerContract,
)
from data_deidentifier.domain.contracts.validator import EntityTypeValidatorContract
from data_deidentifier.domain.exceptions import InvalidInputDataError
from data_deidentifier.domain.types.anonymization_operator import (
    AnonymizationOperator,
)
from data_deidentifier.domain.types.language import SupportedLanguage
from data_deidentifier.domain.types.structured_anonymization_result import (
    StructuredDataAnonymizationResult,
)
from data_deidentifier.domain.types.structured_data import StructuredData


class StructuredDataAnonymizationService:
    """Service for anonymizing personally identifiable information in structured data.

    This service orchestrates the text anonymization process
    and produces structured anonymization results.
    """

    def __init__(
        self,
        anonymizer: StructuredDataAnonymizerContract,
        validator: EntityTypeValidatorContract,
    ) -> None:
        """Initialize the structured data anonymization service.

        Args:
            anonymizer: Implementation of the structured data anonymization contract
            validator: Implementation of the validator contract
        """
        self.anonymizer = anonymizer
        self.validator = validator

    def anonymize(
        self,
        data: StructuredData,
        operator: AnonymizationOperator,
        language: SupportedLanguage,
        entity_types: list[str],
        operator_params: dict[str, Any] | None = None,
    ) -> StructuredDataAnonymizationResult:
        """Anonymize PII entities in structured data.

        Args:
            data: The structured data to anonymize
            operator: Anonymization method to use
            language: Language code of the text
            entity_types: Entity types to detect
            operator_params: Optional parameters for the operator

        Returns:
            A StructuredDataAnonymizationResult containing anonymized data and metadata
        """
        if not data:
            raise InvalidInputDataError("Data cannot be empty")

        # Validate data
        effective_entity_types = self.validator.validate_entity_types(
            entity_types=entity_types,
        )

        # Anonymize the data
        return self.anonymizer.anonymize(
            data=data,
            operator=operator,
            operator_params=operator_params,
            entity_types=effective_entity_types,
            language=language,
        )
