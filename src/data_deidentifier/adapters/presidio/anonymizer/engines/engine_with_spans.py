from typing import Any, cast, override

from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_structured import StructuredAnalysis
from presidio_structured.data.data_processors import JsonDataProcessor
from presidio_structured.structured_engine import StructuredEngine

from data_deidentifier.adapters.presidio.analyzer.structured_types.JSON import (
    StructuredAnalysisWithSpans,
)
from data_deidentifier.adapters.presidio.json_utils import (
    get_nested_value,
    set_nested_value,
)
from data_deidentifier.domain.types.anonymization_operator import AnonymizationOperator
from data_deidentifier.domain.types.structured_anonymization_result import (
    StructuredDataAnalysisField,
)

from .contract import StructuredAnonymizationEngineContract


class StructuredEngineWithSpans(
    StructuredEngine,
    StructuredAnonymizationEngineContract,
):
    """StructuredEngine extension for span-level JSON anonymization.

    Unlike Presidio's StructuredEngine which replaces entire field values,
    this engine uses the text anonymizer with per-field spans to replace only
    the detected entity within the value (e.g. "<PERSON> is kind" instead of
    "<PERSON>"). Detected fields are available via the detected_fields property
    after each anonymize() call.
    """

    def __init__(self, text_anonymizer: AnonymizerEngine) -> None:
        """Initialize with the text anonymizer engine.

        Args:
            text_anonymizer: Presidio AnonymizerEngine used for span-level replacement.
        """
        super().__init__(data_processor=JsonDataProcessor())
        self._text_anonymizer = text_anonymizer
        self._detected_fields: list[StructuredDataAnalysisField] = []

    @property
    @override
    def detected_fields(self) -> list[StructuredDataAnalysisField]:
        # Fields actually anonymized in the last anonymize() call.
        return self._detected_fields

    @override
    def build_operators(
        self,
        operator: AnonymizationOperator,
        fields: list[StructuredDataAnalysisField],
        operator_params: dict[str, Any] | None,
    ) -> dict[str, OperatorConfig]:
        return {
            "DEFAULT": OperatorConfig(
                operator_name=operator,
                params=operator_params or {},
            ),
        }

    @override
    def anonymize(
        self,
        data: Any,
        structured_analysis: StructuredAnalysis,
        operators: dict[str, OperatorConfig] | None = None,
    ) -> Any:
        self._detected_fields = []

        if not isinstance(structured_analysis, StructuredAnalysisWithSpans):
            return data

        if operators is None:
            operators = {}

        for field_path, spans in structured_analysis.spans_mapping.items():
            value = get_nested_value(data, field_path)
            if not isinstance(value, str):
                continue

            result = self._text_anonymizer.anonymize(
                text=value,
                analyzer_results=cast(list, spans),
                operators=operators,
            )

            set_nested_value(data, field_path, result.text)
            field_name = ".".join(field_path)
            self._detected_fields.extend(
                StructuredDataAnalysisField(
                    field_name=field_name,
                    entity_type=item.entity_type,
                )
                for item in (result.items or [])
            )

        return data
