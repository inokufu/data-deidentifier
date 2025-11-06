import pytest

from src.data_deidentifier.domain.contracts.anonymizer.text import (
    TextAnonymizerContract,
)
from src.data_deidentifier.domain.contracts.validator import EntityTypeValidatorContract
from src.data_deidentifier.domain.exceptions import (
    EntityTypeValidationError,
    InvalidInputTextError,
    TextAnonymizationError,
)
from src.data_deidentifier.domain.services.anonymization.text import (
    TextAnonymizationService,
)
from src.data_deidentifier.domain.types.anonymization_operator import (
    AnonymizationOperator,
)
from src.data_deidentifier.domain.types.language import SupportedLanguage
from src.data_deidentifier.domain.types.text_anonymization_result import (
    TextAnonymizationResult,
)


class TestTextAnonymizationServiceSuccess:
    """Test successful anonymization scenarios."""

    def test_anonymize_text_success(
        self,
        mock_text_anonymization_service: TextAnonymizationService,
        mock_text_anonymizer: TextAnonymizerContract,
        mock_entity_validator: EntityTypeValidatorContract,
        sample_text_anonymization_result: TextAnonymizationResult,
    ) -> None:
        """Should successfully anonymize text with valid inputs."""
        # Arrange
        text = "John is a person"
        operator = AnonymizationOperator.REPLACE
        language = SupportedLanguage.ENGLISH
        min_score = 0.8
        entity_types = ["PERSON"]

        mock_entity_validator.validate_entity_types.return_value = entity_types
        mock_text_anonymizer.anonymize.return_value = sample_text_anonymization_result

        # Act
        result = mock_text_anonymization_service.anonymize(
            text=text,
            operator=operator,
            language=language,
            min_score=min_score,
            entity_types=entity_types,
        )

        # Assert
        assert result == sample_text_anonymization_result

        # Verify dependencies called correctly
        mock_entity_validator.validate_entity_types.assert_called_once_with(
            entity_types=entity_types,
        )
        mock_text_anonymizer.anonymize.assert_called_once_with(
            text=text,
            operator=operator,
            language=language,
            min_score=min_score,
            entity_types=entity_types,
            operator_params=None,
        )

    def test_anonymize_text_with_empty_entity_types(
        self,
        mock_text_anonymization_service: TextAnonymizationService,
        mock_text_anonymizer: TextAnonymizerContract,
        mock_entity_validator: EntityTypeValidatorContract,
        sample_text_anonymization_result: TextAnonymizationResult,
    ) -> None:
        """Should handle empty entity types list."""
        # Arrange
        mock_text_anonymizer.anonymize.return_value = sample_text_anonymization_result

        # Act
        mock_text_anonymization_service.anonymize(
            text="Some text",
            operator=AnonymizationOperator.REDACT,
            language=SupportedLanguage.ENGLISH,
            min_score=0.7,
            entity_types=[],
        )

        # Assert
        mock_entity_validator.validate_entity_types.assert_called_once_with(
            entity_types=[],
        )
        mock_text_anonymizer.anonymize.assert_called_once()
        call_args = mock_text_anonymizer.anonymize.call_args
        assert call_args.kwargs["entity_types"] == []

    def test_anonymize_text_with_no_entities_found(
        self,
        mock_text_anonymization_service: TextAnonymizationService,
        mock_text_anonymizer: TextAnonymizerContract,
    ) -> None:
        """Should handle text with no PII entities detected."""
        # Arrange
        result_no_entities = TextAnonymizationResult(
            anonymized_text="Hello world",
            detected_entities=[],
        )
        mock_text_anonymizer.anonymize.return_value = result_no_entities

        # Act
        result = mock_text_anonymization_service.anonymize(
            text="Hello world",
            operator=AnonymizationOperator.REPLACE,
            language=SupportedLanguage.ENGLISH,
            min_score=0.8,
            entity_types=[],
        )

        # Assert
        assert result == result_no_entities


