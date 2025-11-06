from src.data_deidentifier.domain.types.entity import Entity
from src.data_deidentifier.domain.types.text_anonymization_result import (
    TextAnonymizationResult,
)


class TestTextAnonymizationResult:
    """Test TextAnonymizationResult dataclass."""

    def test_create_result_with_empty_entities(self) -> None:
        """Should create result with empty entities list."""
        result = TextAnonymizationResult(
            anonymized_text="Hello world",
            detected_entities=[],
        )

        assert result.anonymized_text == "Hello world"
        assert result.detected_entities == []

    def test_create_result_with_entities(self) -> None:
        """Should create result with detected entities."""
        entities = [
            Entity(type="PERSON", start=0, end=4, score=0.95, text="John"),
            Entity(
                type="EMAIL_ADDRESS",
                start=10,
                end=24,
                score=0.88,
                text="john@email.com",
            ),
        ]

        result = TextAnonymizationResult(
            anonymized_text="<PERSON> sent to <EMAIL>",
            detected_entities=entities,
        )

        assert result.anonymized_text == "<PERSON> sent to <EMAIL>"
        assert len(result.detected_entities) == 2
        assert result.detected_entities[0].type == "PERSON"
        assert result.detected_entities[1].type == "EMAIL_ADDRESS"
