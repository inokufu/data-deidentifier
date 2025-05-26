from abc import ABC, abstractmethod

from logger import LoggerContract
from presidio_structured import StructuredAnalysis
from presidio_structured.data.data_processors import DataProcessorBase

from src.data_deidentifier.domain.types.structured_data import StructuredData


class StructuredTypeAnalyzer(ABC):
    """Base abstract class for structured data analyzers.

    Defines the interface that all data type-specific analyzers must implement.
    It provides mechanisms to determine if analyzer can handle
    a particular data type and to perform PII entity analysis on that data.
    """

    def __init__(self, logger: LoggerContract) -> None:
        """Initialize the structured type analyzer.

        Args:
            logger: Logger instance for logging events.
        """
        self.logger = logger

    @abstractmethod
    def can_handle(self, data: StructuredData) -> bool:
        """Check if this analyzer can handle the provided data type.

        Args:
            data: The data to check.

        Returns:
            True if this analyzer can handle this data type, False otherwise.
        """
        raise NotImplementedError

    @abstractmethod
    def analyze(self, data: StructuredData, language: str) -> StructuredAnalysis:
        """Analyze structured data to detect PII entities.

        Args:
            data: The structured data to analyze.
            language: Language code of the data content.

        Returns:
            StructuredAnalysis object containing the analysis results.

        Raises:
            ValueError: If the data cannot be properly analyzed.
        """
        raise NotImplementedError

    @abstractmethod
    def get_data_processor(self) -> DataProcessorBase:
        """Get the appropriate DataProcessor for this data type.

        Returns:
            DataProcessor instance for this analyzer's data type.
        """
        raise NotImplementedError
