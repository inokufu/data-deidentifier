from abc import ABC, abstractmethod

from src.data_deidentifier.domain.types.entity import Entity


class TextAnalyzerContract(ABC):
    """Abstract base class defining the analyzer interface."""

    @abstractmethod
    def analyze(
        self,
        text: str,
        language: str,
        min_score: float,
        entity_types: list[str] | None = None,
    ) -> list[Entity]:
        """Analyze text to detect PII entities.

        Args:
            text: Text to analyze
            language: Language code of the text
            min_score: Minimum confidence score threshold
            entity_types: Types of entities to detect (None means all supported types)

        Returns:
            List of detected entities

        Raises:
            AnalysisError: If analysis fails
        """
        raise NotImplementedError
