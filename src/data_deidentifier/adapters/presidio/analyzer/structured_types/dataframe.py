from typing import Any, override

import pandas as pd
from presidio_structured import (
    PandasAnalysisBuilder,
    StructuredAnalysis,
)
from presidio_structured.data.data_processors import (
    DataProcessorBase,
    PandasDataProcessor,
)

from src.data_deidentifier.domain.types.language import SupportedLanguage

from .structured_type import StructuredTypeAnalyzer


class DataFrameAnalyzer(StructuredTypeAnalyzer):
    """Analyzer for pandas DataFrame data.

    This class implements analysis for pandas DataFrame objects using
    Presidio's PandasAnalysisBuilder.
    """

    @staticmethod
    @override
    def can_handle(data: Any) -> bool:
        return isinstance(data, pd.DataFrame)

    @override
    def analyze(
        self,
        data: Any,
        language: SupportedLanguage,
    ) -> StructuredAnalysis:
        self.logger.debug("Analyzing DataFrame", {"nb_rows": len(data)})

        analyzer = PandasAnalysisBuilder()
        return analyzer.generate_analysis(
            df=data,
            language=language,
        )

    @override
    def get_data_processor(self) -> DataProcessorBase:
        if self._data_processor is None:
            self._data_processor = PandasDataProcessor()
        return self._data_processor
