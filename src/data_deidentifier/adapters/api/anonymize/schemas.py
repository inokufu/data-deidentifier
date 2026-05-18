from typing import Any

from pydantic import BaseModel, Field

from data_deidentifier.domain.types.anonymization_operator import (
    AnonymizationOperator,
)
from data_deidentifier.domain.types.entity import Entity
from data_deidentifier.domain.types.language import SupportedLanguage
from data_deidentifier.domain.types.structured_data import StructuredData


class AnonymizeTextRequest(BaseModel):
    """Request model for anonymizing text.

    This model defines the input parameters for the text anonymization endpoint.
    """

    text: str = Field(..., description="The text content to anonymize")

    operator: AnonymizationOperator | None = Field(
        default=None,
        description="Anonymization method",
    )

    operator_params: dict[str, Any] | None = Field(
        default=None,
        description="Anonymization operator parameters",
    )

    language: SupportedLanguage | None = Field(
        default=None,
        description="Language code of the text (e.g., 'en', 'fr', 'es')",
    )

    min_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score threshold (0.0 to 1.0)",
    )

    entity_types: list[str] | None = Field(
        default=None,
        description="Types of entities to detect (defaults to all supported types)",
    )


class AnonymizeTextResponse(BaseModel):
    """Response model for text anonymization.

    This model defines the structure of the response
    returned by the text anonymization endpoint.
    """

    anonymized_text: str = Field(..., description="The anonymized text content")

    detected_entities: list[Entity] = Field(
        ...,
        description="List of detected PII entities",
    )

    meta: dict[str, Any] | None = Field(
        default_factory=dict,
        description="Statistics about the anonymization operation",
    )


class AnonymizeStructuredDataRequest(BaseModel):
    """Request model for anonymizing structured data.

    This model defines the input parameters
    for the structured data anonymization endpoint.
    """

    data: StructuredData = Field(..., description="The structured data to anonymize")

    operator: AnonymizationOperator | None = Field(
        default=None,
        description="Anonymization method",
    )

    operator_params: dict[str, Any] | None = Field(
        default=None,
        description="Anonymization operator parameters",
    )

    language: SupportedLanguage | None = Field(
        default=None,
        description="Language code of the data (e.g., 'en', 'fr', 'es')",
    )

    min_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score threshold (0.0 to 1.0)",
    )

    entity_types: list[str] | None = Field(
        default=None,
        description="Types of entities to detect (defaults to all supported types)",
    )


class AnonymizeStructuredDataResponse(BaseModel):
    """Response model for structured data anonymization.

    This model defines the structure of the response returned
    by the structured data anonymization endpoint.
    """

    anonymized_data: StructuredData = Field(
        ...,
        description="The anonymized structured data",
    )

    detected_fields: dict[str, str] = Field(
        ...,
        description="List of detected fields",
    )

    meta: dict[str, Any] | None = Field(
        default_factory=dict,
        description="Statistics about the anonymization operation",
    )
