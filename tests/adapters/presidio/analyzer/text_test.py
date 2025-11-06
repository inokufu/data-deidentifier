from unittest.mock import Mock, patch

import pytest
from logger import LoggerContract
from presidio_analyzer import RecognizerResult

from src.data_deidentifier.adapters.presidio.analyzer.text import PresidioTextAnalyzer
from src.data_deidentifier.adapters.presidio.engines import PresidioEngineFactory
from src.data_deidentifier.adapters.presidio.exceptions import TextAnalysisError
from src.data_deidentifier.domain.types.language import SupportedLanguage


def create_mock_recognizer_result(
    entity_type: str = "PERSON",
    start: int = 0,
    end: int = 4,
    score: float = 0.95,
) -> Mock:
    """Helper to create mock RecognizerResult."""
    result = Mock(spec=RecognizerResult)
    result.entity_type = entity_type
    result.start = start
    result.end = end
    result.score = score
    return result


class TestPresidioTextAnalyzerInitialization:
    """Test analyzer initialization."""

    @patch.object(PresidioEngineFactory, "get_analyzer_engine")
    def test_init_calls_factory_and_logs_success(
        self,
        mock_get_analyzer_engine: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should call factory and log initialization."""
        # Arrange
        mock_analyzer = Mock()
        mock_get_analyzer_engine.return_value = mock_analyzer

        # Act
        analyzer = PresidioTextAnalyzer(logger=mock_logger)

        # Assert
        assert analyzer.logger == mock_logger
        mock_get_analyzer_engine.assert_called_once()


class TestPresidioTextAnalyzerAnalyze:
    """Test analyze method."""

    @patch.object(PresidioEngineFactory, "get_analyzer_engine")
    def test_analyze_success_with_all_parameters(
        self,
        mock_analyzer_engine: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should successfully analyze text with all parameters."""
        # Arrange
        text = "John works at ACME Corp"
        language = SupportedLanguage.ENGLISH
        min_score = 0.8
        entity_types = ["PERSON", "ORG"]

        mock_results = [
            create_mock_recognizer_result("PERSON", 0, 4, 0.95),
            create_mock_recognizer_result("ORG", 14, 23, 0.88),
        ]

        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = mock_results
        mock_analyzer_engine.return_value = mock_analyzer

        analyzer = PresidioTextAnalyzer(logger=mock_logger)

        # Act
        result = analyzer.analyze(
            text=text,
            language=language,
            min_score=min_score,
            entity_types=entity_types,
        )

        # Assert
        assert result == mock_results
        mock_analyzer.analyze.assert_called_once_with(
            text=text,
            language=language.lower(),
            score_threshold=min_score,
            entities=entity_types,
        )

    @patch.object(PresidioEngineFactory, "get_analyzer_engine")
    def test_analyze_success_with_minimal_parameters(
        self,
        mock_analyzer_engine: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should analyze text with minimal parameters (no entity types)."""
        # Arrange
        text = "Simple text"
        language = SupportedLanguage.ENGLISH
        min_score = 0.5

        mock_results = []
        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = mock_results
        mock_analyzer_engine.return_value = mock_analyzer

        analyzer = PresidioTextAnalyzer(logger=mock_logger)

        # Act
        result = analyzer.analyze(
            text=text,
            language=language,
            min_score=min_score,
            entity_types=None,
        )

        # Assert
        assert result == mock_results
        mock_analyzer.analyze.assert_called_once_with(
            text=text,
            language=language.lower(),
            score_threshold=min_score,
            entities=None,
        )

    @patch.object(PresidioEngineFactory, "get_analyzer_engine")
    def test_analyze_with_empty_text(
        self,
        mock_analyzer_engine: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle empty text gracefully."""
        # Arrange
        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = []
        mock_analyzer_engine.return_value = mock_analyzer

        analyzer = PresidioTextAnalyzer(logger=mock_logger)

        # Act
        result = analyzer.analyze(
            text="",
            language=SupportedLanguage.ENGLISH,
            min_score=0.5,
        )

        # Assert
        assert result == []
        mock_analyzer.analyze.assert_called_once()

    @patch.object(PresidioEngineFactory, "get_analyzer_engine")
    def test_analyze_with_no_entities_found(
        self,
        mock_analyzer_engine: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle text with no PII entities detected."""
        # Arrange
        text = "This is clean text with no PII"
        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = []
        mock_analyzer_engine.return_value = mock_analyzer

        analyzer = PresidioTextAnalyzer(logger=mock_logger)

        # Act
        result = analyzer.analyze(
            text=text,
            language=SupportedLanguage.ENGLISH,
            min_score=0.8,
        )

        # Assert
        assert result == []


class TestPresidioTextAnalyzerErrorHandling:
    """Test error handling scenarios."""

    @patch.object(PresidioEngineFactory, "get_analyzer_engine")
    def test_analyze_when_presidio_raises_exception(
        self,
        mock_analyzer_engine: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should raise TextAnalysisError when presidio analyzer fails."""
        # Arrange
        text = "John works here"
        presidio_error = RuntimeError("Presidio analysis failed")

        mock_analyzer = Mock()
        mock_analyzer.analyze.side_effect = presidio_error
        mock_analyzer_engine.return_value = mock_analyzer

        analyzer = PresidioTextAnalyzer(logger=mock_logger)

        # Act & Assert
        with pytest.raises(
            TextAnalysisError,
            match="Unexpected error during entity recognition",
        ):
            analyzer.analyze(
                text=text,
                language=SupportedLanguage.ENGLISH,
                min_score=0.5,
            )

    @patch.object(PresidioEngineFactory, "get_analyzer_engine")
    def test_analyze_error_preserves_original_exception(
        self,
        mock_analyzer_engine: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should chain original exception in TextAnalysisError."""
        # Arrange
        original_error = ValueError("Invalid input")
        mock_analyzer = Mock()
        mock_analyzer.analyze.side_effect = original_error
        mock_analyzer_engine.return_value = mock_analyzer

        analyzer = PresidioTextAnalyzer(logger=mock_logger)

        # Act & Assert
        with pytest.raises(TextAnalysisError) as exc_info:
            analyzer.analyze(
                text="text",
                language=SupportedLanguage.ENGLISH,
                min_score=0.5,
            )

        assert exc_info.value.__cause__ is original_error


class TestPresidioTextAnalyzerEdgeCases:
    """Test edge cases and boundary conditions."""

    @patch.object(PresidioEngineFactory, "get_analyzer_engine")
    def test_analyze_with_unicode_text(
        self,
        mock_analyzer_engine: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle Unicode characters in text."""
        # Arrange
        unicode_text = "José lives in 北京 🌍"
        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = []
        mock_analyzer_engine.return_value = mock_analyzer

        analyzer = PresidioTextAnalyzer(logger=mock_logger)

        # Act
        result = analyzer.analyze(
            text=unicode_text,
            language=SupportedLanguage.ENGLISH,
            min_score=0.5,
        )

        # Assert
        assert result == []
        mock_analyzer.analyze.assert_called_once_with(
            text=unicode_text,
            language="en",
            score_threshold=0.5,
            entities=None,
        )

    @patch.object(PresidioEngineFactory, "get_analyzer_engine")
    def test_analyze_with_very_long_text(
        self,
        mock_analyzer_engine: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle very long text."""
        # Arrange
        long_text = "John " * 10000  # Very long text
        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = []
        mock_analyzer_engine.return_value = mock_analyzer

        analyzer = PresidioTextAnalyzer(logger=mock_logger)

        # Act
        result = analyzer.analyze(
            text=long_text,
            language=SupportedLanguage.ENGLISH,
            min_score=0.5,
        )

        # Assert
        assert result == []

    @patch.object(PresidioEngineFactory, "get_analyzer_engine")
    def test_analyze_with_zero_min_score(
        self,
        mock_analyzer_engine: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle zero minimum score."""
        # Arrange
        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = []
        mock_analyzer_engine.return_value = mock_analyzer

        analyzer = PresidioTextAnalyzer(logger=mock_logger)

        # Act
        analyzer.analyze(
            text="Test text",
            language=SupportedLanguage.ENGLISH,
            min_score=0.0,
        )

        # Assert
        call_args = mock_analyzer.analyze.call_args
        assert call_args.kwargs["score_threshold"] == 0.0

    @patch.object(PresidioEngineFactory, "get_analyzer_engine")
    def test_analyze_with_empty_entity_types_list(
        self,
        mock_analyzer_engine: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle empty entity types list."""
        # Arrange
        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = []
        mock_analyzer_engine.return_value = mock_analyzer

        analyzer = PresidioTextAnalyzer(logger=mock_logger)

        # Act
        analyzer.analyze(
            text="Test text",
            language=SupportedLanguage.ENGLISH,
            min_score=0.5,
            entity_types=[],
        )

        # Assert
        call_args = mock_analyzer.analyze.call_args
        assert call_args.kwargs["entities"] == []
