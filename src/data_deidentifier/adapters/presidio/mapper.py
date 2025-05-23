from presidio_analyzer import RecognizerResult
from presidio_structured import StructuredAnalysis as PresidioStructuredAnalysis

from src.data_deidentifier.domain.types.entity import Entity
from src.data_deidentifier.domain.types.structured_analysis_result import (
    StructuredAnalysisField,
    StructuredAnalysisResult,
)


class PresidioEntityMapper:
    """Handles the conversion between domain entities and Presidio's formats."""

    @staticmethod
    def presidio_result_to_entity(result: RecognizerResult, text: str) -> Entity:
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

    @staticmethod
    def entity_to_presidio_result(entity: Entity) -> RecognizerResult:
        """Convert our Entity model to Presidio's RecognizerResult format.

        Args:
            entity: Entity object with our model

        Returns:
            Presidio's analysis result
        """
        return RecognizerResult(
            entity_type=entity.type,
            start=entity.start,
            end=entity.end,
            score=entity.score,
        )


class PresidioStructuredMapper:
    """Handles the conversion between domain and Presidio's structured analysis."""

    @staticmethod
    def presidio_result_to_domain(
        analysis: PresidioStructuredAnalysis,
    ) -> list[StructuredAnalysisField]:
        """Convert a Presidio StructuredAnalysis to list of domain fields.

        Args:
            analysis: Presidio's structured analysis object containing entity mapping.

        Returns:
            StructuredAnalysisResult object with detected fields and their entity types.
        """
        return [
            StructuredAnalysisField(
                field_name=field_name,
                entity_type=entity_type,
            )
            for field_name, entity_type in analysis.entity_mapping.items()
        ]

    @staticmethod
    def domain_to_presidio_result(
        result: StructuredAnalysisResult,
    ) -> PresidioStructuredAnalysis:
        """Convert our domain StructuredAnalysisResult to Presidio's format.

        Args:
            result: Domain structured result object containing detected fields.

        Returns:
            Presidio's StructuredAnalysis object with entity mapping.
        """
        return PresidioStructuredAnalysis(entity_mapping=result.entity_mapping)
