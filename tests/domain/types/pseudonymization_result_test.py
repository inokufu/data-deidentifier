from src.data_deidentifier.domain.types.entity import Entity
from src.data_deidentifier.domain.types.text_pseudonymization_result import (
    TextPseudonymizationResult,
)


class TestTextPseudonymizationResult:
    """Test TextPseudonymizationResult dataclass."""

    def test_create_result_with_empty_entities(self) -> None:
        """Should create result with empty entities list."""
        result = TextPseudonymizationResult(
            pseudonymized_text="Hello world",
            detected_entities=[],
        )

        assert result.pseudonymized_text == "Hello world"
        assert result.detected_entities == []

    def test_create_result_with_entities(self) -> None:
        """Should create result with detected entities."""
        entities = [
            Entity(type="PERSON", start=0, end=4, score=0.95, text="John"),
            Entity(type="LOCATION", start=15, end=21, score=0.92, text="London"),
        ]

        result = TextPseudonymizationResult(
            pseudonymized_text="<PERSON_789> lives in <LOCATION_101>",
            detected_entities=entities,
        )

        assert result.pseudonymized_text == "<PERSON_789> lives in <LOCATION_101>"
        assert len(result.detected_entities) == 2
        assert result.detected_entities[0].type == "PERSON"
        assert result.detected_entities[1].type == "LOCATION"
