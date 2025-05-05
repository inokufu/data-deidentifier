from src.data_deidentifier.domain.contracts.analyzer.text import TextAnalyzerContract
from src.data_deidentifier.domain.contracts.validator import EntityTypeValidatorContract
from src.data_deidentifier.domain.types.analysis_result import AnalysisResult


class TextAnalysisService:
    """Service for analyzing text to detect personally identifiable information.

    This service orchestrates the text analysis process, manages default values,
    and produces structured analysis results.
    """

    def __init__(
        self,
        analyzer: TextAnalyzerContract,
        validator: EntityTypeValidatorContract,
        default_language: str,
        default_min_score: float,
        default_entity_types: list[str],
    ) -> None:
        """Initialize the text analyzer service.

        Args:
            analyzer: Implementation of the analyzer contract
            validator: Implementation of the validator contract
            default_language: Default language code to use if not specified
            default_min_score: Default minimum confidence score to use if not specified
            default_entity_types: Default entity types to detect
        """
        self.analyzer = analyzer
        self.validator = validator
        self.default_language = default_language
        self.default_min_score = default_min_score
        self.default_entity_types = default_entity_types

    def analyze(
        self,
        text: str,
        language: str | None = None,
        min_score: float | None = None,
        entity_types: list[str] | None = None,
    ) -> AnalysisResult:
        """Analyze text to detect PII entities.

        Args:
            text: The text content to analyze
            language: Language code of the text (defaults to configured default)
            min_score: Minimum confidence score (defaults to configured default)
            entity_types: Entity types to detect

        Returns:
            An AnalysisResult containing the detected entities and analysis metadata
        """
        effective_language = language or self.default_language
        effective_min_score = (
            min_score if min_score is not None else self.default_min_score
        )

        # Validate data
        raw_entity_types = entity_types or self.default_entity_types
        effective_entity_types = self.validator.validate_entity_types(
            entity_types=raw_entity_types,
        )

        # Analyze the text
        entities = self.analyzer.analyze(
            text=text,
            language=effective_language,
            min_score=effective_min_score,
            entity_types=effective_entity_types,
        )

        # Build stats
        entity_stats = {}
        for entity in entities:
            entity_type = entity.type
            entity_stats[entity_type] = entity_stats.get(entity_type, 0) + 1

        return AnalysisResult(
            entities=entities,
            language=effective_language,
            min_score=effective_min_score,
            entity_stats=entity_stats,
        )
