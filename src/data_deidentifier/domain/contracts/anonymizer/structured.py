from abc import ABC, abstractmethod
from typing import Any

from data_deidentifier.domain.types.anonymization_operator import (
    AnonymizationOperator,
)
from data_deidentifier.domain.types.language import SupportedLanguage
from data_deidentifier.domain.types.structured_anonymization_result import (
    StructuredDataAnonymizationResult,
)
from data_deidentifier.domain.types.structured_data import StructuredData


class StructuredDataAnonymizerContract(ABC):
    """Abstract base class defining the structured anonymizer interface."""

    @abstractmethod
    def anonymize(
        self,
        data: StructuredData,
        operator: AnonymizationOperator,
        language: SupportedLanguage,
        entity_types: list[str] | None = None,
        operator_params: dict[str, Any] | None = None,
    ) -> StructuredDataAnonymizationResult:
        """Anonymize PII entities in structured data.

        Args:
            data: Original structured data containing PII entities
            operator: Anonymization method
            language: Language code of the data content
            entity_types: Types of entities to detect (None means all supported types)
            operator_params: Optional parameters for the operator

        Returns:
            A StructuredDataAnonymizationResult containing anonymized data and metadata

        Raises:
            AnonymizationError: If anonymization fails
        """
        raise NotImplementedError
