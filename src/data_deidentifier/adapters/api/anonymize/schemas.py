from typing import Any

from pydantic import BaseModel, Field

from src.data_deidentifier.adapters.api.response import (
    EntityResponse,
    StructuredFieldResponse,
)
from src.data_deidentifier.domain.types.operators import AnonymizationOperator
from src.data_deidentifier.domain.types.structured_data import StructuredData


class AnonymizeTextRequest(BaseModel):
    """Request model for anonymizing text.

    This model defines the input parameters for the text anonymization endpoint.
    """

    text: str = Field(..., description="The text content to anonymize")

    entities: list[EntityResponse] | None = Field(
        default_factory=list,
        description="Pre-identified entities (if empty, text will be analyzed first)",
    )

    operator: AnonymizationOperator | None = Field(
        default=None,
        description="Anonymization method",
    )

    language: str | None = Field(
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

    meta: dict[str, Any] | None = Field(
        default_factory=dict,
        description="Statistics about anonymized entity types",
    )


class AnonymizeStructuredDataRequest(BaseModel):
    """Request model for anonymizing structured data.

    This model defines the input parameters
    for the structured data anonymization endpoint.
    """

    data: StructuredData = Field(..., description="The structured data to anonymize")

    fields: list[StructuredFieldResponse] | None = Field(
        default=None,
        description="Pre-identified fields (if empty, text will be analyzed first)",
    )

    operator: AnonymizationOperator | None = Field(
        default=None,
        description="Anonymization method",
    )

    language: str | None = Field(
        default=None,
        description="Language code of the data (e.g., 'en', 'fr', 'es')",
    )

    entity_types: list[str] | None = Field(
        default=None,
        description="Types of entities to detect (defaults to all supported types)",
    )


class AnonymizeStructuredDataResponse(BaseModel):
    """Response model for structured data anonymization.

    This model defines the structure of the response
    returned by the structured data anonymization endpoint.
    """

    anonymized_data: StructuredData = Field(
        ...,
        description="The anonymized structured data",
    )

    meta: dict[str, Any] | None = Field(
        default_factory=dict,
        description="Statistics about the anonymization operation",
    )
