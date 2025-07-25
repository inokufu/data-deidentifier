from typing import ClassVar

from logger import LoggerContract

from src.data_deidentifier.domain.exceptions import UnsupportedStructuredDataError
from src.data_deidentifier.domain.types.structured_data import StructuredData

from .dataframe import DataFrameAnalyzer
from .JSON import JsonAnalyzer
from .structured_type import StructuredTypeAnalyzer


class StructuredDataAnalyzerFactory:
    """Factory for creating appropriate structured data analyzers.

    This factory maintains a registry of analyzers for different data types
    and provides a mechanism to get the appropriate analyzer for a given data.

    Attributes:
        logger: Logger instance for logging messages.
        _analyzer_cache: List of registered analyzer instances cached.
    """

    _ANALYZER_CLASSES: ClassVar[list[type[StructuredTypeAnalyzer]]] = [
        JsonAnalyzer,
        DataFrameAnalyzer,
    ]

    def __init__(self, logger: LoggerContract) -> None:
        """Initialize the analyzer factory.

        Args:
            logger: Logger instance for logging events.
        """
        self.logger = logger
        self._analyzer_cache: dict[type, StructuredTypeAnalyzer] = {}

    def get_analyzer(self, data: StructuredData) -> StructuredTypeAnalyzer:
        """Get the appropriate analyzer for the data type.

        This method iterates through registered analyzers and returns
        the first one that can handle the given data type.

        Args:
            data: The data to find an analyzer for.

        Returns:
            An appropriate analyzer instance for the data.

        Raises:
            UnsupportedStructuredDataError:
                If no registered analyzer can handle the data type.
        """
        for analyzer_class in self._ANALYZER_CLASSES:
            if analyzer_class.can_handle(data):
                if analyzer_class not in self._analyzer_cache:
                    self._analyzer_cache[analyzer_class] = analyzer_class(
                        logger=self.logger,
                    )
                return self._analyzer_cache[analyzer_class]

        # If we get here, no analyzer could handle the data
        raise UnsupportedStructuredDataError(
            f"Unsupported data type: {type(data).__name__}",
        )
