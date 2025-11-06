import pytest
from logger import LoggerContract

from src.data_deidentifier.domain.contracts.pseudonymizer.method import (
    PseudonymizationMethodContract,
)
from src.data_deidentifier.domain.exceptions import UnknownPseudonymizationMethodError
from src.data_deidentifier.domain.services.pseudonymization.methods.counter import (
    CounterPseudonymizationMethod,
)
from src.data_deidentifier.domain.services.pseudonymization.methods.crypto_hash import (
    CryptoHashPseudonymizationMethod,
)
from src.data_deidentifier.domain.services.pseudonymization.methods.factory import (
    PseudonymizationMethodFactory,
)
from src.data_deidentifier.domain.services.pseudonymization.methods.random_number import (  # noqa: E501
    RandomNumberPseudonymizationMethod,
)
from src.data_deidentifier.domain.types.pseudonymization_method import (
    PseudonymizationMethod,
)


class TestPseudonymizationMethodFactoryCreation:
    """Test successful method creation scenarios."""

    @pytest.mark.parametrize(
        ("method", "expected_class"),
        [
            (PseudonymizationMethod.RANDOM_NUMBER, RandomNumberPseudonymizationMethod),
            (PseudonymizationMethod.COUNTER, CounterPseudonymizationMethod),
            (PseudonymizationMethod.CRYPTO_HASH, CryptoHashPseudonymizationMethod),
        ],
    )
    def test_create_all_supported_methods(
        self,
        method: PseudonymizationMethod,
        expected_class: type,
        mock_logger: LoggerContract,
    ) -> None:
        """Should create instances of the correct class for each method."""
        # Act
        result = PseudonymizationMethodFactory.create(
            method=method,
            method_params={"test": "param"},
            logger=mock_logger,
        )

        # Assert
        assert isinstance(result, expected_class)
        assert isinstance(result, PseudonymizationMethodContract)

    def test_create_with_empty_params(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should create method with empty parameters."""
        # Act
        result = PseudonymizationMethodFactory.create(
            method=PseudonymizationMethod.RANDOM_NUMBER,
            method_params={},
            logger=mock_logger,
        )

        # Assert
        assert isinstance(result, RandomNumberPseudonymizationMethod)
        assert isinstance(result, PseudonymizationMethodContract)


class TestPseudonymizationMethodFactoryErrorHandling:
    """Test error handling scenarios."""

    def test_create_with_unsupported_method_raises_error(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should raise UnknownPseudonymizationMethodError for unsupported method."""
        # Arrange
        fake_method = "UNSUPPORTED_METHOD"

        # Act & Assert
        with pytest.raises(
            UnknownPseudonymizationMethodError,
            match=f"Unsupported pseudonymization method: {fake_method}",
        ):
            PseudonymizationMethodFactory.create(
                method=fake_method,  # type: ignore[arg-type]
                method_params={},
                logger=mock_logger,
            )

    def test_create_when_method_constructor_fails(
        self,
        mock_logger: LoggerContract,
    ) -> None:
        """Should propagate exception when method constructor fails."""
        # Act & Assert
        with pytest.raises(ValueError, match="start_number must be positive"):
            PseudonymizationMethodFactory.create(
                method=PseudonymizationMethod.COUNTER,
                method_params={"start_number": -1},  # Invalid parameter
                logger=mock_logger,
            )


class TestPseudonymizationMethodFactorySupportedMethods:
    """Test supported methods functionality."""

    def test_get_supported_methods_returns_all_methods(self) -> None:
        """Should return all methods defined in the mapping."""
        # Act
        supported_methods = PseudonymizationMethodFactory.get_supported_methods()

        # Assert
        expected_methods = [
            PseudonymizationMethod.RANDOM_NUMBER,
            PseudonymizationMethod.COUNTER,
            PseudonymizationMethod.CRYPTO_HASH,
        ]

        assert isinstance(supported_methods, list)
        assert supported_methods == expected_methods
