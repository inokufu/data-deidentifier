import hashlib
import re

import pytest
from logger import LoggerContract

from src.data_deidentifier.domain.services.pseudonymization.methods.crypto_hash import (
    CryptoHashPseudonymizationMethod,
)
from src.data_deidentifier.domain.types.entity import Entity


class TestCryptoHashPseudonymizationMethodCreation:
    """Test crypto hash method creation and validation."""

    def test_create_with_default_params(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should create crypto hash method with default empty salt."""
        # Arrange & Act
        method = CryptoHashPseudonymizationMethod(params={}, logger=mock_logger)

        # Assert
        pseudonym = method.generate_pseudonym(entity=sample_entity)
        assert re.match(pattern=r"<PERSON_[A-F0-9]{16}>", string=pseudonym)

    def test_create_with_any_params(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should create crypto hash method ignoring irrelevant params."""
        # Arrange & Act
        method = CryptoHashPseudonymizationMethod(
            params={"irrelevant_param": "value"},
            logger=mock_logger,
        )

        # Assert
        pseudonym = method.generate_pseudonym(entity=sample_entity)
        assert re.match(pattern=r"<PERSON_[A-F0-9]{16}>", string=pseudonym)

    def test_create_with_valid_salt(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should create crypto hash method with valid salt."""
        # Arrange & Act
        method = CryptoHashPseudonymizationMethod(
            params={CryptoHashPseudonymizationMethod.PARAM_SALT: "my_secret_salt"},
            logger=mock_logger,
        )

        # Assert
        pseudonym = method.generate_pseudonym(entity=sample_entity)
        assert re.match(pattern=r"<PERSON_[A-F0-9]{16}>", string=pseudonym)

    def test_create_with_empty_salt(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should create crypto hash method with empty salt (same as no salt)."""
        # Arrange & Act
        method = CryptoHashPseudonymizationMethod(
            params={CryptoHashPseudonymizationMethod.PARAM_SALT: ""},
            logger=mock_logger,
        )

        # Assert
        pseudonym = method.generate_pseudonym(entity=sample_entity)
        assert re.match(pattern=r"<PERSON_[A-F0-9]{16}>", string=pseudonym)

    @pytest.mark.parametrize("invalid_salt", [123, 1.5, [], {}, None])
    def test_create_with_invalid_salt_types_raises_error(
        self,
        invalid_salt: any,
        mock_logger: LoggerContract,
    ) -> None:
        """Should raise ValueError for various invalid salt types."""
        with pytest.raises(ValueError, match="Salt must be a string"):
            CryptoHashPseudonymizationMethod(
                params={CryptoHashPseudonymizationMethod.PARAM_SALT: invalid_salt},
                logger=mock_logger,
            )


class TestCryptoHashPseudonymizationMethodGeneration:
    """Test pseudonym generation logic."""

    def test_generate_same_pseudonym_for_same_entity_text(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should generate same pseudonym for same entity text (deterministic)."""
        # Arrange
        method = CryptoHashPseudonymizationMethod(params={}, logger=mock_logger)

        entity1 = Entity(type="PERSON", start=0, end=4, score=0.95, text="John")
        entity2 = Entity(type="PERSON", start=5, end=9, score=0.92, text="John")

        # Act
        pseudonym1 = method.generate_pseudonym(entity=entity1)
        pseudonym2 = method.generate_pseudonym(entity=entity2)

        # Assert
        assert pseudonym1 == pseudonym2
        assert re.match(pattern=r"<PERSON_[A-F0-9]{16}>", string=pseudonym1)

    def test_generate_different_pseudonyms_different_texts(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should generate different pseudonyms for different entity texts."""
        # Arrange
        method = CryptoHashPseudonymizationMethod(params={}, logger=mock_logger)

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
        """Should generate different pseudonyms for different types with same text."""
        # Arrange
        method = CryptoHashPseudonymizationMethod(params={}, logger=mock_logger)

        # Same text but different entity types
        person = Entity(type="PERSON", start=0, end=4, score=0.95, text="John")
        location = Entity(type="LOCATION", start=0, end=4, score=0.95, text="John")
        ip = Entity(
            type="IP_ADDRESS",
            start=0,
            end=4,
            score=0.95,
            text="John",
        )

        # Act
        person_pseudonym = method.generate_pseudonym(entity=person)
        location_pseudonym = method.generate_pseudonym(entity=location)
        ip_pseudonym = method.generate_pseudonym(entity=ip)

        # Assert
        assert person_pseudonym != location_pseudonym
        assert person_pseudonym != ip_pseudonym
        assert location_pseudonym != ip_pseudonym

    def test_generate_pseudonyms_with_different_salts(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should generate different pseudonyms for same text with different salts."""
        # Arrange
        method1 = CryptoHashPseudonymizationMethod(
            params={CryptoHashPseudonymizationMethod.PARAM_SALT: "salt1"},
            logger=mock_logger,
        )
        method2 = CryptoHashPseudonymizationMethod(
            params={CryptoHashPseudonymizationMethod.PARAM_SALT: "salt2"},
            logger=mock_logger,
        )

        entity = Entity(type="PERSON", start=0, end=4, score=0.95, text="John")

        # Act
        pseudonym1 = method1.generate_pseudonym(entity=entity)
        pseudonym2 = method2.generate_pseudonym(entity=entity)

        # Assert
        assert pseudonym1 != pseudonym2

    def test_generate_pseudonym_consistency_with_caching(
        self,
        sample_entity: Entity,
        mock_logger: LoggerContract,
    ) -> None:
        """Should use cache and return same pseudonym for repeated calls."""
        # Arrange
        method = CryptoHashPseudonymizationMethod(
            params={CryptoHashPseudonymizationMethod.PARAM_SALT: "test_salt"},
            logger=mock_logger,
        )

        # Act - Generate multiple times
        pseudonym1 = method.generate_pseudonym(entity=sample_entity)
        pseudonym2 = method.generate_pseudonym(entity=sample_entity)
        pseudonym3 = method.generate_pseudonym(entity=sample_entity)

        # Assert
        assert pseudonym1 == pseudonym2 == pseudonym3

    def test_generate_predictable_hash_for_known_input(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should generate predictable hash for known input."""
        # Arrange
        salt = "test_salt"
        method = CryptoHashPseudonymizationMethod(
            params={CryptoHashPseudonymizationMethod.PARAM_SALT: salt},
            logger=mock_logger,
        )

        entity = Entity(type="PERSON", start=0, end=4, score=0.95, text="John")

        # Calculate expected hash manually
        hash_input = f"{salt}PERSON:John".encode()
        expected_hash = hashlib.blake2b(hash_input, digest_size=8).hexdigest().upper()
        expected_pseudonym = f"<PERSON_{expected_hash}>"

        # Act
        actual_pseudonym = method.generate_pseudonym(entity=entity)

        # Assert
        assert actual_pseudonym == expected_pseudonym


class TestCryptoHashPseudonymizationMethodEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_generate_pseudonym_with_unicode_text(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle Unicode characters in entity text."""
        # Arrange
        method = CryptoHashPseudonymizationMethod(params={}, logger=mock_logger)
        entity1 = Entity(type="PERSON", start=0, end=6, score=0.95, text="José 🎭")
        entity2 = Entity(type="PERSON", start=7, end=13, score=0.95, text="José 🎭")

        # Act
        pseudonym1 = method.generate_pseudonym(entity=entity1)
        pseudonym2 = method.generate_pseudonym(entity=entity2)

        # Assert - Test Unicode handling and caching
        assert pseudonym1 == pseudonym2
        assert re.match(pattern=r"<PERSON_[A-F0-9]{16}>", string=pseudonym1)

    def test_generate_pseudonym_with_very_long_text(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle very long entity text."""
        # Arrange
        method = CryptoHashPseudonymizationMethod(params={}, logger=mock_logger)
        long_text = "A" * 10000  # Very long text
        entity1 = Entity(type="PERSON", start=0, end=10000, score=0.95, text=long_text)
        entity2 = Entity(type="PERSON", start=0, end=10000, score=0.90, text=long_text)

        # Act
        pseudonym1 = method.generate_pseudonym(entity=entity1)
        pseudonym2 = method.generate_pseudonym(entity=entity2)

        # Assert
        assert pseudonym1 == pseudonym2
        assert re.match(pattern=r"<PERSON_[A-F0-9]{16}>", string=pseudonym1)

    def test_generate_pseudonym_salt_with_special_characters(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle salt with special characters."""
        # Arrange
        special_salt = "salt!@#$%^&*()[]{}|\\:;\"'<>?/~`"
        method = CryptoHashPseudonymizationMethod(
            params={CryptoHashPseudonymizationMethod.PARAM_SALT: special_salt},
            logger=mock_logger,
        )
        entity = Entity(type="PERSON", start=0, end=4, score=0.95, text="John")

        # Act
        pseudonym = method.generate_pseudonym(entity=entity)

        # Assert
        assert re.match(pattern=r"<PERSON_[A-F0-9]{16}>", string=pseudonym)
