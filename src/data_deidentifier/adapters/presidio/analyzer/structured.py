from logger import LoggerContract
from presidio_structured import StructuredAnalysis
from presidio_structured.data.data_processors import DataProcessorBase

from src.data_deidentifier.adapters.presidio.engines import PresidioEngineFactory
from src.data_deidentifier.adapters.presidio.exceptions import (
    StructuredDataAnalysisError,
)
from src.data_deidentifier.domain.types.language import SupportedLanguage
from src.data_deidentifier.domain.types.structured_data import StructuredData


class PresidioStructuredDataAnalyzer:
    """Implementation of the structured analyzer contract using Presidio-structured.

    This class uses the Presidio Analyzer to detect PII entities in structured data.
    """

    def __init__(self, logger: LoggerContract) -> None:
        """Initialize the Presidio-structured analyzer.

        Args:
            logger: Logger for logging events
        """
        self.logger = logger

        self.analyzer_factory = (
            PresidioEngineFactory.get_structured_data_analyzer_factory(
                logger=self.logger,
            )
        )

        self.logger.debug("Presidio Structured Analyzer initialized successfully")

    def analyze(
        self,
        data: StructuredData,
        language: SupportedLanguage,
        entity_types: list[str] | None = None,
    ) -> tuple[StructuredAnalysis, DataProcessorBase]:
        """Analyze structured data to detect PII entities.

        Args:
            data: Structured data to analyze
            language: Language code of the text
            entity_types: Types of entities to detect (None means all supported types)

        Returns:
            StructuredAnalysis: List of detected fields
            DataProcessorBase: DataProcessor instance for this analyzer's data type

        Raises:
            StructuredDataAnalysisError: If analysis fails
        """
        analyzer = self.analyzer_factory.get_analyzer(data=data)

        logger_context = {
            "analyzer": type(analyzer).__name__,
            "language": language,
            "entity_types": entity_types,
        }
        self.logger.debug("Starting structured data analysis", logger_context)

        try:
            # Use the analyzer to process the data
            presidio_results = analyzer.analyze(
                data=data,
                language=language,
            )
        except Exception as e:
            msg = "Unexpected error during structured data analysis"
            self.logger.exception(msg, e, logger_context)
            raise StructuredDataAnalysisError(msg) from e

        # Filter by entity types if specified
        if entity_types:
            presidio_results.entity_mapping = {
                field_name: entity_type
                for field_name, entity_type in presidio_results.entity_mapping.items()
                if entity_type in entity_types
            }

        self.logger.info(
            "Structured analysis completed successfully",
            {"fields_mapped": len(presidio_results.entity_mapping), **logger_context},
        )

        return presidio_results, analyzer.get_data_processor()
