from presidio_analyzer import RecognizerResult
from presidio_structured import StructuredAnalysis as PresidioStructuredAnalysis

from data_deidentifier.domain.types.entity import Entity
from data_deidentifier.domain.types.structured_anonymization_result import (
    StructuredDataAnalysisField,
)


class PresidioEntityMapper:
    """Handles the conversion between domain entities and Presidio's formats."""

    @staticmethod
    def presidio_result_to_domain(result: RecognizerResult, text: str) -> Entity:
        """Convert a Presidio RecognizerResult to our Entity model.

        Args:
            result: Presidio's analysis result
            text: Original text (to extract the entity text)

        Returns:
            Entity object with our model
        """
        # Extract text segment
        start = result.start
        end = result.end
        entity_text = (
            text[start:end] if text and start is not None and end is not None else None
        )

        return Entity(
            type=result.entity_type,
            start=start,
            end=end,
            score=result.score,
            text=entity_text,
        )


class PresidioStructuredDataMapper:
    """Handles the conversion between domain and Presidio's structured data analysis."""

    @staticmethod
    def presidio_result_to_domain(
        analysis: PresidioStructuredAnalysis,
    ) -> list[StructuredDataAnalysisField]:
        """Convert a Presidio StructuredAnalysis to list of domain fields.

        Args:
            analysis: Presidio's structured analysis object containing entity mapping.

        Returns:
            StructuredAnalysisResult object with detected fields and their entity types.
        """
        return [
            StructuredDataAnalysisField(
                field_name=field_name,
                entity_type=entity_type,
            )
            for field_name, entity_type in analysis.entity_mapping.items()
        ]
