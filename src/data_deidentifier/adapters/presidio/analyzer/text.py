from logger import LoggerContract
from presidio_analyzer import RecognizerResult

from src.data_deidentifier.adapters.presidio.engines import PresidioEngineFactory
from src.data_deidentifier.adapters.presidio.exceptions import TextAnalysisError
from src.data_deidentifier.domain.types.language import SupportedLanguage


class PresidioTextAnalyzer:
    """Uses the Presidio Analyzer to detect PII entities in text."""

    def __init__(self, logger: LoggerContract) -> None:
        """Initialize the Presidio text analyzer.

        Args:
            logger: Logger for logging events
        """
        self.logger = logger

        self._presidio_analyzer = PresidioEngineFactory.get_analyzer_engine()

        self.logger.debug("Presidio Analyzer initialized successfully")

    def analyze(
        self,
        text: str,
        language: SupportedLanguage,
        min_score: float,
        entity_types: list[str] | None = None,
    ) -> list[RecognizerResult]:
        """Analyze text to detect PII entities.

        Args:
            text: Text to analyze
            language: Language code of the text
            min_score: Minimum confidence score threshold
            entity_types: Types of entities to detect (None means all supported types)

        Returns:
            List of detected entities

        Raises:
            TextAnalysisError: If analysis fails
        """
        language = language.lower()

        logger_context = {
            "text_length": len(text),
            "language": language,
            "min_score": min_score,
            "entity_types": entity_types,
        }
        self.logger.debug("Starting text analysis", logger_context)

        try:
            # Analyze text
            presidio_results = self._presidio_analyzer.analyze(
                text=text,
                language=language,
                score_threshold=min_score,
                entities=entity_types,
            )
        except Exception as e:
            msg = "Unexpected error during entity recognition"
            self.logger.exception(msg, e, logger_context)
            raise TextAnalysisError(msg) from e

        self.logger.info(
            "Analysis completed successfully",
            {"entities_found": len(presidio_results), **logger_context},
        )

        return presidio_results
