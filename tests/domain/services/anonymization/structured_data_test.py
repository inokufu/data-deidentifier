import pytest

from src.data_deidentifier.domain.contracts.anonymizer.structured import (
    StructuredDataAnonymizerContract,
)
from src.data_deidentifier.domain.contracts.validator import EntityTypeValidatorContract
from src.data_deidentifier.domain.exceptions import (
    EntityTypeValidationError,
    InvalidInputDataError,
    StructuredDataAnonymizationError,
)
from src.data_deidentifier.domain.services.anonymization.structured import (
    StructuredDataAnonymizationService,
)
from src.data_deidentifier.domain.types.anonymization_operator import (
    AnonymizationOperator,
)
from src.data_deidentifier.domain.types.language import SupportedLanguage
from src.data_deidentifier.domain.types.structured_anonymization_result import (
    StructuredDataAnonymizationResult,
)


class TestStructuredDataAnonymizationServiceSuccess:
    """Test successful anonymization scenarios."""

    def test_anonymize_data_success(
        self,
        mock_structured_data_anonymization_service: StructuredDataAnonymizationService,
        mock_structured_data_anonymizer: StructuredDataAnonymizerContract,
        mock_entity_validator: EntityTypeValidatorContract,
        sample_structured_data_anonymization_result: StructuredDataAnonymizationResult,
    ) -> None:
        """Should successfully anonymize structured data with valid inputs."""
        # Arrange
        data = {"name": "John Smith", "email": "john@email.com", "age": 30}
        operator = AnonymizationOperator.REPLACE
        language = SupportedLanguage.ENGLISH
        entity_types = ["PERSON", "EMAIL"]

        mock_entity_validator.validate_entity_types.return_value = entity_types
        mock_structured_data_anonymizer.anonymize.return_value = (
            sample_structured_data_anonymization_result
        )

        # Act
        result = mock_structured_data_anonymization_service.anonymize(
            data=data,
            operator=operator,
            language=language,
            entity_types=entity_types,
        )

        # Assert
        assert result == sample_structured_data_anonymization_result

        # Verify dependencies called correctly
        mock_entity_validator.validate_entity_types.assert_called_once_with(
            entity_types=entity_types,
        )
        mock_structured_data_anonymizer.anonymize.assert_called_once_with(
            data=data,
            operator=operator,
            language=language,
            entity_types=entity_types,
            operator_params=None,
        )

    def test_anonymize_data_with_empty_entity_types(
        self,
        mock_structured_data_anonymization_service: StructuredDataAnonymizationService,
        mock_structured_data_anonymizer: StructuredDataAnonymizerContract,
        mock_entity_validator: EntityTypeValidatorContract,
        sample_structured_data_anonymization_result: StructuredDataAnonymizationResult,
    ) -> None:
        """Should handle empty entity types list."""
        # Arrange
        data = {"message": "Hello world", "count": 42}
        mock_entity_validator.validate_entity_types.return_value = []
        mock_structured_data_anonymizer.anonymize.return_value = (
            sample_structured_data_anonymization_result
        )

        # Act
        result = mock_structured_data_anonymization_service.anonymize(
            data=data,
            operator=AnonymizationOperator.REDACT,
            language=SupportedLanguage.ENGLISH,
            entity_types=[],
        )

        # Assert
        assert result == sample_structured_data_anonymization_result
        mock_entity_validator.validate_entity_types.assert_called_once_with(
            entity_types=[],
        )
        mock_structured_data_anonymizer.anonymize.assert_called_once()

    def test_anonymize_data_with_no_pii_detected(
        self,
        mock_structured_data_anonymization_service: StructuredDataAnonymizationService,
        mock_structured_data_anonymizer: StructuredDataAnonymizerContract,
    ) -> None:
        """Should handle data with no PII entities detected."""
        # Arrange
        data = {"settings": {"theme": "dark", "language": "en"}}
        result_no_pii = StructuredDataAnonymizationResult(
            anonymized_data=data,
            detected_fields=[],
        )
        mock_structured_data_anonymizer.anonymize.return_value = result_no_pii

        # Act
        result = mock_structured_data_anonymization_service.anonymize(
            data=data,
            operator=AnonymizationOperator.REPLACE,
            language=SupportedLanguage.ENGLISH,
            entity_types=[],
        )

        # Assert
        assert result == result_no_pii
        assert result.detected_fields == []


