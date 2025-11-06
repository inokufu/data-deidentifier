from unittest.mock import Mock, patch

import pytest
from logger import LoggerContract
from presidio_structured import StructuredAnalysis
from presidio_structured.data.data_processors import DataProcessorBase

from src.data_deidentifier.adapters.presidio.analyzer.structured import (
    PresidioStructuredDataAnalyzer,
)
from src.data_deidentifier.adapters.presidio.engines import PresidioEngineFactory
from src.data_deidentifier.adapters.presidio.exceptions import (
    StructuredDataAnalysisError,
)
from src.data_deidentifier.domain.types.language import SupportedLanguage


def create_mock_structured_analysis(
    entity_mapping: dict[str, str] | None = None,
) -> Mock:
    """Helper to create mock StructuredAnalysis."""
    if entity_mapping is None:
        entity_mapping = {"name": "PERSON", "email": "EMAIL_ADDRESS"}

    analysis = Mock(spec=StructuredAnalysis)
    analysis.entity_mapping = entity_mapping
    return analysis


def create_mock_data_processor() -> Mock:
    """Helper to create mock DataProcessorBase."""
    return Mock(spec=DataProcessorBase)


def create_mock_analyzer(analysis: Mock, data_processor: Mock) -> Mock:
    """Helper to create mock analyzer with data processor."""
    mock_analyzer = Mock()
    mock_analyzer.analyze.return_value = analysis
    mock_analyzer.get_data_processor.return_value = data_processor
    return mock_analyzer


