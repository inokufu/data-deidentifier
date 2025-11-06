from typing import Any, override

from presidio_structured import (
    JsonAnalysisBuilder,
    StructuredAnalysis,
)
from presidio_structured.data.data_processors import (
    DataProcessorBase,
    JsonDataProcessor,
)

from src.data_deidentifier.domain.types.language import SupportedLanguage

from .structured_type import StructuredTypeAnalyzer


class JsonAnalyzer(StructuredTypeAnalyzer):
    """Analyzer for JSON data.

    This class implements analysis for JSON-formatted data (Python dictionaries)
    using Presidio's JsonAnalysisBuilder.
    """

    @staticmethod
    @override
    def can_handle(data: Any) -> bool:
        return isinstance(data, dict)

    @override
    def analyze(self, data: Any, language: SupportedLanguage) -> StructuredAnalysis:
        self.logger.debug("Analyzing JSON data", {"nb_keys": len(data)})

        analyzer = JsonAnalysisBuilder()
        return analyzer.generate_analysis(
            data=data,
            language=language,
        )

    @override
    def get_data_processor(self) -> DataProcessorBase:
        if self._data_processor is None:
            self._data_processor = JsonDataProcessor()
        return self._data_processor
