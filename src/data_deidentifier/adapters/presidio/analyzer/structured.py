from typing import Any, override

from logger import LoggerContract

from src.data_deidentifier.adapters.presidio.analyzer.structured_types.factory import (
    StructuredDataAnalyzerFactory,
)
from src.data_deidentifier.adapters.presidio.mapper import PresidioStructuredMapper
from src.data_deidentifier.domain.contracts.analyzer.structured import (
    StructuredAnalyzerContract,
)
from src.data_deidentifier.domain.exceptions import AnalysisError
from src.data_deidentifier.domain.types.structured_analysis_result import (
    StructuredAnalysisField,
)


class PresidioStructuredAnalyzer(StructuredAnalyzerContract):
    """Implementation of the structured analyzer contract using Presidio-structured.

    This class uses the Presidio Analyzer to detect PII entities in structured data.
    """

    def __init__(self, logger: LoggerContract) -> None:
        """Initialize the Presidio-structured analyzer.

        Args:
            logger: Logger for logging events
        """
        self.logger = logger
        self.analyzer_factory = StructuredDataAnalyzerFactory(logger)
        self.logger.debug("Presidio Structured Analyzer initialized successfully")

    @override
    def analyze(
        self,
        data: Any,
        language: str,
        entity_types: list[str] | None = None,
    ) -> list[StructuredAnalysisField]:
        language = language.lower()

        logger_context = {
            "data_type": str(type(data)),
            "language": language,
            "entity_types": entity_types,
        }
        self.logger.debug("Starting structured data analysis", logger_context)

        try:
            # Get the appropriate analyzer for this data type
            analyzer = self.analyzer_factory.get_analyzer(data)

            # Use the analyzer to process the data
            presidio_analysis = analyzer.analyze(
                data=data,
                language=language,
            )

        except Exception as e:
            msg = "Unexpected error during structured data analysis"
            self.logger.exception(msg, e, logger_context)
            raise AnalysisError(msg) from e

        # Convert to domain model
        fields = PresidioStructuredMapper.presidio_result_to_domain(
            analysis=presidio_analysis,
        )

        # Filter by entity types if specified
        if entity_types:
            fields = [field for field in fields if field.entity_type in entity_types]

        self.logger.info(
            "Structured analysis completed successfully",
            {"fields_mapped": len(fields), **logger_context},
        )

        return fields
