from unittest.mock import Mock, patch

import pytest

from src.data_deidentifier.domain.contracts.pseudonymizer.method import (
    PseudonymizationMethodContract,
)
from src.data_deidentifier.domain.contracts.pseudonymizer.text import (
    TextPseudonymizerContract,
)
from src.data_deidentifier.domain.contracts.validator import EntityTypeValidatorContract
from src.data_deidentifier.domain.exceptions import (
    EntityTypeValidationError,
    InvalidInputTextError,
    TextPseudonymizationError,
    UnknownPseudonymizationMethodError,
)
from src.data_deidentifier.domain.services.pseudonymization.methods.factory import (
    PseudonymizationMethodFactory,
)
from src.data_deidentifier.domain.services.pseudonymization.text import (
    TextPseudonymizationService,
)
from src.data_deidentifier.domain.types.language import SupportedLanguage
from src.data_deidentifier.domain.types.pseudonymization_method import (
    PseudonymizationMethod,
)
from src.data_deidentifier.domain.types.text_pseudonymization_result import (
    TextPseudonymizationResult,
)


class TestTextPseudonymizationServiceSuccess:
    """Test successful pseudonymization scenarios."""

    @patch.object(
        target=PseudonymizationMethodFactory,
        attribute="create",
        return_value=Mock(spec=PseudonymizationMethodContract),
    )
    def test_pseudonymize_text_success_with_enricher(
        self,
        mock_factory_create: Mock,
        mock_text_pseudonymization_service_with_enricher: TextPseudonymizationService,
        mock_text_pseudonymizer: TextPseudonymizerContract,
        mock_entity_validator: EntityTypeValidatorContract,
        sample_pseudonymization_result: TextPseudonymizationResult,
    ) -> None:
        """Should successfully pseudonymize text with enricher."""
        # Arrange
        text = "John lives in London"
        method = PseudonymizationMethod.RANDOM_NUMBER
        language = SupportedLanguage.ENGLISH
        min_score = 0.8
        entity_types = ["PERSON", "LOCATION"]

        mock_entity_validator.validate_entity_types.return_value = entity_types
        mock_text_pseudonymizer.pseudonymize.return_value = (
            sample_pseudonymization_result
        )

        # Act
        result = mock_text_pseudonymization_service_with_enricher.pseudonymize(
            text=text,
            method=method,
            language=language,
            min_score=min_score,
            entity_types=entity_types,
        )

        # Assert
        assert result == sample_pseudonymization_result

        # Verify dependencies called correctly
        mock_factory_create.assert_called_once_with(
            method=method,
            method_params={},
            logger=mock_text_pseudonymization_service_with_enricher.logger,
        )
        mock_entity_validator.validate_entity_types.assert_called_once_with(
            entity_types=entity_types,
        )
        mock_text_pseudonymizer.pseudonymize.assert_called_once_with(
            text=text,
            method=mock_factory_create.return_value,
            entity_types=entity_types,
            language=language,
            min_score=min_score,
            pseudonym_enricher=mock_text_pseudonymization_service_with_enricher.pseudonym_enricher,
        )

    @patch.object(
        target=PseudonymizationMethodFactory,
        attribute="create",
        return_value=Mock(spec=PseudonymizationMethodContract),
    )
    def test_pseudonymize_text_success_without_enricher(
        self,
        mock_factory_create: Mock,
        mock_text_pseudonymization_service: TextPseudonymizationService,
        mock_text_pseudonymizer: TextPseudonymizerContract,
        sample_pseudonymization_result: TextPseudonymizationResult,
    ) -> None:
        """Should successfully pseudonymize text without enricher."""
        # Arrange
        mock_text_pseudonymizer.pseudonymize.return_value = (
            sample_pseudonymization_result
        )

        # Act
        result = mock_text_pseudonymization_service.pseudonymize(
            text="John is a person",
            method=PseudonymizationMethod.COUNTER,
            language=SupportedLanguage.ENGLISH,
            min_score=0.5,
            entity_types=[],
        )

        # Assert
        assert result == sample_pseudonymization_result
        mock_text_pseudonymizer.pseudonymize.assert_called_once()
        # Verify enricher is None
        call_args = mock_text_pseudonymizer.pseudonymize.call_args
        assert call_args.kwargs["pseudonym_enricher"] is None

    @patch.object(
        target=PseudonymizationMethodFactory,
        attribute="create",
        return_value=Mock(spec=PseudonymizationMethodContract),
    )
    def test_pseudonymize_text_with_method_params(
        self,
        mock_factory_create: Mock,
        mock_text_pseudonymization_service: TextPseudonymizationService,
        mock_text_pseudonymizer: TextPseudonymizerContract,
        mock_entity_validator: EntityTypeValidatorContract,
        sample_pseudonymization_result: TextPseudonymizationResult,
    ) -> None:
        """Should pass method parameters to factory."""
        # Arrange
        method_params = {"start_number": 100}
        mock_entity_validator.validate_entity_types.return_value = []
        mock_text_pseudonymizer.pseudonymize.return_value = (
            sample_pseudonymization_result
        )

        # Act
        mock_text_pseudonymization_service.pseudonymize(
            text="Some text",
            method=PseudonymizationMethod.COUNTER,
            language=SupportedLanguage.ENGLISH,
            min_score=0.7,
            entity_types=[],
            method_params=method_params,
        )

        # Assert
        mock_factory_create.assert_called_once_with(
            method=PseudonymizationMethod.COUNTER,
            method_params=method_params,
            logger=mock_text_pseudonymization_service.logger,
        )

    @patch.object(
        target=PseudonymizationMethodFactory,
        attribute="create",
        return_value=Mock(spec=PseudonymizationMethodContract),
    )
    def test_pseudonymize_text_with_empty_entity_types(
        self,
        mock_factory_create: Mock,
        mock_text_pseudonymization_service: TextPseudonymizationService,
        mock_text_pseudonymizer: TextPseudonymizerContract,
        mock_entity_validator: EntityTypeValidatorContract,
        sample_pseudonymization_result: TextPseudonymizationResult,
    ) -> None:
        """Should handle empty entity types list."""
        # Arrange
        mock_entity_validator.validate_entity_types.return_value = []
        mock_text_pseudonymizer.pseudonymize.return_value = (
            sample_pseudonymization_result
        )

        # Act
        result = mock_text_pseudonymization_service.pseudonymize(
            text="Clean text",
            method=PseudonymizationMethod.CRYPTO_HASH,
            language=SupportedLanguage.ENGLISH,
            min_score=0.9,
            entity_types=[],
        )

        # Assert
        assert result == sample_pseudonymization_result
        mock_entity_validator.validate_entity_types.assert_called_once_with(
            entity_types=[],
        )


