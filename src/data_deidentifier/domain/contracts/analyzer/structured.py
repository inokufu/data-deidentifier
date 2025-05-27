from abc import ABC, abstractmethod

from src.data_deidentifier.domain.types.structured_analysis_result import (
    StructuredDataAnalysisField,
)
from src.data_deidentifier.domain.types.structured_data import StructuredData


class StructuredDataAnalyzerContract(ABC):
    """Abstract base class defining the structured analyzer interface."""

    @abstractmethod
    def analyze(
        self,
        data: StructuredData,
        language: str,
        entity_types: list[str] | None = None,
    ) -> list[StructuredDataAnalysisField]:
        """Analyze structured data to detect PII entities.

        Args:
            data: Structured data to analyze (DataFrame, JSON, etc.)
            language: Language code of the data content
            entity_types: Types of entities to detect (None means all supported types)

        Returns:
            List of fields with detected PII entities

        Raises:
            AnalyzeError: If analysis fails
        """
        raise NotImplementedError
