from unittest.mock import Mock, patch

import pytest
from logger import LoggerContract
from presidio_structured import JsonAnalysisBuilder, StructuredAnalysis
from presidio_structured.data.data_processors import JsonDataProcessor

from src.data_deidentifier.adapters.presidio.analyzer.structured_types.JSON import (
    JsonAnalyzer,
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


class TestJsonAnalyzerCanHandle:
    """Test can_handle method."""

    @pytest.mark.parametrize(
        "data",
        [
            {"name": "John", "email": "john@email.com"},  # Normal dict
            {},  # Empty dict
            {  # Nested dict
                "user": {
                    "profile": {"name": "John", "age": 30},
                    "settings": {"theme": "dark"},
                },
            },
        ],
    )
    def test_can_handle_returns_true_for_dict_data(
        self,
        data: dict,
    ) -> None:
        """Should return True for dictionary data (normal, empty, nested)."""
        # Act
        result = JsonAnalyzer.can_handle(data)

        # Assert
        assert result is True

    @pytest.mark.parametrize(
        "invalid_data",
        [
            "string",
            123,
            ["list", "data"],
            None,
            True,
            object(),
        ],
    )
    def test_can_handle_returns_false_for_non_dict_data(
        self,
        invalid_data: any,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return False for non-dictionary data types."""
        # Arrange
        analyzer = JsonAnalyzer(logger=mock_logger)

        # Act
        result = analyzer.can_handle(invalid_data)

        # Assert
        assert result is False


@patch.object(JsonAnalysisBuilder, "__new__")
class TestJsonAnalyzerAnalyze:
    """Test analyze method."""

    @pytest.mark.parametrize(
        ("data", "expected_keys", "description"),
        [
            ({"name": "John Doe", "email": "john@email.com"}, 2, "normal data"),
            ({}, 0, "empty data"),
            (
                {  # nested data
                    "user": {
                        "profile": {
                            "name": "Jane Smith",
                            "contact": {
                                "email": "jane@email.com",
                                "phone": "+1234567890",
                            },
                        },
                        "settings": {"theme": "light"},
                    },
                },
                1,
                "nested data",
            ),
        ],
    )
    def test_analyze_success_with_various_data_types(
        self,
        mock_builder_class: Mock,
        data: dict,
        expected_keys: int,
        description: str,
        mock_logger: LoggerContract,
    ) -> None:
        """Should successfully analyze JSON data."""
        # Arrange
        language = SupportedLanguage.ENGLISH
        mock_analysis = create_mock_structured_analysis()

        mock_builder_class.return_value.generate_analysis.return_value = mock_analysis

        analyzer = JsonAnalyzer(logger=mock_logger)

        # Act
        result = analyzer.analyze(data=data, language=language)

        # Assert
        assert result == mock_analysis
        mock_builder_class.assert_called_once()
        mock_builder_class.return_value.generate_analysis.assert_called_once_with(
            data=data,
            language=language,
        )

    def test_analyze_when_presidio_builder_raises_exception(
        self,
        mock_builder_class: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should propagate exception when JsonAnalysisBuilder fails."""
        # Arrange
        data = {"name": "John"}
        language = SupportedLanguage.ENGLISH
        presidio_error = RuntimeError("Presidio JSON analysis failed")

        mock_builder_class.return_value.generate_analysis.side_effect = presidio_error

        analyzer = JsonAnalyzer(logger=mock_logger)

        # Act & Assert
        with pytest.raises(RuntimeError, match="Presidio JSON analysis failed"):
            analyzer.analyze(data=data, language=language)


class TestJsonAnalyzerGetDataProcessor:
    """Test get_data_processor method."""

    def test_get_data_processor_returns_json_processor(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return JsonDataProcessor instance."""
        # Arrange
        analyzer = JsonAnalyzer(logger=mock_logger)

        # Act
        result = analyzer.get_data_processor()

        # Assert
        assert isinstance(result, JsonDataProcessor)

    def test_get_data_processor_returns_same_instance(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return same JsonDataProcessor instance on multiple calls."""
        # Arrange
        analyzer = JsonAnalyzer(logger=mock_logger)

        # Act
        result1 = analyzer.get_data_processor()
        result2 = analyzer.get_data_processor()

        # Assert
        assert isinstance(result1, JsonDataProcessor)
        assert result1 is result2  # Same instance (cached)


@patch.object(JsonAnalysisBuilder, "__new__")
class TestJsonAnalyzerEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_analyze_with_very_large_data(
        self,
        mock_builder_class: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle very large JSON data."""
        # Arrange
        large_data = {f"key_{i}": f"value_{i}" for i in range(1000)}
        language = SupportedLanguage.ENGLISH
        mock_analysis = create_mock_structured_analysis()

        mock_builder_class.return_value.generate_analysis.return_value = mock_analysis

        analyzer = JsonAnalyzer(logger=mock_logger)

        # Act
        result = analyzer.analyze(data=large_data, language=language)

        # Assert
        assert result == mock_analysis

    def test_analyze_with_unicode_data(
        self,
        mock_builder_class: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle Unicode characters in JSON data."""
        # Arrange
        data = {
            "名前": "田中太郎",  # Japanese name
            "email": "tanaka@email.com",
            "description": "User with émojis 🎭🌍",
        }
        language = SupportedLanguage.ENGLISH
        mock_analysis = create_mock_structured_analysis()

        mock_builder_class.return_value.generate_analysis.return_value = mock_analysis

        analyzer = JsonAnalyzer(logger=mock_logger)

        # Act
        result = analyzer.analyze(data=data, language=language)

        # Assert
        assert result == mock_analysis
        mock_builder_class.return_value.generate_analysis.assert_called_once_with(
            data=data,
            language=language,
        )

    def test_analyze_with_mixed_data_types(
        self,
        mock_builder_class: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle JSON with mixed data types."""
        # Arrange
        data = {
            "string_field": "John Doe",
            "number_field": 42,
            "boolean_field": True,
            "null_field": None,
            "array_field": ["item1", "item2"],
            "nested_object": {"inner": "value"},
        }
        language = SupportedLanguage.ENGLISH
        mock_analysis = create_mock_structured_analysis()

        mock_builder_class.return_value.generate_analysis.return_value = mock_analysis

        analyzer = JsonAnalyzer(logger=mock_logger)

        # Act
        result = analyzer.analyze(data=data, language=language)

        # Assert
        assert result == mock_analysis
        mock_builder_class.return_value.generate_analysis.assert_called_once_with(
            data=data,
            language=language,
        )
