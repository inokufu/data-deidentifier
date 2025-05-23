from typing import Annotated

from fastapi import APIRouter, Depends

from src.data_deidentifier.adapters.api.dependencies import (
    get_config,
    get_structured_analyzer,
    get_text_analyzer,
    get_validator,
)
from src.data_deidentifier.adapters.api.mapper import ApiEntityMapper
from src.data_deidentifier.adapters.infrastructure.config.contract import ConfigContract
from src.data_deidentifier.domain.contracts.analyzer.structured import (
    StructuredAnalyzerContract,
)
from src.data_deidentifier.domain.contracts.analyzer.text import TextAnalyzerContract
from src.data_deidentifier.domain.contracts.validator import EntityTypeValidatorContract
from src.data_deidentifier.domain.services.analyze.structured import (
    StructuredAnalysisService,
)
from src.data_deidentifier.domain.services.analyze.text import TextAnalysisService

from .schemas import (
    AnalyzeStructuredDataRequest,
    AnalyzeStructuredDataResponse,
    AnalyzeTextRequest,
    AnalyzeTextResponse,
)

router = APIRouter(prefix="/analyze")


@router.post(
    "/text",
    tags=["Data anonymization"],
    summary="Analyze text for PII entities",
    status_code=200,
)
async def analyze_text(
    query: AnalyzeTextRequest,
    analyzer: Annotated[TextAnalyzerContract, Depends(get_text_analyzer)],
    validator: Annotated[EntityTypeValidatorContract, Depends(get_validator)],
    config: Annotated[ConfigContract, Depends(get_config)],
) -> AnalyzeTextResponse:
    """Analyze text content for PII entities.

    This endpoint analyzes the provided text to detect personally identifiable
    information (PII) entities such as names, email addresses, phone numbers, etc.

    Args:
        query: The request query model containing the text to analyze
        analyzer: The text analyzer implementation
        validator: The validator implementation
        config: The application configuration

    Returns:
        Analysis results containing the detected entities and statistics
    """
    service = TextAnalysisService(
        analyzer=analyzer,
        validator=validator,
        default_language=config.get_default_language(),
        default_min_score=config.get_default_minimum_score(),
        default_entity_types=config.get_default_entity_types(),
    )

    analysis_result = service.analyze(
        text=query.text,
        language=query.language,
        min_score=query.min_score,
        entity_types=query.entity_types,
    )

    entities = [
        ApiEntityMapper.domain_to_adapter(entity=e) for e in analysis_result.entities
    ]

    return AnalyzeTextResponse(
        entities=entities,
        meta={
            "language": analysis_result.language,
            "min_score": analysis_result.min_score,
            "entities": analysis_result.entity_stats,
        },
    )


@router.post(
    "/structured",
    tags=["Structured data anonymization"],
    summary="Analyze structured data for PII entities",
    status_code=200,
)
async def analyze_structured(
    query: AnalyzeStructuredDataRequest,
    analyzer: Annotated[StructuredAnalyzerContract, Depends(get_structured_analyzer)],
    validator: Annotated[EntityTypeValidatorContract, Depends(get_validator)],
    config: Annotated[ConfigContract, Depends(get_config)],
) -> AnalyzeStructuredDataResponse:
    """Analyze structured data for PII entities.

    This endpoint analyzes the structured data to detect personally identifiable
    information (PII) entities such as names, email addresses, phone numbers, etc.

    Args:
        query: The request query model containing the structured data to analyze
        analyzer: The structured analyzer implementation
        validator: The validator implementation
        config: The application configuration

    Returns:
        Analysis results containing the entity mapping and statistics
    """
    service = StructuredAnalysisService(
        analyzer=analyzer,
        validator=validator,
        default_language=config.get_default_language(),
        default_entity_types=config.get_default_entity_types(),
    )

    analysis_result = service.analyze(
        data=query.data,
        language=query.language,
        entity_types=query.entity_types,
    )

    return AnalyzeStructuredDataResponse(
        entities=analysis_result.entity_mapping,
        meta={
            "language": analysis_result.language,
            "entity_types": analysis_result.entity_stats,
        },
    )
