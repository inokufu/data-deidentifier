from abc import ABC, abstractmethod
from typing import Any

from pandas import DataFrame
from presidio_structured import StructuredAnalysis

from data_deidentifier.domain.types.anonymization_operator import AnonymizationOperator
from data_deidentifier.domain.types.structured_anonymization_result import (
    StructuredDataAnalysisField,
)


class StructuredAnonymizationEngineContract(ABC):
    """Common interface for structured anonymization engines."""

    @abstractmethod
    def anonymize_structured(
        self,
        data: dict | DataFrame,
        structured_analysis: StructuredAnalysis,
        operator: AnonymizationOperator,
        fields: list[StructuredDataAnalysisField],
        operator_params: dict[str, Any] | None = None,
    ) -> tuple[dict | DataFrame, list[StructuredDataAnalysisField]]:
        """Anonymize structured data and return the result with detected fields."""
        raise NotImplementedError
