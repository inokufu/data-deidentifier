from typing import Any, cast, override

from pandas import DataFrame
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
    "<PERSON>").
    """

    def __init__(self, text_anonymizer: AnonymizerEngine) -> None:
        """Initialize with the text anonymizer engine.

        Args:
            text_anonymizer: Presidio AnonymizerEngine used for span-level replacement.
        """
        super().__init__(data_processor=JsonDataProcessor())
        self._text_anonymizer = text_anonymizer

    @override
    def anonymize_structured(
        self,
        data: dict | DataFrame,
        structured_analysis: StructuredAnalysis,
        operator: AnonymizationOperator,
        fields: list[StructuredDataAnalysisField],
        operator_params: dict[str, Any] | None = None,
    ) -> tuple[dict | DataFrame, list[StructuredDataAnalysisField]]:
        """Anonymize JSON data using span-level text replacement.

        Args:
            data: Flattened JSON dict to anonymize in-place.
            structured_analysis: Must be a StructuredAnalysisWithSpans instance.
            operator: Anonymization operator to apply.
            fields: Detected fields (unused — spans carry entity type directly).
            operator_params: Optional operator parameters.

        Returns:
            Tuple of anonymized data and detected fields.
        """
        if not isinstance(structured_analysis, StructuredAnalysisWithSpans):
            return data, []

        operators = {
            "DEFAULT": OperatorConfig(
                operator_name=operator,
                params=operator_params or {},
            ),
        }

        detected_fields: list[StructuredDataAnalysisField] = []
        data_dict = cast(dict[str, Any], data)
        for field_path, spans in structured_analysis.spans_mapping.items():
            value = get_nested_value(data_dict, field_path)
            if not isinstance(value, str):
                continue

            result = self._text_anonymizer.anonymize(
                text=value,
                analyzer_results=cast(list, spans),
                operators=operators,
            )

            set_nested_value(data_dict, field_path, result.text)
            field_name = ".".join(field_path)
            detected_fields.extend(
                StructuredDataAnalysisField(
                    field_name=field_name,
                    entity_type=item.entity_type,
                )
                for item in (result.items or [])
            )

        return data, detected_fields
