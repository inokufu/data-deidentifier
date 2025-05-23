from abc import ABC, abstractmethod

from src.data_deidentifier.domain.types.entity import Entity
from src.data_deidentifier.domain.types.operators import AnonymizationOperator


class TextAnonymizerContract(ABC):
    """Abstract base class defining the text anonymizer interface."""

    @abstractmethod
    def anonymize(
        self,
        text: str,
        entities: list[Entity],
        operator: AnonymizationOperator,
    ) -> str:
        """Anonymize PII entities in text.

        Args:
            text: Original text containing PII entities
            entities: List of entities to anonymize
            operator: Anonymization method

        Returns:
            Anonymized text with PII entities replaced

        Raises:
            AnonymizationError: If anonymization fails
        """
        raise NotImplementedError
