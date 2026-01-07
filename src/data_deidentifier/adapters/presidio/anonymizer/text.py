from typing import Any, override

from logger import LoggerContract
from presidio_anonymizer.entities import OperatorConfig

from data_deidentifier.adapters.presidio.analyzer.text import PresidioTextAnalyzer
from data_deidentifier.adapters.presidio.engines import PresidioEngineFactory
from data_deidentifier.adapters.presidio.exceptions import TextAnalysisError
from data_deidentifier.adapters.presidio.mapper import PresidioEntityMapper
from data_deidentifier.domain.contracts.anonymizer.text import (
    TextAnonymizerContract,
)
from data_deidentifier.domain.exceptions import TextAnonymizationError
from data_deidentifier.domain.types.anonymization_operator import (
    AnonymizationOperator,
)
from data_deidentifier.domain.types.language import SupportedLanguage
from data_deidentifier.domain.types.text_anonymization_result import (
    TextAnonymizationResult,
)


class PresidioTextAnonymizer(TextAnonymizerContract):
    """Implementation of anonymizer contract using Microsoft Presidio."""

    def __init__(self, logger: LoggerContract) -> None:
        """Initialize the Presidio text anonymizer.

        Args:
            logger: Logger for logging events
        """
        self.logger = logger

        self.presidio_anonymizer = PresidioEngineFactory.get_text_anonymizer_engine()
        self.analyzer = PresidioTextAnalyzer(logger=self.logger)

        self.logger.debug("Presidio Anonymizer initialized successfully")

    @override
    def anonymize(
        self,
        text: str,
        operator: AnonymizationOperator,
        language: SupportedLanguage,
        min_score: float,
        entity_types: list[str] | None = None,
        operator_params: dict[str, Any] | None = None,
    ) -> TextAnonymizationResult:
        # Analyze to detect PII entities in text
        try:
            analyzer_results = self.analyzer.analyze(
                text=text,
                language=language,
                min_score=min_score,
                entity_types=entity_types,
            )
        except TextAnalysisError as e:
            raise TextAnonymizationError("Anonymization failed during analysis") from e

        if not text or not analyzer_results:
            return TextAnonymizationResult(
                anonymized_text=text,
                detected_entities=[],
            )

        logger_context = {
            "text_length": len(text),
            "entities_count": len(analyzer_results),
            "operator": operator.value,
        }
        self.logger.debug("Starting text anonymization", logger_context)

        try:
            # Anonymize the text
            presidio_results = self.presidio_anonymizer.anonymize(
                text=text,
                analyzer_results=analyzer_results,
                operators={
                    "DEFAULT": OperatorConfig(
                        operator_name=operator,
                        params=operator_params or {},
                    ),
                },
            )
        except Exception as e:
            msg = "Unexpected error during text anonymization"
            self.logger.exception(msg, e, logger_context)
            raise TextAnonymizationError(msg) from e

        self.logger.info("Text anonymization completed successfully", logger_context)

        # Convert results to our format
        entities = [
            PresidioEntityMapper.presidio_result_to_domain(
                result=result,
                text=text,
            )
            for result in analyzer_results
        ]

        return TextAnonymizationResult(
            anonymized_text=presidio_results.text,
            detected_entities=entities,
        )
