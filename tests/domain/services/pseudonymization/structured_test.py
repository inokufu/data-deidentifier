from unittest.mock import Mock, patch

import pytest

from src.data_deidentifier.domain.contracts.pseudonymizer.method import (
    PseudonymizationMethodContract,
)
from src.data_deidentifier.domain.contracts.pseudonymizer.structured import (
    StructuredDataPseudonymizerContract,
)
from src.data_deidentifier.domain.contracts.validator import EntityTypeValidatorContract
from src.data_deidentifier.domain.exceptions import (
    EntityTypeValidationError,
    InvalidInputDataError,
    StructuredDataPseudonymizationError,
    UnknownPseudonymizationMethodError,
)
from src.data_deidentifier.domain.services.pseudonymization.methods.factory import (
    PseudonymizationMethodFactory,
)
from src.data_deidentifier.domain.services.pseudonymization.structured import (
    StructuredDataPseudonymizationService,
)
from src.data_deidentifier.domain.types.language import SupportedLanguage
from src.data_deidentifier.domain.types.pseudonymization_method import (
    PseudonymizationMethod,
)
from src.data_deidentifier.domain.types.structured_pseudonymization_result import (
    StructuredDataPseudonymizationResult,
)


class TestStructuredDataPseudonymizationServiceSuccess:
    """Test successful pseudonymization scenarios."""

    @patch.object(
        PseudonymizationMethodFactory,
        "create",
        return_value=Mock(spec=PseudonymizationMethodContract),
    )
    def test_pseudonymize_data_success_with_enricher(
        self,
        mock_factory_create: Mock,
        mock_data_pseudo_service_with_enricher: StructuredDataPseudonymizationService,
        mock_data_pseudonymizer: StructuredDataPseudonymizerContract,
        mock_entity_validator: EntityTypeValidatorContract,
        sample_structured_pseudonymization_result: StructuredDataPseudonymizationResult,
    ) -> None:
        """Should successfully pseudonymize structured data with enricher."""
        # Arrange
        data = {"name": "John Smith", "email": "john@email.com", "age": 30}
        method = PseudonymizationMethod.RANDOM_NUMBER
        language = SupportedLanguage.ENGLISH
        entity_types = ["PERSON", "EMAIL"]

        mock_entity_validator.validate_entity_types.return_value = entity_types
        mock_data_pseudonymizer.pseudonymize.return_value = (
            sample_structured_pseudonymization_result
        )

        # Act
        result = mock_data_pseudo_service_with_enricher.pseudonymize(
            data=data,
            method=method,
            language=language,
            entity_types=entity_types,
        )

        # Assert
        assert result == sample_structured_pseudonymization_result

        # Verify dependencies called correctly
        mock_factory_create.assert_called_once_with(
            method=method,
            method_params={},
            logger=mock_data_pseudo_service_with_enricher.logger,
        )
        mock_entity_validator.validate_entity_types.assert_called_once_with(
            entity_types=entity_types,
        )
        mock_data_pseudonymizer.pseudonymize.assert_called_once_with(
            data=data,
            method=mock_factory_create.return_value,
            entity_types=entity_types,
            language=language,
            pseudonym_enricher=mock_data_pseudo_service_with_enricher.pseudonym_enricher,
        )

    @patch.object(
        PseudonymizationMethodFactory,
        "create",
        return_value=Mock(spec=PseudonymizationMethodContract),
    )
    def test_pseudonymize_data_success_without_enricher(
        self,
        mock_factory_create: Mock,
        mock_data_pseudonymization_service: StructuredDataPseudonymizationService,
        mock_data_pseudonymizer: StructuredDataPseudonymizerContract,
        sample_structured_pseudonymization_result: StructuredDataPseudonymizationResult,
    ) -> None:
        """Should successfully pseudonymize structured data without enricher."""
        # Arrange
        data = {"user": {"name": "Jane Doe"}, "metadata": {"version": "1.0"}}
        mock_data_pseudonymizer.pseudonymize.return_value = (
            sample_structured_pseudonymization_result
        )

        # Act
        result = mock_data_pseudonymization_service.pseudonymize(
            data=data,
            method=PseudonymizationMethod.COUNTER,
            language=SupportedLanguage.ENGLISH,
            entity_types=[],
        )

        # Assert
        assert result == sample_structured_pseudonymization_result
        mock_data_pseudonymizer.pseudonymize.assert_called_once()
        # Verify enricher is None
        call_args = mock_data_pseudonymizer.pseudonymize.call_args
        assert call_args.kwargs["pseudonym_enricher"] is None

    @patch.object(
        PseudonymizationMethodFactory,
        "create",
        return_value=Mock(spec=PseudonymizationMethodContract),
    )
    def test_pseudonymize_data_with_method_params(
        self,
        mock_factory_create: Mock,
        mock_data_pseudonymization_service: StructuredDataPseudonymizationService,
        mock_data_pseudonymizer: StructuredDataPseudonymizerContract,
        sample_structured_pseudonymization_result: StructuredDataPseudonymizationResult,
    ) -> None:
        """Should pass method parameters to factory."""
        # Arrange
        data = {"company": "ACME Corp", "location": "New York"}
        method_params = {"salt": "secure_salt"}
        mock_data_pseudonymizer.pseudonymize.return_value = (
            sample_structured_pseudonymization_result
        )

        # Act
        mock_data_pseudonymization_service.pseudonymize(
            data=data,
            method=PseudonymizationMethod.CRYPTO_HASH,
            language=SupportedLanguage.ENGLISH,
            entity_types=[],
            method_params=method_params,
        )

        # Assert
        mock_factory_create.assert_called_once_with(
            method=PseudonymizationMethod.CRYPTO_HASH,
            method_params=method_params,
            logger=mock_data_pseudonymization_service.logger,
        )

    @patch.object(
        PseudonymizationMethodFactory,
        "create",
        return_value=Mock(spec=PseudonymizationMethodContract),
    )
    def test_pseudonymize_data_with_empty_entity_types(
        self,
        mock_factory_create: Mock,
        mock_data_pseudonymization_service: StructuredDataPseudonymizationService,
        mock_data_pseudonymizer: StructuredDataPseudonymizerContract,
        mock_entity_validator: EntityTypeValidatorContract,
        sample_structured_pseudonymization_result: StructuredDataPseudonymizationResult,
    ) -> None:
        """Should handle empty entity types list."""
        # Arrange
        data = {"settings": {"theme": "dark", "language": "en"}}
        mock_entity_validator.validate_entity_types.return_value = []
        mock_data_pseudonymizer.pseudonymize.return_value = (
            sample_structured_pseudonymization_result
        )

        # Act
        result = mock_data_pseudonymization_service.pseudonymize(
            data=data,
            method=PseudonymizationMethod.RANDOM_NUMBER,
            language=SupportedLanguage.ENGLISH,
            entity_types=[],
        )

        # Assert
        assert result == sample_structured_pseudonymization_result
        mock_entity_validator.validate_entity_types.assert_called_once_with(
            entity_types=[],
        )

    @patch.object(
        PseudonymizationMethodFactory,
        "create",
        return_value=Mock(spec=PseudonymizationMethodContract),
    )
    def test_pseudonymize_data_with_no_pii_detected(
        self,
        mock_factory_create: Mock,
        mock_data_pseudonymization_service: StructuredDataPseudonymizationService,
        mock_data_pseudonymizer: StructuredDataPseudonymizerContract,
    ) -> None:
        """Should handle data with no PII entities detected."""
        # Arrange
        data = {"config": {"debug": True, "timeout": 30}}
        result_no_pii = StructuredDataPseudonymizationResult(
            pseudonymized_data=data,
            detected_fields=[],
        )
        mock_data_pseudonymizer.pseudonymize.return_value = result_no_pii

        # Act
        result = mock_data_pseudonymization_service.pseudonymize(
            data=data,
            method=PseudonymizationMethod.COUNTER,
            language=SupportedLanguage.ENGLISH,
            entity_types=[],
        )

        # Assert
        assert result == result_no_pii
        assert result.detected_fields == []


