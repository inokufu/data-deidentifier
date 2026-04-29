from abc import ABC, abstractmethod
from typing import Any

from pandas import DataFrame
from presidio_anonymizer.entities import OperatorConfig
from presidio_structured import StructuredAnalysis

from data_deidentifier.domain.types.anonymization_operator import AnonymizationOperator
from data_deidentifier.domain.types.structured_anonymization_result import (
    StructuredDataAnalysisField,
)


class StructuredAnonymizationEngineContract(ABC):
    """Common interface for structured anonymization engines."""

    @abstractmethod
    def build_operators(
        self,
        operator: AnonymizationOperator,
        fields: list[StructuredDataAnalysisField],
        operator_params: dict[str, Any] | None,
    ) -> dict[str, OperatorConfig]:
        """Build operator configurations for the anonymization step."""
        raise NotImplementedError

    @abstractmethod
    def anonymize(
        self,
        data: dict | DataFrame,
        structured_analysis: StructuredAnalysis,
        operators: dict[str, OperatorConfig] | None = None,
    ) -> dict | DataFrame:
        """Anonymize structured data using the given operator configurations."""
        raise NotImplementedError

    @property
    @abstractmethod
    def detected_fields(self) -> list[StructuredDataAnalysisField]:
        """Fields detected for anonymization."""
        raise NotImplementedError
