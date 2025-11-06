import pandas as pd
import pytest
from logger import LoggerContract

from src.data_deidentifier.adapters.presidio.analyzer.structured_types.dataframe import (  # noqa: E501
    DataFrameAnalyzer,
)
from src.data_deidentifier.adapters.presidio.analyzer.structured_types.factory import (
    StructuredDataAnalyzerFactory,
)
from src.data_deidentifier.adapters.presidio.analyzer.structured_types.JSON import (
    JsonAnalyzer,
)
from src.data_deidentifier.domain.exceptions import UnsupportedStructuredDataError


class TestStructuredDataAnalyzerFactorySuccess:
    """Test successful analyzer retrieval scenarios."""

    def test_get_analyzer_for_json_data(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return JsonAnalyzer for dictionary data."""
        # Arrange
        factory = StructuredDataAnalyzerFactory(logger=mock_logger)
        json_data = {"name": "John", "email": "john@email.com"}

        # Act
        analyzer = factory.get_analyzer(data=json_data)

        # Assert
        assert isinstance(analyzer, JsonAnalyzer)
        assert analyzer.logger == mock_logger

    def test_get_analyzer_for_dataframe_data(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return DataFrameAnalyzer for pandas DataFrame."""
        # Arrange
        factory = StructuredDataAnalyzerFactory(logger=mock_logger)
        df_data = pd.DataFrame({"name": ["John"], "email": ["john@email.com"]})

        # Act
        analyzer = factory.get_analyzer(data=df_data)

        # Assert
        assert isinstance(analyzer, DataFrameAnalyzer)
        assert analyzer.logger == mock_logger

    def test_get_analyzer_with_nested_json_data(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return JsonAnalyzer for nested dictionary data."""
        # Arrange
        factory = StructuredDataAnalyzerFactory(logger=mock_logger)
        nested_data = {
            "user": {
                "profile": {"name": "John", "email": "john@email.com"},
                "settings": {"theme": "dark"},
            },
        }

        # Act
        analyzer = factory.get_analyzer(data=nested_data)

        # Assert
        assert isinstance(analyzer, JsonAnalyzer)


class TestStructuredDataAnalyzerFactoryCaching:
    """Test caching behavior."""

    def test_get_analyzer_caches_instances_when_enabled(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should cache analyzer instances when caching is enabled."""
        # Arrange
        factory = StructuredDataAnalyzerFactory(logger=mock_logger)
        json_data = {"name": "John"}

        # Act
        analyzer1 = factory.get_analyzer(data=json_data)
        analyzer2 = factory.get_analyzer(data=json_data)

        # Assert
        assert analyzer1 is analyzer2  # Same instance (cached)

    def test_get_analyzer_caches_different_analyzer_types(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should cache different analyzer types separately."""
        # Arrange
        factory = StructuredDataAnalyzerFactory(logger=mock_logger)
        json_data = {"name": "John"}
        df_data = pd.DataFrame({"name": ["John"]})

        # Act
        json_analyzer1 = factory.get_analyzer(data=json_data)
        df_analyzer1 = factory.get_analyzer(data=df_data)
        json_analyzer2 = factory.get_analyzer(data=json_data)
        df_analyzer2 = factory.get_analyzer(data=df_data)

        # Assert
        assert json_analyzer1 is json_analyzer2  # Same JSON analyzer instance
        assert df_analyzer1 is df_analyzer2  # Same DataFrame analyzer instance
        assert json_analyzer1 is not df_analyzer1  # Different analyzer types


class TestStructuredDataAnalyzerFactoryErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.parametrize(
        "unsupported_data",
        [
            "Hello",  # str
            123,  # int
            [1, 2, 3],  # list
            (1, 2, 3),  # tuple
            {1, 2, 3},  # set
            None,  # None
        ],
    )
    def test_get_analyzer_various_unsupported_types_raise_error(
        self,
        mock_logger: LoggerContract,
        unsupported_data: str | int | dict | tuple | list | None,
    ) -> None:
        """Should raise UnsupportedStructuredDataError for various unsupported types."""
        # Arrange
        factory = StructuredDataAnalyzerFactory(logger=mock_logger)

        # Act & Assert
        with pytest.raises(UnsupportedStructuredDataError):
            factory.get_analyzer(data=unsupported_data)


class TestStructuredDataAnalyzerFactoryEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_get_analyzer_with_empty_dict(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle empty dictionary data."""
        # Arrange
        factory = StructuredDataAnalyzerFactory(logger=mock_logger)
        empty_dict = {}

        # Act
        analyzer = factory.get_analyzer(data=empty_dict)

        # Assert
        assert isinstance(analyzer, JsonAnalyzer)

    def test_get_analyzer_with_empty_dataframe(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle empty DataFrame data."""
        # Arrange
        factory = StructuredDataAnalyzerFactory(logger=mock_logger)
        empty_df = pd.DataFrame()

        # Act
        analyzer = factory.get_analyzer(data=empty_df)

        # Assert
        assert isinstance(analyzer, DataFrameAnalyzer)

    def test_get_analyzer_with_complex_nested_structure(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle complex nested data structures."""
        # Arrange
        factory = StructuredDataAnalyzerFactory(logger=mock_logger)
        complex_data = {
            "users": [
                {
                    "id": 1,
                    "profile": {
                        "name": "John Doe",
                        "contacts": {
                            "email": "john@email.com",
                            "phones": ["+33123456789", "+33987654321"],
                        },
                    },
                    "preferences": {"theme": "dark", "notifications": True},
                },
            ],
            "metadata": {"version": "1.0", "created_at": "2024-01-01"},
        }

        # Act
        analyzer = factory.get_analyzer(data=complex_data)

        # Assert
        assert isinstance(analyzer, JsonAnalyzer)

    def test_cache_behavior_with_multiple_data_instances_same_type(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should cache based on analyzer type, not data instance."""
        # Arrange
        factory = StructuredDataAnalyzerFactory(logger=mock_logger)
        data1 = {"name": "John"}
        data2 = {"email": "jane@email.com"}

        # Act
        analyzer1 = factory.get_analyzer(data=data1)
        analyzer2 = factory.get_analyzer(data=data2)

        # Assert
        assert analyzer1 is analyzer2  # Same analyzer instance for same type
