from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any, override

from presidio_analyzer import RecognizerResult
from presidio_structured import JsonAnalysisBuilder, StructuredAnalysis
from presidio_structured.data.data_processors import (
    DataProcessorBase,
    JsonDataProcessor,
)

from data_deidentifier.domain.types.language import SupportedLanguage

from .structured_type import StructuredTypeAnalyzer


@dataclass
class StructuredAnalysisWithSpans(StructuredAnalysis):
    """StructuredAnalysis extended with per-field spans for text-level anonymization.

    spans_mapping uses tuples of key segments (e.g. ("user", "info", "name")) rather
    than dot-joined strings, to avoid ambiguity when keys contain literal dots
    (e.g. email addresses used as keys).
    """

    spans_mapping: dict[tuple[str, ...], list[RecognizerResult]]


class JsonAnalysisBuilderWithSpans(JsonAnalysisBuilder):
    """Presidio extension that captures all entity spans per field.

    The parent class (JsonAnalysisBuilder) discards span information, keeping
    only the entity type of the first result per field. This subclass preserves
    all RecognizerResult objects so the anonymizer can do text-level replacement
    (e.g. "<PERSON> is kind") instead of full-field replacement.
    """

    @override
    def generate_analysis(
        self,
        data: dict,
        language: str = "en",
    ) -> StructuredAnalysisWithSpans:
        """Analyze a JSON dict and return entity mapping alongside full spans.

        Returns:
            StructuredAnalysisWithSpans where entity_mapping is keyed by
            dot-separated paths (e.g. "actor.0.name") and spans_mapping by
            tuples (e.g. ("actor", "0", "name")).
        """
        dict_analyzer_results = self.batch_analyzer.analyze_dict(
            input_dict=data,
            language=language,
            n_process=self.n_process,
            batch_size=self.batch_size,
        )

        entity_mapping: dict[str, str] = {}
        spans_mapping: dict[tuple[str, ...], list[RecognizerResult]] = {}

        # Iterative traversal of the DictAnalyzerResult tree using a stack.
        # Each entry is (iterator of DictAnalyzerResult, path prefix as tuple).
        stack: list[tuple[Iterator, tuple[str, ...]]] = [(dict_analyzer_results, ())]
        while stack:
            results, path = stack.pop()
            for result in results:
                current_path = (*path, result.key)
                if isinstance(result.value, dict):
                    stack.append((result.recognizer_results, current_path))
                else:
                    spans = list(result.recognizer_results)
                    if spans and isinstance(spans[0], RecognizerResult):
                        entity_mapping[".".join(current_path)] = spans[0].entity_type
                        spans_mapping[current_path] = spans

        return StructuredAnalysisWithSpans(
            entity_mapping=entity_mapping,
            spans_mapping=spans_mapping,
        )


class JsonAnalyzer(StructuredTypeAnalyzer):
    """Analyzer for JSON data.

    This class implements analysis for JSON-formatted data (Python dictionaries)
    using JsonAnalysisBuilderWithSpans, a Presidio extension
    that captures full span information.
    """

    @override
    def can_handle(self, data: Any) -> bool:
        return isinstance(data, dict)

    @override
    def analyze(
        self,
        data: Any,
        language: SupportedLanguage,
    ) -> StructuredAnalysisWithSpans:
        self.logger.debug("Analyzing JSON data", {"nb_keys": len(data)})

        analyzer = JsonAnalysisBuilderWithSpans(analyzer=self.analyzer_engine)
        return analyzer.generate_analysis(
            data=data,
            language=language.value.lower(),
        )

    @override
    def get_data_processor(self) -> DataProcessorBase:
        return JsonDataProcessor()
