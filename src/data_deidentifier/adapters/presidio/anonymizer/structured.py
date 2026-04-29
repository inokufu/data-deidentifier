from typing import Any, override

from logger import LoggerContract

from data_deidentifier.adapters.presidio.analyzer.structured import (
    PresidioStructuredDataAnalyzer,
)
from data_deidentifier.adapters.presidio.engines import PresidioEngineFactory
from data_deidentifier.adapters.presidio.exceptions import (
    StructuredDataAnalysisError,
)
from data_deidentifier.adapters.presidio.json_utils import flatten, unflatten
from data_deidentifier.adapters.presidio.mapper import PresidioStructuredDataMapper
from data_deidentifier.domain.contracts.anonymizer.structured import (
    StructuredDataAnonymizerContract,
)
from data_deidentifier.domain.exceptions import StructuredDataAnonymizationError
from data_deidentifier.domain.types.anonymization_operator import (
    AnonymizationOperator,
)
from data_deidentifier.domain.types.language import SupportedLanguage
from data_deidentifier.domain.types.structured_anonymization_result import (
    StructuredDataAnonymizationResult,
)
from data_deidentifier.domain.types.structured_data import StructuredData


class PresidioStructuredDataAnonymizer(StructuredDataAnonymizerContract):
    """Implementation of the data anonymizer contract using Presidio-structured."""

    def __init__(self, logger: LoggerContract) -> None:
        """Initialize the Presidio-structured anonymizer.

        Args:
            logger: Logger for logging events
        """
        self.logger = logger

        self.analyzer = PresidioStructuredDataAnalyzer(logger=self.logger)

        self.logger.debug("Presidio Structured Anonymizer initialized successfully")

    @override
    def anonymize(
        self,
        data: StructuredData,
        operator: AnonymizationOperator,
        language: SupportedLanguage,
        entity_types: list[str] | None = None,
        operator_params: dict[str, Any] | None = None,
    ) -> StructuredDataAnonymizationResult:
        flat_data = flatten(data)

        try:
            # Use the analyzer to process the data
            analyzer_results, data_processor = self.analyzer.analyze(
                data=flat_data,
                language=language,
                entity_types=entity_types,
            )
        except StructuredDataAnalysisError as e:
            raise StructuredDataAnonymizationError(
                "Anonymization failed during analysis",
            ) from e

        # Convert results to our format
        fields = PresidioStructuredDataMapper.presidio_result_to_domain(
            analysis=analyzer_results,
        )

        logger_context = {
            "data_type": str(type(data)),
            "fields_count": len(fields),
            "operator": operator.value,
        }
        self.logger.debug("Starting structured data anonymization", logger_context)

        # Get the appropriate data processor for this data type
        engine = PresidioEngineFactory.get_structured_data_anonymizer_engine(
            processor=data_processor,
        )
        operators = engine.build_operators(
            operator=operator,
            fields=fields,
            operator_params=operator_params,
        )

        try:
            # Anonymize the structured data
            anonymized_data = engine.anonymize(
                data=flat_data,
                structured_analysis=analyzer_results,
                operators=operators,
            )
        except Exception as e:
            msg = "Unexpected error during structured data anonymization"
            self.logger.exception(msg, e, logger_context)
            raise StructuredDataAnonymizationError(msg) from e

        self.logger.info(
            "Structured data anonymization completed successfully",
            logger_context,
        )

        return StructuredDataAnonymizationResult(
            anonymized_data=unflatten(anonymized_data),
            detected_fields=engine.detected_fields,
        )
