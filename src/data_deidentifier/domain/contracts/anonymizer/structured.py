from abc import ABC, abstractmethod

from src.data_deidentifier.domain.types.operators import AnonymizationOperator
from src.data_deidentifier.domain.types.structured_analysis_result import (
    StructuredDataAnalysisField,
)
from src.data_deidentifier.domain.types.structured_data import StructuredData


class StructuredDataAnonymizerContract(ABC):
    """Abstract base class defining the structured anonymizer interface."""

    @abstractmethod
    def anonymize(
        self,
        data: StructuredData,
        fields: list[StructuredDataAnalysisField],
        operator: AnonymizationOperator,
    ) -> StructuredData:
        """Anonymize PII entities in structured data.

        Args:
            data: Original structured data containing PII entities
            fields: List of fields with their entity types to anonymize
            operator: Anonymization method

        Returns:
            Anonymized structured data with PII entities replaced

        Raises:
            AnonymizationError: If anonymization fails
        """
        raise NotImplementedError
