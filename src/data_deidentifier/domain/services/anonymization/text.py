from typing import Any

from data_deidentifier.domain.contracts.anonymizer.text import (
    TextAnonymizerContract,
)
from data_deidentifier.domain.contracts.validator import EntityTypeValidatorContract
from data_deidentifier.domain.exceptions import (
    InvalidInputTextError,
)
from data_deidentifier.domain.types.anonymization_operator import (
    AnonymizationOperator,
)
from data_deidentifier.domain.types.language import SupportedLanguage
from data_deidentifier.domain.types.text_anonymization_result import (
    TextAnonymizationResult,
)


class TextAnonymizationService:
    """Service for anonymizing personally identifiable information in text.

    This service orchestrates the text anonymization process
    and produces structured anonymization results.
    """

    def __init__(
        self,
        anonymizer: TextAnonymizerContract,
        validator: EntityTypeValidatorContract,
    ) -> None:
        """Initialize the text anonymization service.

        Args:
            anonymizer: Implementation of the text anonymization contract
            validator: Implementation of the validator contract
        """
        self.anonymizer = anonymizer
        self.validator = validator

    def anonymize(  # noqa: PLR0913
        self,
        text: str,
        operator: AnonymizationOperator,
        language: SupportedLanguage,
        min_score: float,
        entity_types: list[str],
        operator_params: dict[str, Any] | None = None,
    ) -> TextAnonymizationResult:
        """Anonymize PII entities in text.

        Args:
            text: The text to anonymize
            operator: Anonymization method to use
            language: Language code of the text
            min_score: Minimum confidence score
            entity_types: Entity types to detect
            operator_params: Optional parameters for the operator

        Returns:
            An AnonymizationResult containing the anonymized text and metadata
        """
        if not text or not text.strip():
            raise InvalidInputTextError("Text cannot be empty")

        # Validate data
        effective_entity_types = self.validator.validate_entity_types(
            entity_types=entity_types,
        )

        # Anonymize the text
        return self.anonymizer.anonymize(
            text=text,
            operator=operator,
            operator_params=operator_params,
            entity_types=effective_entity_types,
            language=language,
            min_score=min_score,
        )
