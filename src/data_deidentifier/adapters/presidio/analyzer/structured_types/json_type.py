from typing import Any, override

from logger import LoggerContract
from presidio_structured import (
    JsonAnalysisBuilder,
    StructuredAnalysis,
)
from presidio_structured.data.data_processors import (
    DataProcessorBase,
    JsonDataProcessor,
)

from .structured_type import StructuredTypeAnalyzer


class JsonAnalyzer(StructuredTypeAnalyzer):
    """Analyzer for JSON data.

    This class implements analysis for JSON-formatted data (Python dictionaries)
    using Presidio's JsonAnalysisBuilder.
    """

    def __init__(self, logger: LoggerContract) -> None:
        """Initialize the JSON analyzer.

        Args:
            logger: Logger instance for logging events.
        """
        super().__init__(logger)
        self.analyzer = JsonAnalysisBuilder()

    @override
    def can_handle(self, data: Any) -> bool:
        return isinstance(data, dict)

    @override
    def analyze(self, data: Any, language: str) -> StructuredAnalysis:
        self.logger.debug("Analyzing JSON data", {"nb_keys": len(data)})

        return self.analyzer.generate_analysis(
            data=data,
            language=language,
        )

    @override
    def get_data_processor(self) -> DataProcessorBase:
        return JsonDataProcessor()
