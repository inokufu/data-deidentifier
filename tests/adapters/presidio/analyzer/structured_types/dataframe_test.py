from unittest.mock import Mock, patch

import pandas as pd
import pytest
from logger import LoggerContract
from presidio_structured import PandasAnalysisBuilder, StructuredAnalysis
from presidio_structured.data.data_processors import PandasDataProcessor

from src.data_deidentifier.adapters.presidio.analyzer.structured_types.dataframe import (  # noqa: E501
    DataFrameAnalyzer,
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


class TestDataFrameAnalyzerCanHandle:
    """Test can_handle method."""

    @pytest.mark.parametrize(
        "data",
        [
            pd.DataFrame(
                {"name": ["John"], "email": ["john@email.com"]},
            ),  # Normal DataFrame
            pd.DataFrame(),  # Empty DataFrame
            pd.DataFrame(
                {  # DataFrame with multiple columns and rows
                    "name": ["John", "Jane", "Bob"],
                    "email": ["john@email.com", "jane@email.com", "bob@email.com"],
                    "age": [25, 30, 35],
                },
            ),
            pd.DataFrame({"mixed": [1, "text", 3.14, True, None]}),  # Mixed types
        ],
    )
    def test_can_handle_returns_true_for_dataframe_data(
        self,
        data: pd.DataFrame,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return True for pandas DataFrame data (normal, empty, mixed types)."""
        # Act
        result = DataFrameAnalyzer.can_handle(data)

        # Assert
        assert result is True

    @pytest.mark.parametrize(
        "invalid_data",
        [
            {"name": "John"},  # Dict
            "string",  # String
            123,  # Integer
            ["list", "data"],  # List
            None,  # None
            True,  # Boolean
            object(),  # Generic object
        ],
    )
    def test_can_handle_returns_false_for_non_dataframe_data(
        self,
        invalid_data: object,
    ) -> None:
        """Should return False for non-DataFrame data types."""
        # Act
        result = DataFrameAnalyzer.can_handle(invalid_data)

        # Assert
        assert result is False


@patch.object(PandasAnalysisBuilder, "__new__")
class TestDataFrameAnalyzerAnalyze:
    """Test analyze method."""

    @pytest.mark.parametrize(
        ("data", "expected_rows", "description"),
        [
            (
                pd.DataFrame({"name": ["John Doe"], "email": ["john@email.com"]}),
                1,
                "single row data",
            ),
            (pd.DataFrame(), 0, "empty data"),
            (
                pd.DataFrame(
                    {
                        "name": ["Jane Smith", "Bob Johnson", "Alice Brown"],
                        "email": ["jane@email.com", "bob@email.com", "alice@email.com"],
                        "phone": ["+1234567890", "+0987654321", "+1122334455"],
                    },
                ),
                3,
                "multiple rows data",
            ),
        ],
    )
    def test_analyze_success_with_various_data_types(
        self,
        mock_builder_class: Mock,
        data: pd.DataFrame,
        expected_rows: int,
        description: str,
        mock_logger: LoggerContract,
    ) -> None:
        """Should successfully analyze DataFrame data."""
        # Arrange
        language = SupportedLanguage.ENGLISH
        mock_analysis = create_mock_structured_analysis()

        mock_builder_class.return_value.generate_analysis.return_value = mock_analysis

        analyzer = DataFrameAnalyzer(logger=mock_logger)

        # Act
        result = analyzer.analyze(data=data, language=language)

        # Assert
        assert result == mock_analysis
        mock_builder_class.assert_called_once()
        mock_builder_class.return_value.generate_analysis.assert_called_once_with(
            df=data,
            language=language,
        )

    def test_analyze_when_presidio_builder_raises_exception(
        self,
        mock_builder_class: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should propagate exception when PandasAnalysisBuilder fails."""
        # Arrange
        data = pd.DataFrame({"name": ["John"]})
        language = SupportedLanguage.ENGLISH
        presidio_error = RuntimeError("Presidio DataFrame analysis failed")

        mock_builder_class.return_value.generate_analysis.side_effect = presidio_error

        analyzer = DataFrameAnalyzer(logger=mock_logger)

        # Act & Assert
        with pytest.raises(RuntimeError, match="Presidio DataFrame analysis failed"):
            analyzer.analyze(data=data, language=language)


class TestDataFrameAnalyzerGetDataProcessor:
    """Test get_data_processor method."""

    def test_get_data_processor_returns_pandas_processor(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return PandasDataProcessor instance."""
        # Arrange
        analyzer = DataFrameAnalyzer(logger=mock_logger)

        # Act
        result = analyzer.get_data_processor()

        # Assert
        assert isinstance(result, PandasDataProcessor)

    def test_get_data_processor_creates_new_instances(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return same PandasDataProcessor instance on multiple calls."""
        # Arrange
        analyzer = DataFrameAnalyzer(logger=mock_logger)

        # Act
        result1 = analyzer.get_data_processor()
        result2 = analyzer.get_data_processor()

        # Assert
        assert isinstance(result1, PandasDataProcessor)
        assert isinstance(result2, PandasDataProcessor)
        assert result1 is result2  # Same instance (cached)


@patch.object(PandasAnalysisBuilder, "__new__")
class TestDataFrameAnalyzerEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_analyze_with_very_large_dataframe(
        self,
        mock_builder_class: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle very large DataFrame data."""
        # Arrange
        large_data = pd.DataFrame(
            {
                "name": [f"User_{i}" for i in range(1000)],
                "email": [f"user_{i}@email.com" for i in range(1000)],
                "id": range(1000),
            },
        )
        language = SupportedLanguage.ENGLISH
        mock_analysis = create_mock_structured_analysis()

        mock_builder_class.return_value.generate_analysis.return_value = mock_analysis

        analyzer = DataFrameAnalyzer(logger=mock_logger)

        # Act
        result = analyzer.analyze(data=large_data, language=language)

        # Assert
        assert result == mock_analysis

    def test_analyze_with_unicode_data(
        self,
        mock_builder_class: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle Unicode characters in DataFrame data."""
        # Arrange
        data = pd.DataFrame(
            {
                "名前": ["田中太郎", "佐藤花子"],  # Japanese names
                "email": ["tanaka@email.com", "sato@email.com"],
                "description": ["User with émojis 🎭", "Another user 🌍"],
            },
        )
        language = SupportedLanguage.ENGLISH
        mock_analysis = create_mock_structured_analysis()

        mock_builder_class.return_value.generate_analysis.return_value = mock_analysis

        analyzer = DataFrameAnalyzer(logger=mock_logger)

        # Act
        result = analyzer.analyze(data=data, language=language)

        # Assert
        assert result == mock_analysis
        mock_builder_class.return_value.generate_analysis.assert_called_once_with(
            df=data,
            language=language,
        )

    def test_analyze_with_mixed_data_types(
        self,
        mock_builder_class: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle DataFrame with mixed data types."""
        # Arrange
        data = pd.DataFrame(
            {
                "string_field": ["John Doe", "Jane Smith"],
                "number_field": [42, 33],
                "float_field": [3.14, 2.71],
                "boolean_field": [True, False],
                "age": [25, 30],
                "null_values": [None, None],
                "datetime_field": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            },
        )
        language = SupportedLanguage.ENGLISH
        mock_analysis = create_mock_structured_analysis()

        mock_builder_class.return_value.generate_analysis.return_value = mock_analysis

        analyzer = DataFrameAnalyzer(logger=mock_logger)

        # Act
        result = analyzer.analyze(data=data, language=language)

        # Assert
        assert result == mock_analysis
        mock_builder_class.return_value.generate_analysis.assert_called_once_with(
            df=data,
            language=language,
        )