class TestTextPseudonymizationServiceInputValidation:
    """Test input validation scenarios."""

    @pytest.mark.parametrize(
        "invalid_text",
        ["", " ", "\n", "\t", "   ", "\n\n\t   \n"],
    )
    def test_pseudonymize_various_empty_texts_raise_error(
        self,
        mock_text_pseudonymization_service: TextPseudonymizationService,
        invalid_text: str,
    ) -> None:
        """Should raise InvalidInputTextError for various empty/whitespace texts."""
        with pytest.raises(InvalidInputTextError, match="Text cannot be empty"):
            mock_text_pseudonymization_service.pseudonymize(
                text=invalid_text,
                method=PseudonymizationMethod.RANDOM_NUMBER,
                language=SupportedLanguage.ENGLISH,
                min_score=0.8,
                entity_types=[],
            )


class TestTextPseudonymizationServiceErrorHandling:
    """Test error handling and exception chaining."""

    @patch.object(
        target=PseudonymizationMethodFactory,
        attribute="create",
        side_effect=UnknownPseudonymizationMethodError(
            "Unsupported pseudonymization method",
        ),
    )
    def test_pseudonymize_when_factory_fails_chains_exception(
        self,
        mock_factory_create: Mock,
        mock_text_pseudonymization_service: TextPseudonymizationService,
        mock_text_pseudonymizer: TextPseudonymizerContract,
        mock_entity_validator: EntityTypeValidatorContract,
    ) -> None:
        """Should chain exception when method factory fails."""
        # Act & Assert
        with pytest.raises(
            TextPseudonymizationError,
            match="Pseudonymization method loading failed",
        ):
            mock_text_pseudonymization_service.pseudonymize(
                text="Valid text",
                method=PseudonymizationMethod.RANDOM_NUMBER,
                language=SupportedLanguage.ENGLISH,
                min_score=0.8,
                entity_types=[],
            )

        # Validator and pseudonymizer should not be called
        mock_entity_validator.validate_entity_types.assert_not_called()
        mock_text_pseudonymizer.pseudonymize.assert_not_called()

    @patch.object(
        target=PseudonymizationMethodFactory,
        attribute="create",
        return_value=Mock(spec=PseudonymizationMethodContract),
    )
    def test_pseudonymize_when_validator_fails_chains_exception(
        self,
        mock_factory_create: Mock,
        mock_text_pseudonymization_service: TextPseudonymizationService,
        mock_entity_validator: EntityTypeValidatorContract,
    ) -> None:
        """Should chain exception when validator fails."""
        # Arrange
        mock_entity_validator.validate_entity_types.side_effect = (
            EntityTypeValidationError("Invalid entity type: UNKNOWN")
        )

        # Act & Assert
        with pytest.raises(EntityTypeValidationError):
            mock_text_pseudonymization_service.pseudonymize(
                text="Valid text",
                method=PseudonymizationMethod.RANDOM_NUMBER,
                language=SupportedLanguage.ENGLISH,
                min_score=0.8,
                entity_types=["UNKNOWN"],
            )

    @patch.object(
        target=PseudonymizationMethodFactory,
        attribute="create",
        return_value=Mock(spec=PseudonymizationMethodContract),
    )
    def test_pseudonymize_when_pseudonymizer_fails_chains_exception(
        self,
        mock_factory_create: Mock,
        mock_text_pseudonymization_service: TextPseudonymizationService,
        mock_text_pseudonymizer: TextPseudonymizerContract,
    ) -> None:
        """Should chain exception when pseudonymizer fails."""
        # Arrange
        mock_text_pseudonymizer.pseudonymize.side_effect = TextPseudonymizationError(
            "Pseudonymization failed",
        )

        # Act & Assert
        with pytest.raises(TextPseudonymizationError):
            mock_text_pseudonymization_service.pseudonymize(
                text="Valid text",
                method=PseudonymizationMethod.RANDOM_NUMBER,
                language=SupportedLanguage.ENGLISH,
                min_score=0.8,
                entity_types=[],
            )


