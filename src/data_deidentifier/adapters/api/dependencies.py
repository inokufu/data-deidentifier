from typing import Annotated

from fastapi import Depends, Request
from logger import LoggerContract

from data_deidentifier.adapters.infrastructure.config.contract import ConfigContract
from data_deidentifier.adapters.infrastructure.enrichment.factory import (
    EnrichmentFactory,
)
from data_deidentifier.adapters.presidio.anonymizer.structured import (
    PresidioStructuredDataAnonymizer,
)
from data_deidentifier.adapters.presidio.anonymizer.text import (
    PresidioTextAnonymizer,
)
from data_deidentifier.adapters.presidio.health_check import PresidioHealthChecker
from data_deidentifier.adapters.presidio.pseudonymizer.structured import (
    PresidioStructuredDataPseudonymizer,
)
from data_deidentifier.adapters.presidio.pseudonymizer.text import (
    PresidioTextPseudonymizer,
)
from data_deidentifier.adapters.presidio.validator import PresidioValidator
from data_deidentifier.domain.contracts.anonymizer.structured import (
    StructuredDataAnonymizerContract,
)
from data_deidentifier.domain.contracts.anonymizer.text import (
    TextAnonymizerContract,
)
from data_deidentifier.domain.contracts.enricher.manager import (
    PseudonymEnrichmentManagerContract,
)
from data_deidentifier.domain.contracts.health_check import HealthCheckContract
from data_deidentifier.domain.contracts.pseudonymizer.structured import (
    StructuredDataPseudonymizerContract,
)
from data_deidentifier.domain.contracts.pseudonymizer.text import (
    TextPseudonymizerContract,
)
from data_deidentifier.domain.contracts.validator import EntityTypeValidatorContract
from data_deidentifier.domain.services.anonymization.structured import (
    StructuredDataAnonymizationService,
)
from data_deidentifier.domain.services.anonymization.text import (
    TextAnonymizationService,
)
from data_deidentifier.domain.services.health_check.health_check import (
    HealthCheckService,
)
from data_deidentifier.domain.services.pseudonymization.structured import (
    StructuredDataPseudonymizationService,
)
from data_deidentifier.domain.services.pseudonymization.text import (
    TextPseudonymizationService,
)


async def get_config(request: Request) -> ConfigContract:
    """Get the application configuration from the request state.

    Args:
        request: The FastAPI request object

    Returns:
        The application configuration
    """
    return request.state.config


async def get_logger(request: Request) -> LoggerContract:
    """Get the logger from the request state.

    Args:
        request: The FastAPI request object

    Returns:
        The logger instance
    """
    return request.state.logger


async def get_text_anonymizer(
    logger: Annotated[LoggerContract, Depends(get_logger)],
) -> TextAnonymizerContract:
    """Create and return a text anonymizer instance.

    Args:
        logger: The logger instance

    Returns:
        An implementation of the text anonymizer contract
    """
    return PresidioTextAnonymizer(
        logger=logger,
    )


async def get_validator(
    logger: Annotated[LoggerContract, Depends(get_logger)],
) -> EntityTypeValidatorContract:
    """Create and return an entity type validator instance.

    Args:
        logger: The logger instance

    Returns:
        An implementation of the entity type validator contract
    """
    return PresidioValidator(
        logger=logger,
    )


async def get_structured_anonymizer(
    logger: Annotated[LoggerContract, Depends(get_logger)],
) -> StructuredDataAnonymizerContract:
    """Create and return a structured data anonymizer instance.

    Args:
        logger: The logger instance

    Returns:
        An implementation of the structured data anonymizer contract
    """
    return PresidioStructuredDataAnonymizer(
        logger=logger,
    )


async def get_pseudonym_enricher(
    config: Annotated[ConfigContract, Depends(get_config)],
    logger: Annotated[LoggerContract, Depends(get_logger)],
) -> PseudonymEnrichmentManagerContract | None:
    """Create and return a pseudonym enricher instance.

    Args:
        config: The application configuration containing enrichment settings
        logger: The logger instance

    Returns:
        An implementation of the enrichment manager contract.
    """
    enrichment_configs = config.get_enrichment_configurations()
    if not enrichment_configs:
        logger.warning("No configurations provided for entity enrichment")
        return None

    return EnrichmentFactory(
        config=config,
        logger=logger,
    )


async def get_text_pseudonymizer(
    config: Annotated[ConfigContract, Depends(get_config)],
    logger: Annotated[LoggerContract, Depends(get_logger)],
) -> TextPseudonymizerContract:
    """Create and return a text pseudonymizer instance.

    Args:
        config: The application configuration
        logger: The logger instance

    Returns:
        An implementation of the text pseudonymizer contract
    """
    return PresidioTextPseudonymizer(
        config=config,
        logger=logger,
    )


async def get_structured_pseudonymizer(
    config: Annotated[ConfigContract, Depends(get_config)],
    logger: Annotated[LoggerContract, Depends(get_logger)],
) -> StructuredDataPseudonymizerContract:
    """Create and return a structured data pseudonymizer instance.

    Args:
        config: The application configuration
        logger: The logger instance

    Returns:
        An implementation of the structured data pseudonymizer contract
    """
    return PresidioStructuredDataPseudonymizer(
        config=config,
        logger=logger,
    )


