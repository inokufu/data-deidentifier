from abc import ABC, abstractmethod
from typing import Any

from configcore import ConfigContract as CoreConfigContract

from data_deidentifier.domain.types.anonymization_operator import (
    AnonymizationOperator,
)
from data_deidentifier.domain.types.language import SupportedLanguage
from data_deidentifier.domain.types.pseudonymization_method import (
    PseudonymizationMethod,
)


class ConfigContract(CoreConfigContract, ABC):
    """Contract for application configuration."""

    @abstractmethod
    def get_default_language(self) -> SupportedLanguage:
        """Get the default language for text analysis.

        Returns:
            The default language code (e.g., 'en', 'fr')
        """
        raise NotImplementedError

    @abstractmethod
    def get_default_minimum_score(self) -> float:
        """Get the default minimum confidence score for entity detection.

        Returns:
            The default minimum score as a float between 0.0 and 1.0
        """
        raise NotImplementedError

    @abstractmethod
    def get_default_entity_types(self) -> list[str]:
        """Get the default entity types to detect.

        Returns:
            List of default entity types for text analysis.
        """
        raise NotImplementedError

    @abstractmethod
    def get_default_anonymization_operator(self) -> AnonymizationOperator:
        """Get the default anonymization operator.

        Returns:
            The default anonymization operator
        """
        raise NotImplementedError

    @abstractmethod
    def get_default_pseudonymization_method(self) -> PseudonymizationMethod:
        """Get the default pseudonymization method.

        Returns:
            The default pseudonymization method
        """
        raise NotImplementedError

    @abstractmethod
    def get_enrichment_configurations(self) -> dict[str, dict[str, Any]]:
        """Get the enrichment configurations for entity types.

        Returns:
            dict[str, dict[str, Any]]: A mapping of entity types to their
                enrichment configurations. Keys are entity types (e.g., 'LOCATION')
                and values are configuration dictionaries containing enricher
                type and type-specific parameters.

        Examples:
            {
                "LOCATION": {
                    "type": "http",
                    "url": "http://geo-service/enrich",
                }
            }
        """
        raise NotImplementedError
