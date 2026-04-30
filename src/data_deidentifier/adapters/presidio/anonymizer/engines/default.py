from typing import Any, override

from pandas import DataFrame
from presidio_anonymizer.entities import OperatorConfig
from presidio_structured import StructuredAnalysis
from presidio_structured.structured_engine import StructuredEngine

from data_deidentifier.domain.types.anonymization_operator import AnonymizationOperator
from data_deidentifier.domain.types.structured_anonymization_result import (
    StructuredDataAnalysisField,
)

from .contract import StructuredAnonymizationEngineContract


class DefaultStructuredEngine(StructuredEngine, StructuredAnonymizationEngineContract):
    """Extends StructuredEngine with anonymize_structured support."""

    @override
    def anonymize_structured(
        self,
        data: dict | DataFrame,
        structured_analysis: StructuredAnalysis,
        operator: AnonymizationOperator,
        fields: list[StructuredDataAnalysisField],
        operator_params: dict[str, Any] | None = None,
    ) -> tuple[dict | DataFrame, list[StructuredDataAnalysisField]]:
        # Create entity-specific OperatorConfig instead of single DEFAULT config
        # Required because structured data processing doesn't auto-inject entity_type
        # into params (unlike text anonymization), but our PseudonymizeOperator needs it
        operators = {
            field.entity_type: OperatorConfig(
                operator_name=operator,
                params={
                    **(operator_params or {}),
                    "entity_type": field.entity_type,
                },
            )
            for field in fields
        }

        result = self.anonymize(
            data=data,
            structured_analysis=structured_analysis,
            operators=operators,
        )

        detected_fields = [
            StructuredDataAnalysisField(
                field_name=name,
                entity_type=entity_type,
            )
            for name, entity_type in structured_analysis.entity_mapping.items()
        ]
        return result, detected_fields
