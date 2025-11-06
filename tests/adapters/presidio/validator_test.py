from unittest.mock import Mock, patch

import pytest
from logger import LoggerContract

from src.data_deidentifier.adapters.presidio.engines import PresidioEngineFactory
from src.data_deidentifier.adapters.presidio.validator import PresidioValidator
from src.data_deidentifier.domain.exceptions import EntityTypeValidationError


@patch.object(PresidioEngineFactory, "get_analyzer_engine")
class TestPresidioValidatorInitialization:
    """Test validator initialization."""

    def test_init_creates_analyzer_engine(
        self,
        mock_analyzer_engine: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should call factory and store logger."""
        # Arrange
        mock_analyzer = Mock()
        mock_analyzer_engine.return_value = mock_analyzer

        # Act
        presidio_validator = PresidioValidator(logger=mock_logger)

        # Assert
        assert presidio_validator.logger == mock_logger
        mock_analyzer_engine.assert_called_once()


@patch.object(PresidioEngineFactory, "get_analyzer_engine")
class TestPresidioValidatorSupportedEntities:
    """Test supported entities property and lazy loading."""

    def test_supported_entities_lazy_loading_first_call(
        self,
        mock_analyzer_engine: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should load supported entities on first access."""
        # Arrange
        mock_analyzer = Mock()
        mock_analyzer_engine.return_value = mock_analyzer

        supported_entities = ["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER"]
        mock_analyzer.get_supported_entities.return_value = supported_entities

        presidio_validator = PresidioValidator(logger=mock_logger)

        # Act
        result = presidio_validator.supported_entities

        # Assert
        expected = set(supported_entities)
        assert result == expected
        mock_analyzer.get_supported_entities.assert_called_once()

    def test_supported_entities_caching_subsequent_calls(
        self,
        mock_analyzer_engine: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should use cached value on subsequent calls."""
        # Arrange
        mock_analyzer = Mock()
        mock_analyzer_engine.return_value = mock_analyzer

        supported_entities = ["PERSON", "EMAIL_ADDRESS"]
        mock_analyzer.get_supported_entities.return_value = supported_entities

        presidio_validator = PresidioValidator(logger=mock_logger)

        # Act - Multiple calls
        result1 = presidio_validator.supported_entities
        result2 = presidio_validator.supported_entities

        # Assert
        expected = set(supported_entities)
        assert result1 == result2 == expected
        # Should only call analyzer once (caching works)
        mock_analyzer.get_supported_entities.assert_called_once()


@patch.object(PresidioEngineFactory, "get_analyzer_engine")
class TestPresidioValidatorValidateEntityTypes:
    """Test entity types validation logic."""

    def test_validate_empty_list_returns_empty(
        self,
        mock_analyzer_engine: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should return empty list for empty input."""
        # Arrange
        mock_analyzer = Mock()
        mock_analyzer_engine.return_value = mock_analyzer

        presidio_validator = PresidioValidator(logger=mock_logger)

        # Act
        result = presidio_validator.validate_entity_types(entity_types=[])

        # Assert
        assert result == []
        # Should not call get_supported_entities (short-circuit)
        mock_analyzer.get_supported_entities.assert_not_called()

    def test_validate_supported_types_success(
        self,
        mock_analyzer_engine: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should validate and normalize supported entity types."""
        # Arrange
        mock_analyzer = Mock()
        mock_analyzer_engine.return_value = mock_analyzer

        supported_entities = ["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER"]
        mock_analyzer.get_supported_entities.return_value = supported_entities

        presidio_validator = PresidioValidator(logger=mock_logger)

        # Act
        result = presidio_validator.validate_entity_types(
            entity_types=["person", "EMAIL_ADDRESS", "Phone_Number"],
        )

        # Assert
        assert set(result) == set(
            supported_entities,
        )  # Order might vary since we use set internally

    def test_validate_mixed_case_normalization(
        self,
        mock_analyzer_engine: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should normalize entity types to uppercase."""
        # Arrange
        mock_analyzer = Mock()
        mock_analyzer_engine.return_value = mock_analyzer

        supported_entities = ["PERSON", "EMAIL_ADDRESS"]
        mock_analyzer.get_supported_entities.return_value = supported_entities

        presidio_validator = PresidioValidator(logger=mock_logger)

        # Act
        result = presidio_validator.validate_entity_types(
            entity_types=["person", "EMAIL_ADDRESS", "PERSON"],
        )

        # Assert
        # Should deduplicate and normalize
        assert set(result) == set(supported_entities)

    def test_validate_unsupported_types_raises_error(
        self,
        mock_analyzer_engine: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should raise EntityTypeValidationError for unsupported types."""
        # Arrange
        mock_analyzer = Mock()
        mock_analyzer.get_supported_entities.return_value = ["PERSON", "EMAIL_ADDRESS"]
        mock_analyzer_engine.return_value = mock_analyzer

        presidio_validator = PresidioValidator(logger=mock_logger)

        # Act & Assert
        with pytest.raises(
            EntityTypeValidationError,
            match="Unsupported entity types",
        ):
            presidio_validator.validate_entity_types(
                entity_types=["PERSON", "UNKNOWN", "INVALID"],
            )

        mock_logger.warning.assert_called_once()


@patch.object(PresidioEngineFactory, "get_analyzer_engine")
class TestPresidioValidatorEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_supported_entities_empty_from_analyzer(
        self,
        mock_analyzer_engine: Mock,
        mock_logger: LoggerContract,
    ) -> None:
        """Should handle empty supported entities from analyzer."""
        # Arrange
        mock_analyzer = Mock()
        mock_analyzer.get_supported_entities.return_value = []
        mock_analyzer_engine.return_value = mock_analyzer

        presidio_validator = PresidioValidator(logger=mock_logger)

        # Act
        supported = presidio_validator.supported_entities

        # Assert
        assert supported == set()

        # All types should be unsupported
        with pytest.raises(EntityTypeValidationError):
            presidio_validator.validate_entity_types(entity_types=["PERSON"])