class TestStructuredDataAnonymizationServiceInputValidation:
    """Test input validation scenarios."""

    @pytest.mark.parametrize(
        "invalid_data",
        [
            {},
            None,
        ],
    )
    def test_anonymize_various_empty_data_raise_error(
        self,
        mock_structured_data_anonymization_service: StructuredDataAnonymizationService,
        invalid_data: dict | None,
    ) -> None:
        """Should raise InvalidInputDataError for various empty data."""
        with pytest.raises(InvalidInputDataError, match="Data cannot be empty"):
            mock_structured_data_anonymization_service.anonymize(
                data=invalid_data,
                operator=AnonymizationOperator.REPLACE,
                language=SupportedLanguage.ENGLISH,
                entity_types=[],
            )


class TestStructuredDataAnonymizationServiceErrorHandling:
    """Test error handling and exception chaining."""

    def test_anonymize_when_validator_fails_chains_exception(
        self,
        mock_structured_data_anonymization_service: StructuredDataAnonymizationService,
        mock_entity_validator: EntityTypeValidatorContract,
        mock_structured_data_anonymizer: StructuredDataAnonymizerContract,
    ) -> None:
        """Should chain exception when validator fails."""
        # Arrange
        mock_entity_validator.validate_entity_types.side_effect = (
            EntityTypeValidationError("Invalid entity type: UNKNOWN")
        )

        # Act & Assert
        with pytest.raises(EntityTypeValidationError):
            mock_structured_data_anonymization_service.anonymize(
                data={"name": "John"},
                operator=AnonymizationOperator.REPLACE,
                language=SupportedLanguage.ENGLISH,
                entity_types=["UNKNOWN"],
            )

        # Anonymizer should not be called
        mock_structured_data_anonymizer.anonymize.assert_not_called()

    def test_anonymize_when_anonymizer_fails_chains_exception(
        self,
        mock_structured_data_anonymization_service: StructuredDataAnonymizationService,
        mock_structured_data_anonymizer: StructuredDataAnonymizerContract,
    ) -> None:
        """Should chain exception when anonymizer fails."""
        # Arrange
        mock_structured_data_anonymizer.anonymize.side_effect = (
            StructuredDataAnonymizationError(
                "Anonymization processing failed",
            )
        )

        # Act & Assert
        with pytest.raises(StructuredDataAnonymizationError):
            mock_structured_data_anonymization_service.anonymize(
                data={"name": "John"},
                operator=AnonymizationOperator.REPLACE,
                language=SupportedLanguage.ENGLISH,
                entity_types=[],
            )


class TestStructuredDataAnonymizationServiceEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_anonymize_with_deeply_nested_data(
        self,
        mock_structured_data_anonymization_service: StructuredDataAnonymizationService,
        mock_structured_data_anonymizer: StructuredDataAnonymizerContract,
        sample_structured_data_anonymization_result: StructuredDataAnonymizationResult,
    ) -> None:
        """Should handle deeply nested data structures."""
        # Arrange
        nested_data = {
            "user": {
                "profile": {
                    "personal": {
                        "name": "John Doe",
                        "contacts": {
                            "email": "john@email.com",
                            "phones": ["+33123456789", "+33987654321"],
                        },
                    },
                },
            },
            "metadata": {"version": "1.0"},
        }
        mock_structured_data_anonymizer.anonymize.return_value = (
            sample_structured_data_anonymization_result
        )

        # Act
        result = mock_structured_data_anonymization_service.anonymize(
            data=nested_data,
            operator=AnonymizationOperator.REPLACE,
            language=SupportedLanguage.ENGLISH,
            entity_types=["PERSON", "EMAIL", "PHONE_NUMBER"],
        )

        # Assert
        assert result == sample_structured_data_anonymization_result
        mock_structured_data_anonymizer.anonymize.assert_called_once()
