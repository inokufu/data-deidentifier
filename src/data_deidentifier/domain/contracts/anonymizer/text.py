from abc import ABC, abstractmethod
from typing import Any

from data_deidentifier.domain.types.anonymization_operator import (
    AnonymizationOperator,
)
from data_deidentifier.domain.types.language import SupportedLanguage
from data_deidentifier.domain.types.text_anonymization_result import (
    TextAnonymizationResult,
)


class TextAnonymizerContract(ABC):
    """Abstract base class defining the text anonymizer interface."""

    @abstractmethod
    def anonymize(  # noqa: PLR0913
        self,
        text: str,
        operator: AnonymizationOperator,
        language: SupportedLanguage,
        min_score: float,
        entity_types: list[str] | None = None,
        operator_params: dict[str, Any] | None = None,
    ) -> TextAnonymizationResult:
        """Anonymize PII entities in text.

        Args:
            text: Original text containing PII entities
            operator: Anonymization method
            language: Language code of the text
            min_score: Minimum confidence score threshold
            entity_types: Types of entities to detect (None means all supported types)
            operator_params: Optional parameters for the operator

        Returns:
            An AnonymizationResult containing the anonymized text and metadata

        Raises:
            AnonymizationError: If anonymization fails
        """
        raise NotImplementedError