class TestStructuredDataPseudonymizationServiceInputValidation:
    """Test input validation scenarios."""

    @pytest.mark.parametrize(
        "invalid_data",
        [{}, None],
    )
    def test_pseudonymize_various_empty_data_raise_error(
        self,
        mock_data_pseudonymization_service: StructuredDataPseudonymizationService,
        invalid_data: dict | None,
    ) -> None:
        """Should raise InvalidInputDataError for various empty data."""
        with pytest.raises(InvalidInputDataError, match="Data cannot be empty"):
            mock_data_pseudonymization_service.pseudonymize(
                data=invalid_data,
                method=PseudonymizationMethod.RANDOM_NUMBER,
                language=SupportedLanguage.ENGLISH,
                entity_types=[],
            )


class TestStructuredDataPseudonymizationServiceErrorHandling:
    """Test error handling and exception chaining."""

    @patch.object(
        PseudonymizationMethodFactory,
        "create",
        side_effect=UnknownPseudonymizationMethodError(
            "Unsupported pseudonymization method",
        ),
    )
    def test_pseudonymize_when_factory_fails_chains_exception(
        self,
        mock_factory_create: Mock,
        mock_data_pseudonymization_service: StructuredDataPseudonymizationService,
        mock_data_pseudonymizer: StructuredDataPseudonymizerContract,
        mock_entity_validator: EntityTypeValidatorContract,
    ) -> None:
        """Should chain exception when method factory fails."""
        # Act & Assert
        with pytest.raises(
            StructuredDataPseudonymizationError,
            match="Pseudonymization method loading failed",
        ):
            mock_data_pseudonymization_service.pseudonymize(
                data={"name": "John"},
                method=PseudonymizationMethod.RANDOM_NUMBER,
                language=SupportedLanguage.ENGLISH,
                entity_types=[],
            )

        # Validator and pseudonymizer should not be called
        mock_entity_validator.validate_entity_types.assert_not_called()
        mock_data_pseudonymizer.pseudonymize.assert_not_called()

    @patch.object(
        PseudonymizationMethodFactory,
        "create",
        return_value=Mock(spec=PseudonymizationMethodContract),
    )
    def test_pseudonymize_when_validator_fails_chains_exception(
        self,
        mock_factory_create: Mock,
        mock_data_pseudonymization_service: StructuredDataPseudonymizationService,
        mock_entity_validator: EntityTypeValidatorContract,
    ) -> None:
        """Should chain exception when validator fails."""
        # Arrange
        mock_entity_validator.validate_entity_types.side_effect = (
            EntityTypeValidationError("Invalid entity type: UNKNOWN")
        )

        # Act & Assert
        with pytest.raises(EntityTypeValidationError):
            mock_data_pseudonymization_service.pseudonymize(
                data={"name": "John"},
                method=PseudonymizationMethod.RANDOM_NUMBER,
                language=SupportedLanguage.ENGLISH,
                entity_types=["UNKNOWN"],
            )

    @patch.object(
        PseudonymizationMethodFactory,
        "create",
        return_value=Mock(spec=PseudonymizationMethodContract),
    )
    def test_pseudonymize_when_pseudonymizer_fails_chains_exception(
        self,
        mock_factory_create: Mock,
        mock_data_pseudonymization_service: StructuredDataPseudonymizationService,
        mock_data_pseudonymizer: StructuredDataPseudonymizerContract,
    ) -> None:
        """Should chain exception when pseudonymizer fails."""
        # Arrange
        mock_data_pseudonymizer.pseudonymize.side_effect = (
            StructuredDataPseudonymizationError(
                "Pseudonymization failed",
            )
        )

        # Act & Assert
        with pytest.raises(StructuredDataPseudonymizationError):
            mock_data_pseudonymization_service.pseudonymize(
                data={"name": "John"},
                method=PseudonymizationMethod.RANDOM_NUMBER,
                language=SupportedLanguage.ENGLISH,
                entity_types=[],
            )


class TestStructuredDataPseudonymizationServiceEdgeCases:
    """Test edge cases and boundary conditions."""

    @patch.object(
        PseudonymizationMethodFactory,
        "create",
        return_value=Mock(spec=PseudonymizationMethodContract),
    )
    def test_pseudonymize_with_deeply_nested_data(
        self,
        mock_factory_create: Mock,
        mock_data_pseudonymization_service: StructuredDataPseudonymizationService,
        mock_data_pseudonymizer: StructuredDataPseudonymizerContract,
        sample_structured_pseudonymization_result: StructuredDataPseudonymizationResult,
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
        mock_data_pseudonymizer.pseudonymize.return_value = (
            sample_structured_pseudonymization_result
        )

        # Act
        result = mock_data_pseudonymization_service.pseudonymize(
            data=nested_data,
            method=PseudonymizationMethod.CRYPTO_HASH,
            language=SupportedLanguage.ENGLISH,
            entity_types=["PERSON", "EMAIL", "PHONE_NUMBER"],
        )

        # Assert
        assert result == sample_structured_pseudonymization_result
        mock_data_pseudonymizer.pseudonymize.assert_called_once()
