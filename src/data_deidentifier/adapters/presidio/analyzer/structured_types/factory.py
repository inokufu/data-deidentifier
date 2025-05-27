from logger import LoggerContract

from src.data_deidentifier.domain.exceptions import UnsupportedStructuredDataError
from src.data_deidentifier.domain.types.structured_data import StructuredData

from .dataframe import DataFrameAnalyzer
from .json_type import JsonAnalyzer
from .structured_type import StructuredTypeAnalyzer


class StructuredDataAnalyzerFactory:
    """Factory for creating appropriate structured data analyzers.

    This factory maintains a registry of analyzers for different data types
    and provides a mechanism to get the appropriate analyzer for a given data.

    Attributes:
        logger: Logger instance for logging messages.
        analyzers: List of registered analyzer instances.
    """

    def __init__(self, logger: LoggerContract) -> None:
        """Initialize the factory with default analyzers.

        Args:
            logger: Logger instance for logging events.
        """
        self.logger = logger
        self.analyzers: list[StructuredTypeAnalyzer] = [
            JsonAnalyzer(self.logger),
            DataFrameAnalyzer(self.logger),
        ]

    def register_analyzer(self, analyzer: StructuredTypeAnalyzer) -> None:
        """Register a new analyzer.

        Args:
            analyzer: The analyzer instance to register.
        """
        self.analyzers.append(analyzer)
        self.logger.debug(
            "Registered analyzer",
            {"analyzer": analyzer.__class__.__name__},
        )

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
        for analyzer in self.analyzers:
            if analyzer.can_handle(data):
                return analyzer

        # If we get here, no analyzer could handle the data
        raise UnsupportedStructuredDataError(
            f"Unsupported data type: {type(data).__name__}",
        )
