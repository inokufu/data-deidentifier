from types import SimpleNamespace

from src.data_deidentifier.adapters.presidio.mapper import (
    PresidioEntityMapper,
    PresidioStructuredDataMapper,
)
from src.data_deidentifier.domain.types.entity import Entity
from src.data_deidentifier.domain.types.structured_anonymization_result import (
    StructuredDataAnalysisField,
)


class TestPresidioEntityMapper:
    """Test PresidioEntityMapper conversion logic."""

    def test_presidio_result_to_domain_success(self) -> None:
        """Should convert RecognizerResult to Entity with text extraction."""
        # Arrange
        presidio_result = SimpleNamespace(
            entity_type="PERSON",
            start=0,
            end=4,
            score=0.95,
        )
        text = "John works at ACME Corp"

        # Act
        entity = PresidioEntityMapper.presidio_result_to_domain(
            result=presidio_result,
            text=text,
        )

        # Assert
        assert isinstance(entity, Entity)
        assert entity.type == "PERSON"
        assert entity.start == 0
        assert entity.end == 4
        assert entity.score == 0.95
        assert entity.text == "John"  # Extracted from text[0:4]
        assert entity.path is None

    def test_presidio_result_to_domain_mid_text_extraction(self) -> None:
        """Should extract text from middle of string."""
        # Arrange
        presidio_result = SimpleNamespace(
            entity_type="ORG",
            start=14,
            end=23,
            score=0.88,
        )
        text = "John works at ACME Corp"

        # Act
        entity = PresidioEntityMapper.presidio_result_to_domain(
            result=presidio_result,
            text=text,
        )

        # Assert
        assert entity.type == "ORG"
        assert entity.start == 14
        assert entity.end == 23
        assert entity.score == 0.88
        assert entity.text == "ACME Corp"  # Extracted from text[14:23]
        assert entity.path is None

    def test_presidio_result_to_domain_with_unicode_text(self) -> None:
        """Should handle Unicode characters in text."""
        # Arrange
        presidio_result = SimpleNamespace(
            entity_type="PERSON",
            start=0,
            end=4,
            score=0.97,
        )
        text = "José lives in Paris 🇫🇷"

        # Act
        entity = PresidioEntityMapper.presidio_result_to_domain(
            result=presidio_result,
            text=text,
        )

        # Assert
        assert entity.type == "PERSON"
        assert entity.start == 0
        assert entity.end == 4
        assert entity.score == 0.97
        assert entity.text == "José"
        assert entity.path is None


class TestPresidioStructuredDataMapper:
    """Test PresidioStructuredDataMapper conversion logic."""

    def test_presidio_result_to_domain_success(self) -> None:
        """Should convert StructuredAnalysis to list of fields."""
        # Arrange
        mapping = {
            "name": "PERSON",
            "email": "EMAIL",
            "phone": "PHONE_NUMBER",
        }
        analysis = SimpleNamespace(entity_mapping=mapping)

        # Act
        fields = PresidioStructuredDataMapper.presidio_result_to_domain(
            analysis=analysis,
        )

        # Assert
        assert len(fields) == 3
        assert all(isinstance(field, StructuredDataAnalysisField) for field in fields)

        # Convert to dict for easier assertion
        result_mapping = {field.field_name: field.entity_type for field in fields}
        assert result_mapping == mapping

    def test_presidio_result_to_domain_empty_mapping(self) -> None:
        """Should handle empty entity mapping."""
        # Arrange
        analysis = SimpleNamespace(entity_mapping={})

        # Act
        fields = PresidioStructuredDataMapper.presidio_result_to_domain(
            analysis=analysis,
        )

        # Assert
        assert fields == []

    def test_presidio_result_to_domain_nested_field_names(self) -> None:
        """Should handle nested field names (dot notation)."""
        # Arrange
        mapping = {
            "user.profile.name": "PERSON",
            "user.profile.email": "EMAIL",
            "user.addresses.0.city": "LOCATION",
        }
        analysis = SimpleNamespace(entity_mapping=mapping)

        # Act
        fields = PresidioStructuredDataMapper.presidio_result_to_domain(
            analysis=analysis,
        )

        # Assert
        assert len(fields) == 3
        result_mapping = {field.field_name: field.entity_type for field in fields}
        assert result_mapping == mapping
