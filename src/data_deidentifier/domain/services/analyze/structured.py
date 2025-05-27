from src.data_deidentifier.domain.contracts.analyzer.structured import (
    StructuredDataAnalyzerContract,
)
from src.data_deidentifier.domain.contracts.validator import EntityTypeValidatorContract
from src.data_deidentifier.domain.exceptions import StructuredDataAnalysisError
from src.data_deidentifier.domain.types.structured_analysis_result import (
    StructuredDataAnalysisResult,
)
from src.data_deidentifier.domain.types.structured_data import StructuredData


class StructuredDataAnalysisService:
    """Service for analyzing structured data to detect PII.

    This service orchestrates the text analysis process, manages default values,
    and produces structured analysis results.
    """

    def __init__(
        self,
        analyzer: StructuredDataAnalyzerContract,
        validator: EntityTypeValidatorContract,
        default_language: str,
        default_entity_types: list[str],
    ) -> None:
        """Initialize the structured analyzer service.

        Args:
            analyzer: Implementation of the structured analyzer contract
            validator: Implementation of the validator contract
            default_language: Default language code to use if not specified
            default_entity_types: Default entity types to detect
        """
        self.analyzer = analyzer
        self.validator = validator
        self.default_language = default_language
        self.default_entity_types = default_entity_types

    def analyze(
        self,
        data: StructuredData,
        language: str | None = None,
        entity_types: list[str] | None = None,
    ) -> StructuredDataAnalysisResult:
        """Analyze structured data to detect PII entities.

        Args:
            data: The structured data to analyze (DataFrame, JSON, etc.)
            language: Language code of the data (defaults to configured default)
            entity_types: Entity types to detect

        Returns:
            A StructuredAnalysisResult containing the entity mapping and metadata
        """
        if not data:
            raise StructuredDataAnalysisError("Data cannot be empty")

        effective_language = language or self.default_language

        # Validate entity types
        raw_entity_types = entity_types or self.default_entity_types
        effective_entity_types = self.validator.validate_entity_types(
            entity_types=raw_entity_types,
        )

        # Analyze data
        fields = self.analyzer.analyze(
            data=data,
            language=effective_language,
            entity_types=effective_entity_types,
        )

        # Build stats
        entity_stats = {}
        for field in fields:
            entity_type = field.entity_type
            entity_stats[entity_type] = entity_stats.get(entity_type, 0) + 1

        return StructuredDataAnalysisResult(
            fields=fields,
            language=effective_language,
            entity_stats=entity_stats,
        )
