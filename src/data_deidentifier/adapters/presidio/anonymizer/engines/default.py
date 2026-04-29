from typing import Any, override

from pandas import DataFrame
from presidio_anonymizer.entities import OperatorConfig
from presidio_structured import StructuredAnalysis
from presidio_structured.data.data_processors import DataProcessorBase
from presidio_structured.structured_engine import StructuredEngine

from data_deidentifier.domain.types.anonymization_operator import AnonymizationOperator
from data_deidentifier.domain.types.structured_anonymization_result import (
    StructuredDataAnalysisField,
)

from .contract import StructuredAnonymizationEngineContract


class DefaultStructuredEngine(StructuredAnonymizationEngineContract, StructuredEngine):
    """Wraps StructuredEngine with build_operators and detected_fields support."""

    def __init__(self, processor: DataProcessorBase) -> None:
        """Initialize with a data processor.

        Args:
            processor: Presidio data processor for the engine.
        """
        super().__init__(data_processor=processor)
        self._detected_fields: list[StructuredDataAnalysisField] = []

    @property
    @override
    def detected_fields(self) -> list[StructuredDataAnalysisField]:
        """Fields detected in the last build_operators() call."""
        return self._detected_fields

    @override
    def build_operators(
        self,
        operator: AnonymizationOperator,
        fields: list[StructuredDataAnalysisField],
        operator_params: dict[str, Any] | None,
    ) -> dict[str, OperatorConfig]:
        # Create entity-specific OperatorConfig instead of single DEFAULT config
        # Required because structured data processing doesn't auto-inject entity_type
        # into params (unlike text anonymization), but our PseudonymizeOperator needs it
        self._detected_fields = fields
        return {
            field.entity_type: OperatorConfig(
                operator_name=operator,
                params={
                    **(operator_params or {}),
                    "entity_type": field.entity_type,
                },
            )
            for field in fields
        }

    @override
    def anonymize(
        self,
        data: dict | DataFrame,
        structured_analysis: StructuredAnalysis,
        operators: dict[str, OperatorConfig] | None = None,
    ) -> dict | DataFrame:
        # Delegate anonymization to the wrapped StructuredEngine.
        return super().anonymize(
            data=data,
            structured_analysis=structured_analysis,
            operators=operators,
        )