class TestTextAnonymizationServiceInputValidation:
    """Test input validation scenarios."""

    @pytest.mark.parametrize(
        "invalid_text",
        ["", " ", "\n", "\t", "   ", "\n\n\t   \n"],
    )
    def test_anonymize_various_empty_texts_raise_error(
        self,
        mock_text_anonymization_service: TextAnonymizationService,
        invalid_text: str,
    ) -> None:
        """Should raise InvalidInputTextError for various empty/whitespace texts."""
        with pytest.raises(InvalidInputTextError, match="Text cannot be empty"):
            mock_text_anonymization_service.anonymize(
                text=invalid_text,
                operator=AnonymizationOperator.REPLACE,
                language=SupportedLanguage.ENGLISH,
                min_score=0.8,
                entity_types=[],
            )


class TestTextAnonymizationServiceErrorHandling:
    """Test error handling and exception chaining."""

    def test_anonymize_when_validator_fails_chains_exception(
        self,
        mock_text_anonymization_service: TextAnonymizationService,
        mock_entity_validator: EntityTypeValidatorContract,
        mock_text_anonymizer: TextAnonymizerContract,
    ) -> None:
        """Should chain exception when validator fails."""
        # Arrange
        mock_entity_validator.validate_entity_types.side_effect = (
            EntityTypeValidationError("Invalid entity type: UNKNOWN")
        )

        # Act & Assert
        with pytest.raises(EntityTypeValidationError):
            mock_text_anonymization_service.anonymize(
                text="Valid text",
                operator=AnonymizationOperator.REPLACE,
                language=SupportedLanguage.ENGLISH,
                min_score=0.8,
                entity_types=["UNKNOWN"],
            )

        # Anonymizer should not be called
        mock_text_anonymizer.anonymize.assert_not_called()

    def test_anonymize_when_anonymizer_fails_chains_exception(
        self,
        mock_text_anonymization_service: TextAnonymizationService,
        mock_text_anonymizer: TextAnonymizerContract,
    ) -> None:
        """Should chain exception when anonymizer fails."""
        # Arrange
        mock_text_anonymizer.anonymize.side_effect = TextAnonymizationError(
            "Anonymization processing failed",
        )

        # Act & Assert
        with pytest.raises(TextAnonymizationError):
            mock_text_anonymization_service.anonymize(
                text="Valid text",
                operator=AnonymizationOperator.REPLACE,
                language=SupportedLanguage.ENGLISH,
                min_score=0.8,
                entity_types=[],
            )


class TestTextAnonymizationServiceEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_anonymize_with_very_long_text(
        self,
        mock_text_anonymization_service: TextAnonymizationService,
        mock_text_anonymizer: TextAnonymizerContract,
        sample_text_anonymization_result: TextAnonymizationResult,
    ) -> None:
        """Should handle very long text."""
        # Arrange
        long_text = "John " * 10000  # Very long text
        mock_text_anonymizer.anonymize.return_value = sample_text_anonymization_result

        # Act
        result = mock_text_anonymization_service.anonymize(
            text=long_text,
            operator=AnonymizationOperator.REPLACE,
            language=SupportedLanguage.ENGLISH,
            min_score=0.8,
            entity_types=[],
        )

        # Assert
        assert result == sample_text_anonymization_result
        mock_text_anonymizer.anonymize.assert_called_once()

    def test_anonymize_with_unicode_text(
        self,
        mock_text_anonymization_service: TextAnonymizationService,
        mock_text_anonymizer: TextAnonymizerContract,
        sample_text_anonymization_result: TextAnonymizationResult,
    ) -> None:
        """Should handle Unicode characters in text."""
        # Arrange
        unicode_text = "José lives in 北京 🌍"
        mock_text_anonymizer.anonymize.return_value = sample_text_anonymization_result

        # Act
        result = mock_text_anonymization_service.anonymize(
            text=unicode_text,
            operator=AnonymizationOperator.REPLACE,
            language=SupportedLanguage.ENGLISH,
            min_score=0.8,
            entity_types=[],
        )

        # Assert
        assert result == sample_text_anonymization_result
        mock_text_anonymizer.anonymize.assert_called_once()
