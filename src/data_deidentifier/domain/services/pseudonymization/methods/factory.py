from typing import Any, ClassVar

from logger import LoggerContract

from data_deidentifier.domain.contracts.pseudonymizer.method import (
    PseudonymizationMethodContract,
)
from data_deidentifier.domain.exceptions import TextPseudonymizationError
from data_deidentifier.domain.types.pseudonymization_method import (
    PseudonymizationMethod,
)

from .counter import CounterPseudonymizationMethod
from .crypto_hash import CryptoHashPseudonymizationMethod
from .random_number import RandomNumberPseudonymizationMethod


class PseudonymizationMethodFactory:
    """Factory for creating pseudonymization method instances."""

    # Mapping between method enums and implementation classes
    _METHOD_MAPPING: ClassVar[
        dict[PseudonymizationMethod, type[PseudonymizationMethodContract]]
    ] = {
        PseudonymizationMethod.RANDOM_NUMBER: RandomNumberPseudonymizationMethod,
        PseudonymizationMethod.COUNTER: CounterPseudonymizationMethod,
        PseudonymizationMethod.CRYPTO_HASH: CryptoHashPseudonymizationMethod,
    }

    @classmethod
    def create(
        cls,
        method: PseudonymizationMethod,
        method_params: dict[str, Any],
        logger: LoggerContract,
    ) -> PseudonymizationMethodContract:
        """Create a pseudonymization method instance.

        Args:
            method: The pseudonymization method enum
            method_params: Parameters for the pseudonymization method
            logger: Logger for logging events

        Returns:
            A method instance implementing PseudonymizationMethodContract

        Raises:
            TextPseudonymizationError: If method is not supported
        """
        if method not in cls._METHOD_MAPPING:
            raise TextPseudonymizationError(
                f"Unsupported pseudonymization method: {method}. "
                f"Supported methods: {cls.get_supported_methods()}",
            )

        method_class = cls._METHOD_MAPPING[method]
        return method_class(params=method_params, logger=logger)

    @classmethod
    def get_supported_methods(cls) -> list[PseudonymizationMethod]:
        """Get list of supported pseudonymization methods.

        Returns:
            List of supported methods
        """
        return list(cls._METHOD_MAPPING.keys())