async def get_text_anonymization_service(
    anonymizer: Annotated[TextAnonymizerContract, Depends(get_text_anonymizer)],
    validator: Annotated[EntityTypeValidatorContract, Depends(get_validator)],
) -> TextAnonymizationService:
    """Create and return a text anonymization service instance.

    This dependency factory creates a fully configured text anonymization service
    with all necessary dependencies injected. The service orchestrates the text
    anonymization process by validating entity types and delegating to the
    appropriate anonymizer implementation.

    Args:
        anonymizer: The text anonymizer implementation to use for processing
        validator: The entity type validator for validating input parameters

    Returns:
        TextAnonymizationService: A configured service instance ready to
            anonymize PII entities in text content.
    """
    return TextAnonymizationService(
        anonymizer=anonymizer,
        validator=validator,
    )


async def get_structured_data_anonymization_service(
    anonymizer: Annotated[
        StructuredDataAnonymizerContract,
        Depends(get_structured_anonymizer),
    ],
    validator: Annotated[EntityTypeValidatorContract, Depends(get_validator)],
) -> StructuredDataAnonymizationService:
    """Create and return a structured data anonymization service instance.

    This dependency factory creates a fully configured structured data anonymization
    service with all necessary dependencies injected. The service orchestrates the
    anonymization process for structured data formats like JSON and DataFrames.

    Args:
        anonymizer: The structured data anonymizer implementation to use for processing
        validator: The entity type validator for validating input parameters

    Returns:
        StructuredDataAnonymizationService: A configured service instance ready to
            anonymize PII entities in structured data.
    """
    return StructuredDataAnonymizationService(
        anonymizer=anonymizer,
        validator=validator,
    )


async def get_text_pseudonymization_service(
    pseudonymizer: Annotated[
        TextPseudonymizerContract,
        Depends(get_text_pseudonymizer),
    ],
    validator: Annotated[EntityTypeValidatorContract, Depends(get_validator)],
    logger: Annotated[LoggerContract, Depends(get_logger)],
    pseudonym_enricher: Annotated[
        PseudonymEnrichmentManagerContract | None,
        Depends(get_pseudonym_enricher),
    ],
) -> TextPseudonymizationService:
    """Create and return a text pseudonymization service instance.

    This dependency factory creates a fully configured text pseudonymization service
    with all necessary dependencies injected. The service orchestrates the text
    pseudonymization process, including optional pseudonym enrichment for enhanced
    utility while maintaining privacy.

    Args:
        pseudonymizer: The text pseudonymizer implementation to use for processing
        validator: The entity type validator for validating input parameters
        logger: The logger instance for recording service operations
        pseudonym_enricher: Optional pseudonym enricher
            for adding contextual information to pseudonymized entities

    Returns:
        TextPseudonymizationService: A configured service instance ready to
            pseudonymize PII entities in text content with optional enrichment.
    """
    return TextPseudonymizationService(
        pseudonymizer=pseudonymizer,
        validator=validator,
        logger=logger,
        pseudonym_enricher=pseudonym_enricher,
    )


async def get_structured_data_pseudonymization_service(
    pseudonymizer: Annotated[
        StructuredDataPseudonymizerContract,
        Depends(get_structured_pseudonymizer),
    ],
    validator: Annotated[EntityTypeValidatorContract, Depends(get_validator)],
    logger: Annotated[LoggerContract, Depends(get_logger)],
    pseudonym_enricher: Annotated[
        PseudonymEnrichmentManagerContract | None,
        Depends(get_pseudonym_enricher),
    ],
) -> StructuredDataPseudonymizationService:
    """Create and return a structured data pseudonymization service instance.

    This dependency factory creates a fully configured structured data pseudonymization
    service with all necessary dependencies injected. The service orchestrates the
    pseudonymization process for structured data formats with optional entity
    enrichment capabilities.

    Args:
        pseudonymizer: The data pseudonymizer implementation to use for processing
        validator: The entity type validator for validating input parameters
        logger: The logger instance for recording service operations
        pseudonym_enricher: Optional entity enricher for adding contextual information
            to pseudonymized entities

    Returns:
        StructuredDataPseudonymizationService: A configured service instance ready to
            pseudonymize PII entities in structured data with optional enrichment.
    """
    return StructuredDataPseudonymizationService(
        pseudonymizer=pseudonymizer,
        validator=validator,
        logger=logger,
        pseudonym_enricher=pseudonym_enricher,
    )


async def get_health_checker(
    logger: Annotated[LoggerContract, Depends(get_logger)],
) -> HealthCheckContract:
    """Create and return a health checker instance.

    Args:
        logger: The logger instance

    Returns:
        An implementation of the health check contract
    """
    return PresidioHealthChecker(logger=logger)


async def get_health_check_service(
    health_checker: Annotated[
        HealthCheckContract,
        Depends(get_health_checker),
    ],
    config: Annotated[ConfigContract, Depends(get_config)],
    logger: Annotated[LoggerContract, Depends(get_logger)],
) -> HealthCheckService:
    """Create and return a health check service instance.

    Args:
        health_checker: The health checker
        config: The application configuration
        logger: The logger instance

    Returns:
        A configured health check service
    """
    return HealthCheckService(
        health_checker=health_checker,
        config=config,
        logger=logger,
    )
