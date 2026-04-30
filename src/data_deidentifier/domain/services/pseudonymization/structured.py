from typing import Any

from logger import LoggerContract

from data_deidentifier.domain.contracts.enricher.manager import (
    PseudonymEnrichmentManagerContract,
)
from data_deidentifier.domain.contracts.pseudonymizer.structured import (
    StructuredDataPseudonymizerContract,
)
from data_deidentifier.domain.contracts.validator import EntityTypeValidatorContract
from data_deidentifier.domain.exceptions import (
    InvalidInputDataError,
    StructuredDataPseudonymizationError,
)
from data_deidentifier.domain.services.pseudonymization.methods.factory import (
    PseudonymizationMethodFactory,
)
from data_deidentifier.domain.types.language import SupportedLanguage
from data_deidentifier.domain.types.pseudonymization_method import (
    PseudonymizationMethod,
)
from data_deidentifier.domain.types.structured_data import StructuredData
from data_deidentifier.domain.types.structured_pseudonymization_result import (
    StructuredDataPseudonymizationResult,
)


class StructuredDataPseudonymizationService:
    """Service for pseudonymizing personally identifiable information in data.

    This service orchestrates the structured data pseudonymization process
    and produces structured pseudonymization results.
    """

    def __init__(
        self,
        pseudonymizer: StructuredDataPseudonymizerContract,
        validator: EntityTypeValidatorContract,
        logger: LoggerContract,
        pseudonym_enricher: PseudonymEnrichmentManagerContract | None = None,
    ) -> None:
        """Initialize the structured data pseudonymization service.

        Args:
            pseudonymizer: Implementation of the data pseudonymization contract
            validator: Implementation of the validator contract
            logger: Logger for logging events
            pseudonym_enricher: Optional enrichment service for adding contextual
                information to pseudonyms found in structured data
        """
        self.pseudonymizer = pseudonymizer
        self.validator = validator
        self.logger = logger
        self.pseudonym_enricher = pseudonym_enricher

    def pseudonymize(  # noqa: PLR0913
        self,
        data: StructuredData,
        method: PseudonymizationMethod,
        language: SupportedLanguage,
        min_score: float,
        entity_types: list[str],
        method_params: dict[str, Any] | None = None,
    ) -> StructuredDataPseudonymizationResult:
        """Pseudonymize PII entities in text.

        Args:
            data: The structured data to pseudonymize
            method: Pseudonymization method to use
            language: Language code of the text
            min_score: Minimum confidence score threshold
            entity_types: Entity types to detect
            method_params: Optional parameters for the method


        Returns:
            A StructuredDataPseudonymizationResult
            containing the pseudonymized data and metadata

        Raises:
            InvalidInputDataError: If the text is empty
            StructuredDataPseudonymizationError: If the method is unknown
        """
        if not data:
            raise InvalidInputDataError("Data cannot be empty")

        # Get the pseudonymization method
        try:
            method_instance = PseudonymizationMethodFactory.create(
                method=method,
                method_params=method_params or {},
                logger=self.logger,
            )
        except Exception as e:
            raise StructuredDataPseudonymizationError(
                "Pseudonymization method loading failed",
            ) from e

        # Validate data
        effective_entity_types = self.validator.validate_entity_types(
            entity_types=entity_types,
        )

        # Pseudonymize the text
        return self.pseudonymizer.pseudonymize(
            data=data,
            method=method_instance,
            entity_types=effective_entity_types,
            language=language,
            pseudonym_enricher=self.pseudonym_enricher,
            min_score=min_score,
        )
