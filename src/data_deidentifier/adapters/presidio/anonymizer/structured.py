from typing import override

from logger import LoggerContract
from presidio_anonymizer.entities import OperatorConfig
from presidio_structured import StructuredEngine

from src.data_deidentifier.adapters.presidio.analyzer.structured_types.factory import (
    StructuredDataAnalyzerFactory,
)
from src.data_deidentifier.adapters.presidio.mapper import PresidioStructuredMapper
from src.data_deidentifier.domain.contracts.anonymizer.structured import (
    StructuredDataAnonymizerContract,
)
from src.data_deidentifier.domain.exceptions import StructuredDataAnonymizationError
from src.data_deidentifier.domain.types.operators import AnonymizationOperator
from src.data_deidentifier.domain.types.structured_analysis_result import (
    StructuredDataAnalysisField,
)
from src.data_deidentifier.domain.types.structured_data import StructuredData


class PresidioStructuredDataAnonymizer(StructuredDataAnonymizerContract):
    """Implementation of the data anonymizer contract using Presidio-structured."""

    def __init__(self, logger: LoggerContract) -> None:
        """Initialize the Presidio-structured anonymizer.

        Args:
            logger: Logger for logging events
        """
        self.logger = logger

        self.analyzer_factory = StructuredDataAnalyzerFactory(logger)

        self.logger.debug("Presidio Structured Anonymizer initialized successfully")

    @override
    def anonymize(
        self,
        data: StructuredData,
        fields: list[StructuredDataAnalysisField],
        operator: AnonymizationOperator,
    ) -> StructuredData:
        if not data or not fields:
            return data

        logger_context = {
            "data_type": str(type(data)),
            "fields_count": len(fields),
            "operator": operator.value,
        }
        self.logger.debug("Starting structured data anonymization", logger_context)

        # Convert domain fields to Presidio StructuredAnalysis
        presidio_analysis = PresidioStructuredMapper.domain_to_presidio_result(
            fields=fields,
        )

        # Prepare operator config
        entity_types = {field.entity_type for field in fields}
        operator_config = OperatorConfig(operator_name=operator)
        operators = {entity_type: operator_config for entity_type in entity_types}

        # Get the appropriate data processor for this data type
        analyzer = self.analyzer_factory.get_analyzer(data=data)
        data_processor = analyzer.get_data_processor()
        engine = StructuredEngine(data_processor=data_processor)

        try:
            # Anonymize the structured data
            anonymized_data = engine.anonymize(
                data=data,
                structured_analysis=presidio_analysis,
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

        return anonymized_data
