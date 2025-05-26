from typing import Annotated

from fastapi import APIRouter, Depends
from logger import LoggerContract

from src.data_deidentifier.adapters.api.dependencies import (
    get_config,
    get_logger,
    get_structured_analyzer,
    get_structured_anonymizer,
    get_text_analyzer,
    get_text_anonymizer,
    get_validator,
)
from src.data_deidentifier.adapters.api.mapper import ApiEntityMapper
from src.data_deidentifier.adapters.infrastructure.config.contract import ConfigContract
from src.data_deidentifier.domain.contracts.anonymizer.structured import (
    StructuredDataAnonymizerContract,
)
from src.data_deidentifier.domain.contracts.anonymizer.text import (
    TextAnonymizerContract,
)
from src.data_deidentifier.domain.contracts.validator import EntityTypeValidatorContract
from src.data_deidentifier.domain.services.analyze.structured import (
    StructuredDataAnalysisService,
)
from src.data_deidentifier.domain.services.analyze.text import TextAnalysisService
from src.data_deidentifier.domain.services.anonymize.structured import (
    StructuredDataAnonymizationService,
)
from src.data_deidentifier.domain.services.anonymize.text import (
    TextAnonymizationService,
)
from src.data_deidentifier.domain.types.structured_analysis_result import (
    StructuredDataAnalysisField,
)

from .schemas import (
    AnonymizeStructuredDataRequest,
    AnonymizeStructuredDataResponse,
    AnonymizeTextRequest,
    AnonymizeTextResponse,
)

router = APIRouter(prefix="/anonymize")


@router.post(
    "/text",
    tags=["Data anonymization"],
    summary="Anonymize text content for PII entities",
    status_code=200,
)
async def anonymize_text(
    query: AnonymizeTextRequest,
    anonymizer: Annotated[TextAnonymizerContract, Depends(get_text_anonymizer)],
    validator: Annotated[EntityTypeValidatorContract, Depends(get_validator)],
    config: Annotated[ConfigContract, Depends(get_config)],
    logger: Annotated[LoggerContract, Depends(get_logger)],
) -> AnonymizeTextResponse:
    """Anonymize PII entities in text content.

    If entities are not provided, the text will be analyzed first to detect them.

    Args:
        query: The request containing text to anonymize
        anonymizer: The text anonymizer implementation
        validator: The validator implementation
        config: The application configuration
        logger: The logger instance

    Returns:
        Anonymized text and information about the entities that were anonymized
    """
    anonymize_service = TextAnonymizationService(
        anonymizer=anonymizer,
        validator=validator,
        default_operator=config.get_default_anonymization_operator(),
    )

    text = query.text

    if query.entities:
        # Convert provided API entities to domain entities
        entities = [
            ApiEntityMapper.adapter_to_domain(entity_response=e) for e in query.entities
        ]
    else:
        # Retrieve entities via analyze service
        analyze_service = TextAnalysisService(
            analyzer=await get_text_analyzer(logger=logger),
            validator=validator,
            default_language=config.get_default_language(),
            default_min_score=config.get_default_minimum_score(),
            default_entity_types=config.get_default_entity_types(),
        )

        analysis_result = analyze_service.analyze(
            text=query.text,
            language=query.language,
            min_score=query.min_score,
            entity_types=query.entity_types,
        )

        entities = analysis_result.entities

    # Anonymize the text
    result = anonymize_service.anonymize(
        text=text,
        entities=entities,
        operator=query.operator,
    )

    return AnonymizeTextResponse(
        anonymized_text=result.anonymized_text,
        meta={
            "operator": result.operator,
            "entities": result.entity_stats,
        },
    )


@router.post(
    "/structured",
    tags=["Structured data anonymization"],
    summary="Anonymize structured data for PII entities",
    status_code=200,
)
async def anonymize_structured(
    query: AnonymizeStructuredDataRequest,
    anonymizer: Annotated[
        StructuredDataAnonymizerContract,
        Depends(get_structured_anonymizer),
    ],
    validator: Annotated[EntityTypeValidatorContract, Depends(get_validator)],
    config: Annotated[ConfigContract, Depends(get_config)],
    logger: Annotated[LoggerContract, Depends(get_logger)],
) -> AnonymizeStructuredDataResponse:
    """Anonymize PII entities in structured data.

    If entity mapping is not provided, the data will be analyzed first to detect it.

    Args:
        query: The request containing structured data to anonymize
        anonymizer: The structured data anonymizer implementation
        validator: The validator implementation
        config: The application configuration
        logger: The logger instance

    Returns:
        Anonymized structured data
        and information about the entities that were anonymized
    """
    anonymize_service = StructuredDataAnonymizationService(
        anonymizer=anonymizer,
        validator=validator,
        default_operator=config.get_default_anonymization_operator(),
    )

    data = query.data

    if query.entities:
        # Use provided entity mapping to create fields
        fields = [
            StructuredDataAnalysisField(
                field_name=field_name,
                entity_type=entity_type,
            )
            for field_name, entity_type in query.entities.items()
        ]
    else:
        # Retrieve fields via analyze service
        analyze_service = StructuredDataAnalysisService(
            analyzer=await get_structured_analyzer(logger=logger),
            validator=validator,
            default_language=config.get_default_language(),
            default_entity_types=config.get_default_entity_types(),
        )

        analysis_result = analyze_service.analyze(
            data=data,
            language=query.language,
            entity_types=query.entity_types,
        )

        fields = analysis_result.fields

    # Anonymize the data
    result = anonymize_service.anonymize(
        data=data,
        fields=fields,
        operator=query.operator,
    )

    return AnonymizeStructuredDataResponse(
        anonymized_data=result.anonymized_data,
        meta={
            "operator": result.operator,
            "entities": result.entity_stats,
        },
    )
