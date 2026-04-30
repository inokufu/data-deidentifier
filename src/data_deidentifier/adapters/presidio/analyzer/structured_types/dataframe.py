from typing import cast, override

import pandas as pd
from presidio_structured import (
    PandasAnalysisBuilder,
    StructuredAnalysis,
)
from presidio_structured.data.data_processors import (
    DataProcessorBase,
    PandasDataProcessor,
)

from data_deidentifier.domain.types.language import SupportedLanguage
from data_deidentifier.domain.types.structured_data import StructuredData

from .structured_type import StructuredTypeAnalyzer


class DataFrameAnalyzer(StructuredTypeAnalyzer):
    """Analyzer for pandas DataFrame data.

    This class implements analysis for pandas DataFrame objects using
    Presidio's PandasAnalysisBuilder.
    """

    @override
    def can_handle(self, data: StructuredData) -> bool:
        return isinstance(data, pd.DataFrame)

    @override
    def analyze(
        self,
        data: StructuredData,
        language: SupportedLanguage,
        min_score: float = 0.0,
    ) -> StructuredAnalysis:
        # PandasAnalysisBuilder.generate_analysis() doesn't expose score_threshold.
        self.logger.debug("Analyzing DataFrame", {"nb_rows": len(data)})

        analyzer = PandasAnalysisBuilder(analyzer=self.analyzer_engine)
        return analyzer.generate_analysis(
            df=cast(pd.DataFrame, data),  # can_handle() guarantees data is a DataFrame
            language=language.value.lower(),
        )

    @override
    def get_data_processor(self) -> DataProcessorBase:
        return PandasDataProcessor()
