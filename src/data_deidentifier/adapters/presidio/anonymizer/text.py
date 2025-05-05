from typing import override

from logger import LoggerContract
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from src.data_deidentifier.adapters.presidio.mapper import PresidioEntityMapper
from src.data_deidentifier.domain.contracts.anonymizer.text import (
    TextAnonymizerContract,
)
from src.data_deidentifier.domain.exceptions import AnonymizationError
from src.data_deidentifier.domain.types.entity import Entity
from src.data_deidentifier.domain.types.operators import AnonymizationOperator


class PresidioTextAnonymizer(TextAnonymizerContract):
    """Implementation of anonymizer contract using Microsoft Presidio."""

    def __init__(self, logger: LoggerContract) -> None:
        """Initialize the Presidio anonymizer.

        Args:
            logger: Logger for logging events
        """
        self.logger = logger

        self.presidio_anonymizer = AnonymizerEngine()

        self.logger.debug("Presidio Anonymizer initialized successfully")

    @override
    def anonymize(
        self,
        text: str,
        entities: list[Entity],
        operator: AnonymizationOperator,
    ) -> str:
        if not text or not entities:
            return text

        logger_context = {
            "text_length": len(text),
            "entities_count": len(entities),
            "operator": operator.value,
        }
        self.logger.debug("Starting text anonymization", logger_context)

        # Convert our entities to Presidio's RecognizerResult format
        analyzer_results = [
            PresidioEntityMapper.entity_to_presidio_result(entity=entity)
            for entity in entities
        ]

        # Prepare operator config
        entity_types = {entity.entity_type for entity in analyzer_results}
        operator_config = OperatorConfig(operator_name=operator)
        operators = {entity_type: operator_config for entity_type in entity_types}

        try:
            # Anonymize the text
            result = self.presidio_anonymizer.anonymize(
                text=text,
                analyzer_results=analyzer_results,
                operators=operators,
            )
        except Exception as e:
            msg = "Unexpected error during text anonymization"
            self.logger.exception(msg, e, logger_context)
            raise AnonymizationError(msg) from e

        self.logger.info("Text anonymization completed successfully", logger_context)

        return result.text