class TestTextPseudonymizationServiceEdgeCases:
    """Test edge cases and boundary conditions."""

    @patch.object(
        target=PseudonymizationMethodFactory,
        attribute="create",
        return_value=Mock(spec=PseudonymizationMethodContract),
    )
    def test_pseudonymize_with_very_long_text(
        self,
        mock_factory_create: Mock,
        mock_text_pseudonymization_service: TextPseudonymizationService,
        mock_text_pseudonymizer: TextPseudonymizerContract,
        sample_pseudonymization_result: TextPseudonymizationResult,
    ) -> None:
        """Should handle very long text."""
        # Arrange
        long_text = "John " * 10000
        mock_text_pseudonymizer.pseudonymize.return_value = (
            sample_pseudonymization_result
        )

        # Act
        result = mock_text_pseudonymization_service.pseudonymize(
            text=long_text,
            method=PseudonymizationMethod.RANDOM_NUMBER,
            language=SupportedLanguage.ENGLISH,
            min_score=0.8,
            entity_types=[],
        )

        # Assert
        assert result == sample_pseudonymization_result

    @patch.object(
        target=PseudonymizationMethodFactory,
        attribute="create",
        return_value=Mock(spec=PseudonymizationMethodContract),
    )
    def test_pseudonymize_with_unicode_text(
        self,
        mock_factory_create: Mock,
        mock_text_pseudonymization_service: TextPseudonymizationService,
        mock_text_pseudonymizer: TextPseudonymizerContract,
        sample_pseudonymization_result: TextPseudonymizationResult,
    ) -> None:
        """Should handle Unicode characters in text."""
        # Arrange
        unicode_text = "José lives in 北京 🌍"
        mock_text_pseudonymizer.pseudonymize.return_value = (
            sample_pseudonymization_result
        )

        # Act
        result = mock_text_pseudonymization_service.pseudonymize(
            text=unicode_text,
            method=PseudonymizationMethod.CRYPTO_HASH,
            language=SupportedLanguage.ENGLISH,
            min_score=0.8,
            entity_types=[],
        )

        # Assert
        assert result == sample_pseudonymization_result
