import re

from logger import LoggerContract

from src.data_deidentifier.domain.services.pseudonymization.methods.random_number import (  # noqa: E501
    RandomNumberPseudonymizationMethod,
)
from src.data_deidentifier.domain.types.entity import Entity


class TestRandomNumberPseudonymizationMethodCreation:
    """Test random number method creation."""

    def test_create_with_empty_params(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should create random number method with empty params."""
        # Arrange & Act
        method = RandomNumberPseudonymizationMethod(params={}, logger=mock_logger)

        # Assert
        pseudonym = method.generate_pseudonym(entity=sample_entity)
        assert re.match(pattern=r"<PERSON_\d+>", string=pseudonym)

    def test_create_with_any_params(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should create random number method ignoring any params."""
        # Arrange & Act - params are ignored for this method
        method = RandomNumberPseudonymizationMethod(
            params={"irrelevant_param": "value"},
            logger=mock_logger,
        )

        # Assert
        pseudonym = method.generate_pseudonym(entity=sample_entity)
        assert re.match(pattern=r"<PERSON_\d+>", string=pseudonym)


class TestRandomNumberPseudonymizationMethodGeneration:
    """Test pseudonym generation logic."""

    def test_generate_different_pseudonyms_different_texts(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should generate different pseudonyms for different entity texts."""
        # Arrange
        method = RandomNumberPseudonymizationMethod(params={}, logger=mock_logger)

        john = Entity(type="PERSON", start=0, end=4, score=0.95, text="John")
        jane = Entity(type="PERSON", start=10, end=14, score=0.92, text="Jane")
        bob = Entity(type="PERSON", start=20, end=23, score=0.88, text="Bob")

        # Act
        john_pseudonym = method.generate_pseudonym(entity=john)
        jane_pseudonym = method.generate_pseudonym(entity=jane)
        bob_pseudonym = method.generate_pseudonym(entity=bob)

        # Assert
        assert john_pseudonym != jane_pseudonym
        assert john_pseudonym != bob_pseudonym
        assert jane_pseudonym != bob_pseudonym

    def test_generate_pseudonyms_different_entity_types(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should generate pseudonyms for different entity types."""
        # Arrange
        method = RandomNumberPseudonymizationMethod(params={}, logger=mock_logger)

        email = Entity(
            type="EMAIL",
            start=10,
            end=24,
            score=0.88,
            text="john@email.com",
        )
        phone = Entity(type="PHONE", start=30, end=42, score=0.92, text="+33123456789")

        # Act
        email_pseudonym = method.generate_pseudonym(entity=email)
        phone_pseudonym = method.generate_pseudonym(entity=phone)

        # Assert
        assert re.match(pattern=r"<EMAIL_\d+>", string=email_pseudonym)
        assert re.match(pattern=r"<PHONE_\d+>", string=phone_pseudonym)

    def test_generate_pseudonym_consistency_same_entity_text(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return same pseudonym for same entity text (caching)."""
        # Arrange
        method = RandomNumberPseudonymizationMethod(params={}, logger=mock_logger)

        entity1 = Entity(type="PERSON", start=0, end=4, score=0.95, text="John")
        entity2 = Entity(type="PERSON", start=5, end=9, score=0.92, text="John")

        # Act
        pseudonym1 = method.generate_pseudonym(entity=entity1)
        pseudonym2 = method.generate_pseudonym(entity=entity2)

        # Assert
        assert pseudonym1 == pseudonym2


class TestRandomNumberPseudonymizationMethodEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_generate_pseudonym_with_unicode_text(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle Unicode characters in entity text."""
        # Arrange
        method = RandomNumberPseudonymizationMethod(params={}, logger=mock_logger)
        entity1 = Entity(type="PERSON", start=0, end=6, score=0.95, text="José 🎭")
        entity2 = Entity(type="PERSON", start=7, end=13, score=0.95, text="José 🎭")

        # Act
        pseudonym1 = method.generate_pseudonym(entity=entity1)
        pseudonym2 = method.generate_pseudonym(entity=entity2)

        # Assert
        assert pseudonym1 == pseudonym2

    def test_generate_pseudonym_with_very_long_text(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle very long entity text."""
        # Arrange
        method = RandomNumberPseudonymizationMethod(params={}, logger=mock_logger)
        long_text = "A" * 10000  # Very long text
        entity1 = Entity(type="PERSON", start=0, end=10000, score=0.95, text=long_text)
        entity2 = Entity(type="PERSON", start=0, end=10000, score=0.90, text=long_text)

        # Act
        pseudonym1 = method.generate_pseudonym(entity=entity1)
        pseudonym2 = method.generate_pseudonym(entity=entity2)

        # Assert
        assert pseudonym1 == pseudonym2
