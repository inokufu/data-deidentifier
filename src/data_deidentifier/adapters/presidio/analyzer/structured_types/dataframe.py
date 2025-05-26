from typing import Any, override

import pandas as pd
from logger import LoggerContract
from presidio_structured import (
    PandasAnalysisBuilder,
    StructuredAnalysis,
)
from presidio_structured.data.data_processors import (
    DataProcessorBase,
    PandasDataProcessor,
)

from .structured_type import StructuredTypeAnalyzer


class DataFrameAnalyzer(StructuredTypeAnalyzer):
    """Analyzer for pandas DataFrame data.

    This class implements analysis for pandas DataFrame objects using
    Presidio's PandasAnalysisBuilder.
    """

    def __init__(self, logger: LoggerContract) -> None:
        """Initialize the DataFrame analyzer.

        Args:
            logger: Logger instance for logging events.
        """
        super().__init__(logger)
        self.analyzer = PandasAnalysisBuilder()

    @override
    def can_handle(self, data: Any) -> bool:
        return isinstance(data, pd.DataFrame)

    @override
    def analyze(
        self,
        data: Any,
        language: str,
    ) -> StructuredAnalysis:
        self.logger.debug("Analyzing DataFrame", {"nb_rows": len(data)})

        return self.analyzer.generate_analysis(
            df=data,
            language=language,
        )

    @override
    def get_data_processor(self) -> DataProcessorBase:
        return PandasDataProcessor()
