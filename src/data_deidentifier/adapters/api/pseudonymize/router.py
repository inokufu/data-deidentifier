from typing import Annotated

from fastapi import APIRouter, Depends

from data_deidentifier.adapters.api.dependencies import (
    get_config,
    get_structured_data_pseudonymization_service,
    get_text_pseudonymization_service,
)
from data_deidentifier.adapters.infrastructure.config.contract import ConfigContract
from data_deidentifier.domain.services.pseudonymization.structured import (
    StructuredDataPseudonymizationService,
)
from data_deidentifier.domain.services.pseudonymization.text import (
    TextPseudonymizationService,
)

from .schemas import (
    PseudonymizeStructuredDataRequest,
    PseudonymizeStructuredDataResponse,
    PseudonymizeTextRequest,
    PseudonymizeTextResponse,
)

router = APIRouter(prefix="/pseudonymize")


@router.post(
    "/text",
    tags=["Text pseudonymization"],
    summary="Pseudonymize text content for PII entities",
    status_code=200,
)
async def pseudonymize_text(
    query: PseudonymizeTextRequest,
    pseudonymization_service: Annotated[
        TextPseudonymizationService,
        Depends(get_text_pseudonymization_service),
    ],
    config: Annotated[ConfigContract, Depends(get_config)],
) -> PseudonymizeTextResponse:
    """Pseudonymize PII entities in text content.

    Args:
        query: The request containing text to pseudonymize
        pseudonymization_service: The text pseudonymization instance
        config: The application configuration

    Returns:
        Pseudonymized text and information about the entities that were pseudonymized
    """
    effective_method = query.method or config.get_default_pseudonymization_method()
    effective_language = query.language or config.get_default_language()
    effective_min_score = (
        query.min_score
        if query.min_score is not None
        else config.get_default_minimum_score()
    )
    effective_entity_types = query.entity_types or config.get_default_entity_types()

    result = pseudonymization_service.pseudonymize(
        text=query.text,
        method=effective_method,
        method_params=query.method_params,
        language=effective_language,
        min_score=effective_min_score,
        entity_types=effective_entity_types,
    )

    return PseudonymizeTextResponse(
        pseudonymized_text=result.pseudonymized_text,
        detected_entities=result.detected_entities,
        meta={
            "method": effective_method,
            "language": effective_language,
            "min_score": effective_min_score,
        },
    )


@router.post(
    "/structured",
    tags=["Data pseudonymization"],
    summary="Pseudonymize structured data content for PII entities",
    status_code=200,
)
async def pseudonymize_structured(
    query: PseudonymizeStructuredDataRequest,
    pseudonymization_service: Annotated[
        StructuredDataPseudonymizationService,
        Depends(get_structured_data_pseudonymization_service),
    ],
    config: Annotated[ConfigContract, Depends(get_config)],
) -> PseudonymizeStructuredDataResponse:
    """Pseudonymize PII entities in structured data.

    Args:
        query: The request containing structured data to pseudonymize
        pseudonymization_service: The structured data pseudonymization instance
        config: The application configuration

    Returns:
        Pseudonymized structured data
        and information about fields that were pseudonymized
    """
    effective_method = query.method or config.get_default_pseudonymization_method()
    effective_language = query.language or config.get_default_language()
    effective_entity_types = query.entity_types or config.get_default_entity_types()

    result = pseudonymization_service.pseudonymize(
        data=query.data,
        method=effective_method,
        method_params=query.method_params,
        language=effective_language,
        entity_types=effective_entity_types,
    )

    return PseudonymizeStructuredDataResponse(
        pseudonymized_data=result.pseudonymized_data,
        detected_fields=result.field_mapping,
        meta={
            "method": effective_method,
            "language": effective_language,
        },
    )