class TestPresidioStructuredDataAnalyzerInitialization:
    """Test analyzer initialization."""

    @patch.object(PresidioEngineFactory, "get_structured_data_analyzer_factory")
    def test_init_creates_analyzer_factory(
        self,
        mock_data_factory: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should call factory and log initialization."""
        # Arrange
        mock_factory = Mock()
        mock_data_factory.return_value = mock_factory

        # Act
        analyzer = PresidioStructuredDataAnalyzer(logger=mock_logger)

        # Assert
        assert analyzer.logger == mock_logger
        mock_data_factory.assert_called_once_with(logger=mock_logger)

    @patch.object(PresidioEngineFactory, "get_structured_data_analyzer_factory")
    def test_init_stores_logger(
        self,
        mock_data_factory: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should store logger reference."""
        # Act
        analyzer = PresidioStructuredDataAnalyzer(logger=mock_logger)

        # Assert
        assert analyzer.logger is mock_logger


class TestPresidioStructuredDataAnalyzerAnalyze:
    """Test analyze method."""

    @patch.object(PresidioEngineFactory, "get_structured_data_analyzer_factory")
    def test_analyze_success_with_all_parameters(
        self,
        mock_data_factory: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should successfully analyze structured data with all parameters."""
        # Arrange
        data = {"name": "John Doe", "email": "john@email.com", "age": 30}
        language = SupportedLanguage.ENGLISH
        entity_types = ["PERSON", "EMAIL_ADDRESS"]

        mock_analysis = create_mock_structured_analysis(
            {"name": "PERSON", "email": "EMAIL_ADDRESS"},
        )
        mock_data_processor = create_mock_data_processor()
        mock_analyzer = create_mock_analyzer(mock_analysis, mock_data_processor)

        mock_factory = Mock()
        mock_factory.get_analyzer.return_value = mock_analyzer
        mock_data_factory.return_value = mock_factory

        analyzer = PresidioStructuredDataAnalyzer(logger=mock_logger)

        # Act
        result_analysis, result_processor = analyzer.analyze(
            data=data,
            language=language,
            entity_types=entity_types,
        )

        # Assert
        assert result_analysis == mock_analysis
        assert result_processor == mock_data_processor

        mock_factory.get_analyzer.assert_called_once_with(data=data)
        mock_analyzer.analyze.assert_called_once_with(
            data=data,
            language=language.lower(),
        )

    @patch.object(PresidioEngineFactory, "get_structured_data_analyzer_factory")
    def test_analyze_success_without_entity_types(
        self,
        mock_data_factory: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should analyze structured data without entity type filtering."""
        # Arrange
        data = {"company": "ACME Corp", "location": "New York"}
        language = SupportedLanguage.ENGLISH

        mock_analysis = create_mock_structured_analysis(
            {"company": "ORG", "location": "LOCATION"},
        )
        mock_data_processor = create_mock_data_processor()
        mock_analyzer = create_mock_analyzer(mock_analysis, mock_data_processor)

        mock_factory = Mock()
        mock_factory.get_analyzer.return_value = mock_analyzer
        mock_data_factory.return_value = mock_factory

        analyzer = PresidioStructuredDataAnalyzer(logger=mock_logger)

        # Act
        result_analysis, result_processor = analyzer.analyze(
            data=data,
            language=language,
            entity_types=None,
        )

        # Assert
        assert result_analysis == mock_analysis
        assert result_processor == mock_data_processor
        # Original entity mapping should be unchanged
        assert result_analysis.entity_mapping == {
            "company": "ORG",
            "location": "LOCATION",
        }

    @patch.object(PresidioEngineFactory, "get_structured_data_analyzer_factory")
    def test_analyze_filters_by_entity_types(
        self,
        mock_data_factory: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should filter results by specified entity types."""
        # Arrange
        data = {"name": "John", "email": "john@email.com", "phone": "+1234567890"}
        language = SupportedLanguage.ENGLISH
        entity_types = ["PERSON", "PHONE_NUMBER"]  # Exclude EMAIL_ADDRESS

        # Mock analysis returns all entity types
        mock_analysis = create_mock_structured_analysis(
            {"name": "PERSON", "email": "EMAIL_ADDRESS", "phone": "PHONE_NUMBER"},
        )
        mock_data_processor = create_mock_data_processor()
        mock_analyzer = create_mock_analyzer(mock_analysis, mock_data_processor)

        mock_factory = Mock()
        mock_factory.get_analyzer.return_value = mock_analyzer
        mock_data_factory.return_value = mock_factory

        analyzer = PresidioStructuredDataAnalyzer(logger=mock_logger)

        # Act
        result_analysis, _ = analyzer.analyze(
            data=data,
            language=language,
            entity_types=entity_types,
        )

        # Assert
        # Should filter out EMAIL_ADDRESS, keep only PERSON and PHONE_NUMBER
        expected_filtered = {"name": "PERSON", "phone": "PHONE_NUMBER"}
        assert result_analysis.entity_mapping == expected_filtered

    @patch.object(PresidioEngineFactory, "get_structured_data_analyzer_factory")
    def test_analyze_converts_language_to_lowercase(
        self,
        mock_data_factory: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should convert language to lowercase before calling presidio."""
        # Arrange
        data = {"field": "value"}
        mock_analysis = create_mock_structured_analysis({})
        mock_data_processor = create_mock_data_processor()
        mock_analyzer = create_mock_analyzer(mock_analysis, mock_data_processor)

        mock_factory = Mock()
        mock_factory.get_analyzer.return_value = mock_analyzer
        mock_data_factory.return_value = mock_factory

        analyzer = PresidioStructuredDataAnalyzer(logger=mock_logger)

        # Act
        analyzer.analyze(
            data=data,
            language=SupportedLanguage.ENGLISH,  # "en"
            entity_types=None,
        )

        # Assert
        call_args = mock_analyzer.analyze.call_args
        assert call_args.kwargs["language"] == "en"  # Should be lowercase

    @patch.object(PresidioEngineFactory, "get_structured_data_analyzer_factory")
    def test_analyze_with_empty_data(
        self,
        mock_data_factory: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle empty data gracefully."""
        # Arrange
        data = {}
        mock_analysis = create_mock_structured_analysis({})
        mock_data_processor = create_mock_data_processor()
        mock_analyzer = create_mock_analyzer(mock_analysis, mock_data_processor)

        mock_factory = Mock()
        mock_factory.get_analyzer.return_value = mock_analyzer
        mock_data_factory.return_value = mock_factory

        analyzer = PresidioStructuredDataAnalyzer(logger=mock_logger)

        # Act
        result_analysis, result_processor = analyzer.analyze(
            data=data,
            language=SupportedLanguage.ENGLISH,
        )

        # Assert
        assert result_analysis == mock_analysis
        assert result_processor == mock_data_processor
        mock_analyzer.analyze.assert_called_once_with(data=data, language="en")

    @patch.object(PresidioEngineFactory, "get_structured_data_analyzer_factory")
    def test_analyze_with_no_entities_found(
        self,
        mock_data_factory: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle data with no PII entities detected."""
        # Arrange
        data = {"setting": "theme", "value": "dark"}
        mock_analysis = create_mock_structured_analysis({})  # No entities
        mock_data_processor = create_mock_data_processor()
        mock_analyzer = create_mock_analyzer(mock_analysis, mock_data_processor)

        mock_factory = Mock()
        mock_factory.get_analyzer.return_value = mock_analyzer
        mock_data_factory.return_value = mock_factory

        analyzer = PresidioStructuredDataAnalyzer(logger=mock_logger)

        # Act
        result_analysis, _ = analyzer.analyze(
            data=data,
            language=SupportedLanguage.ENGLISH,
        )

        # Assert
        assert result_analysis.entity_mapping == {}


class TestPresidioStructuredDataAnalyzerErrorHandling:
    """Test error handling scenarios."""

    @patch.object(PresidioEngineFactory, "get_structured_data_analyzer_factory")
    def test_analyze_when_factory_get_analyzer_fails(
        self,
        mock_data_factory: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should let factory errors bubble up (not caught by try/catch)."""
        # Arrange
        data = {"name": "John"}
        factory_error = RuntimeError("Unsupported data type")

        mock_factory = Mock()
        mock_factory.get_analyzer.side_effect = factory_error
        mock_data_factory.return_value = mock_factory

        analyzer = PresidioStructuredDataAnalyzer(logger=mock_logger)

        # Act & Assert
        # Factory errors are NOT caught by the try/catch in the code
        with pytest.raises(RuntimeError, match="Unsupported data type"):
            analyzer.analyze(
                data=data,
                language=SupportedLanguage.ENGLISH,
            )

    @patch.object(PresidioEngineFactory, "get_structured_data_analyzer_factory")
    def test_analyze_when_presidio_analyzer_fails(
        self,
        mock_data_factory: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should raise StructuredDataAnalysisError when presidio analyzer fails."""
        # Arrange
        data = {"name": "John"}
        presidio_error = RuntimeError("Presidio analysis failed")

        mock_analyzer = Mock()
        mock_analyzer.analyze.side_effect = presidio_error

        mock_factory = Mock()
        mock_factory.get_analyzer.return_value = mock_analyzer
        mock_data_factory.return_value = mock_factory

        analyzer = PresidioStructuredDataAnalyzer(logger=mock_logger)

        # Act & Assert
        with pytest.raises(
            StructuredDataAnalysisError,
            match="Unexpected error during structured data analysis",
        ):
            analyzer.analyze(
                data=data,
                language=SupportedLanguage.ENGLISH,
            )

        # Verify error logging
        mock_logger.exception.assert_called_once_with(
            "Unexpected error during structured data analysis",
            presidio_error,
            {
                "analyzer": type(mock_analyzer).__name__,
                "language": "en",
                "entity_types": None,
            },
        )

    @patch.object(PresidioEngineFactory, "get_structured_data_analyzer_factory")
    def test_analyze_error_preserves_original_exception(
        self,
        mock_data_factory: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should chain original exception in StructuredDataAnalysisError."""
        # Arrange
        original_error = ValueError("Invalid structured data")

        mock_analyzer = Mock()
        mock_analyzer.analyze.side_effect = original_error

        mock_factory = Mock()
        mock_factory.get_analyzer.return_value = mock_analyzer
        mock_data_factory.return_value = mock_factory

        analyzer = PresidioStructuredDataAnalyzer(logger=mock_logger)

        # Act & Assert
        with pytest.raises(StructuredDataAnalysisError) as exc_info:
            analyzer.analyze(
                data={"field": "value"},
                language=SupportedLanguage.ENGLISH,
            )

        assert exc_info.value.__cause__ is original_error


class TestPresidioStructuredDataAnalyzerLogging:
    """Test logging behavior."""

    @patch.object(PresidioEngineFactory, "get_structured_data_analyzer_factory")
    def test_analyze_logs_debug_start_message(
        self,
        mock_data_factory: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should log debug message when starting analysis."""
        # Arrange
        data = {"name": "John", "email": "john@email.com"}
        language = SupportedLanguage.ENGLISH
        entity_types = ["PERSON"]

        mock_analysis = create_mock_structured_analysis()
        mock_data_processor = create_mock_data_processor()
        mock_analyzer = create_mock_analyzer(mock_analysis, mock_data_processor)

        mock_factory = Mock()
        mock_factory.get_analyzer.return_value = mock_analyzer
        mock_data_factory.return_value = mock_factory

        analyzer = PresidioStructuredDataAnalyzer(logger=mock_logger)

        # Act
        analyzer.analyze(
            data=data,
            language=language,
            entity_types=entity_types,
        )

        # Assert
        expected_context = {
            "analyzer": type(mock_analyzer).__name__,
            "language": "en",
            "entity_types": entity_types,
        }
        mock_logger.debug.assert_any_call(
            "Starting structured data analysis",
            expected_context,
        )

    @patch.object(PresidioEngineFactory, "get_structured_data_analyzer_factory")
    def test_analyze_logs_info_success_message(
        self,
        mock_data_factory: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should log info message when analysis completes successfully."""
        # Arrange
        data = {"name": "John", "email": "john@email.com"}
        mock_analysis = create_mock_structured_analysis(
            {"name": "PERSON", "email": "EMAIL_ADDRESS"},
        )
        mock_data_processor = create_mock_data_processor()
        mock_analyzer = create_mock_analyzer(mock_analysis, mock_data_processor)

        mock_factory = Mock()
        mock_factory.get_analyzer.return_value = mock_analyzer
        mock_data_factory.return_value = mock_factory

        analyzer = PresidioStructuredDataAnalyzer(logger=mock_logger)

        # Act
        analyzer.analyze(
            data=data,
            language=SupportedLanguage.ENGLISH,
        )

        # Assert
        expected_context = {
            "fields_mapped": 2,  # 2 fields detected
            "analyzer": type(mock_analyzer).__name__,
            "language": "en",
            "entity_types": None,
        }
        mock_logger.info.assert_called_once_with(
            "Structured analysis completed successfully",
            expected_context,
        )

    @patch.object(PresidioEngineFactory, "get_structured_data_analyzer_factory")
    def test_analyze_logs_correct_fields_count(
        self,
        mock_data_factory: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should log correct number of mapped fields."""
        # Arrange
        mock_analysis = create_mock_structured_analysis(
            {
                "name": "PERSON",
                "email": "EMAIL_ADDRESS",
                "phone": "PHONE_NUMBER",
                "address": "LOCATION",
            },
        )
        mock_data_processor = create_mock_data_processor()
        mock_analyzer = create_mock_analyzer(mock_analysis, mock_data_processor)

        mock_factory = Mock()
        mock_factory.get_analyzer.return_value = mock_analyzer
        mock_data_factory.return_value = mock_factory

        analyzer = PresidioStructuredDataAnalyzer(logger=mock_logger)

        # Act
        analyzer.analyze(
            data={"some": "data"},
            language=SupportedLanguage.ENGLISH,
        )

        # Assert
        call_args = mock_logger.info.call_args
        assert call_args.args[1]["fields_mapped"] == 4


class TestPresidioStructuredDataAnalyzerEdgeCases:
    """Test edge cases and boundary conditions."""

    @patch.object(PresidioEngineFactory, "get_structured_data_analyzer_factory")
    def test_analyze_with_nested_data_structure(
        self,
        mock_data_factory: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle nested data structures."""
        # Arrange
        nested_data = {
            "user": {
                "profile": {"name": "John Doe", "email": "john@email.com"},
                "settings": {"theme": "dark"},
            },
        }

        mock_analysis = create_mock_structured_analysis(
            {"user.profile.name": "PERSON", "user.profile.email": "EMAIL_ADDRESS"},
        )
        mock_data_processor = create_mock_data_processor()
        mock_analyzer = create_mock_analyzer(mock_analysis, mock_data_processor)

        mock_factory = Mock()
        mock_factory.get_analyzer.return_value = mock_analyzer
        mock_data_factory.return_value = mock_factory

        analyzer = PresidioStructuredDataAnalyzer(logger=mock_logger)

        # Act
        result_analysis, result_processor = analyzer.analyze(
            data=nested_data,
            language=SupportedLanguage.ENGLISH,
        )

        # Assert
        assert result_analysis == mock_analysis
        assert result_processor == mock_data_processor
        mock_factory.get_analyzer.assert_called_once_with(data=nested_data)

    @patch.object(PresidioEngineFactory, "get_structured_data_analyzer_factory")
    def test_analyze_filters_with_empty_entity_types_list(
        self,
        mock_data_factory: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should treat empty entity types list same as None (no filtering)."""
        # Arrange
        data = {"name": "John"}
        mock_analysis = create_mock_structured_analysis({"name": "PERSON"})
        mock_data_processor = create_mock_data_processor()
        mock_analyzer = create_mock_analyzer(mock_analysis, mock_data_processor)

        mock_factory = Mock()
        mock_factory.get_analyzer.return_value = mock_analyzer
        mock_data_factory.return_value = mock_factory

        analyzer = PresidioStructuredDataAnalyzer(logger=mock_logger)

        # Act
        result_analysis, _ = analyzer.analyze(
            data=data,
            language=SupportedLanguage.ENGLISH,
            entity_types=[],  # Empty list
        )

        # Assert
        # Current code behavior: if entity_types: evaluates to False for [],
        # so no filtering is applied (same as None)
        assert result_analysis.entity_mapping == {"name": "PERSON"}

        call_args = mock_logger.info.call_args
        assert call_args.args[1]["fields_mapped"] == 1

    @patch.object(PresidioEngineFactory, "get_structured_data_analyzer_factory")
    def test_analyze_with_mixed_entity_types_filtering(
        self,
        mock_data_factory: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should correctly filter with mix of included and excluded entity types."""
        # Arrange
        data = {"data": "test"}
        original_mapping = {
            "name": "PERSON",
            "email": "EMAIL_ADDRESS",
            "phone": "PHONE_NUMBER",
            "company": "ORG",
            "city": "LOCATION",
        }
        entity_types = ["PERSON", "LOCATION", "IP_ADDRESS"]  # Include non-existent type

        mock_analysis = create_mock_structured_analysis(original_mapping)
        mock_data_processor = create_mock_data_processor()
        mock_analyzer = create_mock_analyzer(mock_analysis, mock_data_processor)

        mock_factory = Mock()
        mock_factory.get_analyzer.return_value = mock_analyzer
        mock_data_factory.return_value = mock_factory

        analyzer = PresidioStructuredDataAnalyzer(logger=mock_logger)

        # Act
        result_analysis, _ = analyzer.analyze(
            data=data,
            language=SupportedLanguage.ENGLISH,
            entity_types=entity_types,
        )

        # Assert
        # Should only keep PERSON and LOCATION (IP_ADDRESS doesn't exist in original)
        expected_filtered = {"name": "PERSON", "city": "LOCATION"}
        assert result_analysis.entity_mapping == expected_filtered
