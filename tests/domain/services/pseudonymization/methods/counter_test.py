import pytest
from logger import LoggerContract

from src.data_deidentifier.domain.services.pseudonymization.methods.counter import (
    CounterPseudonymizationMethod,
)
from src.data_deidentifier.domain.types.entity import Entity


class TestCounterPseudonymizationMethodCreation:
    """Test counter method creation and validation."""

    def test_create_with_default_params(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should create counter method with default start number."""
        # Arrange & Act
        method = CounterPseudonymizationMethod(params={}, logger=mock_logger)

        # Assert
        pseudonym = method.generate_pseudonym(sample_entity)
        assert pseudonym == "<PERSON_1>"

    def test_create_with_any_params(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should create counter method with default start number."""
        # Arrange & Act
        method = CounterPseudonymizationMethod(
            params={"irrelevant_param": "value"},
            logger=mock_logger,
        )

        # Assert
        pseudonym = method.generate_pseudonym(sample_entity)
        assert pseudonym == "<PERSON_1>"

    def test_create_with_custom_start_number(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should create counter method with custom start number."""
        # Arrange & Act
        method = CounterPseudonymizationMethod(
            params={CounterPseudonymizationMethod.PARAM_START_NUMBER: 100},
            logger=mock_logger,
        )

        # Assert
        pseudonym = method.generate_pseudonym(sample_entity)
        assert pseudonym == "<PERSON_100>"

    def test_create_with_negative_start_number_raises_error(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should raise ValueError for negative start number."""
        with pytest.raises(ValueError, match="start_number must be positive"):
            CounterPseudonymizationMethod(
                params={CounterPseudonymizationMethod.PARAM_START_NUMBER: -1},
                logger=mock_logger,
            )

    @pytest.mark.parametrize("invalid_start", ["abc", 1.5, [], {}])
    def test_create_with_various_invalid_start_numbers(
        self,
        invalid_start: any,
        mock_logger: LoggerContract,
    ) -> None:
        """Should raise ValueError for various invalid start number types."""
        with pytest.raises(ValueError, match="start_number must be an integer"):
            CounterPseudonymizationMethod(
                params={
                    CounterPseudonymizationMethod.PARAM_START_NUMBER: invalid_start,
                },
                logger=mock_logger,
            )

    def test_create_with_none_start_number_uses_default(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should use default start number when None provided."""
        # Arrange & Act
        method = CounterPseudonymizationMethod(
            params={CounterPseudonymizationMethod.PARAM_START_NUMBER: None},
            logger=mock_logger,
        )

        # Assert
        pseudonym = method.generate_pseudonym(sample_entity)
        assert pseudonym == "<PERSON_1>"


class TestCounterPseudonymizationMethodGeneration:
    """Test pseudonym generation logic."""

    def test_generate_first_pseudonym_for_entity_type(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should generate first pseudonym with start number."""
        # Arrange
        method = CounterPseudonymizationMethod(params={}, logger=mock_logger)

        # Act
        pseudonym = method.generate_pseudonym(sample_entity)

        # Assert
        assert pseudonym == "<PERSON_1>"

        # Test that next entity gets incremented number
        next_entity = Entity(type="PERSON", start=10, end=14, score=0.92, text="Jane")
        next_pseudonym = method.generate_pseudonym(next_entity)
        assert next_pseudonym == "<PERSON_2>"

    def test_generate_sequential_pseudonyms_same_type(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should generate sequential pseudonyms for same entity type."""
        # Arrange
        method = CounterPseudonymizationMethod(
            params={CounterPseudonymizationMethod.PARAM_START_NUMBER: 10},
            logger=mock_logger,
        )

        entity1 = Entity(type="PERSON", start=0, end=4, score=0.95, text="John")
        entity2 = Entity(type="PERSON", start=5, end=9, score=0.92, text="Jane")
        entity3 = Entity(type="PERSON", start=10, end=13, score=0.88, text="Bob")

        # Act
        pseudonym1 = method.generate_pseudonym(entity1)
        pseudonym2 = method.generate_pseudonym(entity2)
        pseudonym3 = method.generate_pseudonym(entity3)

        # Assert
        assert pseudonym1 == "<PERSON_10>"
        assert pseudonym2 == "<PERSON_11>"
        assert pseudonym3 == "<PERSON_12>"

    def test_generate_pseudonyms_different_entity_types(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should use separate counters for different entity types."""
        # Arrange
        method = CounterPseudonymizationMethod(
            params={CounterPseudonymizationMethod.PARAM_START_NUMBER: 5},
            logger=mock_logger,
        )

        person = Entity(type="PERSON", start=0, end=4, score=0.95, text="John")
        email = Entity(
            type="EMAIL",
            start=10,
            end=24,
            score=0.88,
            text="john@email.com",
        )
        phone = Entity(type="PHONE", start=30, end=42, score=0.92, text="+33123456789")

        # Act
        person_pseudonym = method.generate_pseudonym(person)
        email_pseudonym = method.generate_pseudonym(email)
        phone_pseudonym = method.generate_pseudonym(phone)

        # Assert
        assert person_pseudonym == "<PERSON_5>"
        assert email_pseudonym == "<EMAIL_5>"
        assert phone_pseudonym == "<PHONE_5>"

    def test_generate_pseudonym_consistency_same_entity_text(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return same pseudonym for same entity text (caching)."""
        # Arrange
        method = CounterPseudonymizationMethod(params={}, logger=mock_logger)

        entity1 = Entity(type="PERSON", start=0, end=4, score=0.95, text="John")
        entity2 = Entity(type="PERSON", start=5, end=9, score=0.92, text="John")

        # Act
        pseudonym1 = method.generate_pseudonym(entity1)
        pseudonym2 = method.generate_pseudonym(entity2)

        # Assert
        assert pseudonym1 == "<PERSON_1>"
        assert pseudonym1 == pseudonym2


class TestCounterPseudonymizationMethodEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_generate_pseudonym_with_unicode_text(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle Unicode characters in entity text."""
        # Arrange
        method = CounterPseudonymizationMethod(params={}, logger=mock_logger)
        entity1 = Entity(type="PERSON", start=0, end=6, score=0.95, text="José 🎭")
        entity2 = Entity(type="PERSON", start=7, end=13, score=0.95, text="José 🎭")

        # Act
        pseudonym1 = method.generate_pseudonym(entity1)
        pseudonym2 = method.generate_pseudonym(entity2)

        # Assert - Test Unicode handling and caching
        assert pseudonym1 == "<PERSON_1>"
        assert pseudonym1 == pseudonym2  # Same Unicode text should be cached
