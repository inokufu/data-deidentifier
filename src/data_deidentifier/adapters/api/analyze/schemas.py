from typing import Any

from pydantic import BaseModel, Field

from src.data_deidentifier.adapters.api.response import (
    EntityResponse,
    StructuredFieldResponse,
)


class AnalyzeTextRequest(BaseModel):
    """Request model for analyzing text.

    This model defines the input parameters for the text analysis endpoint.
    """

    text: str = Field(..., description="The text content to analyze")

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


class AnalyzeTextResponse(BaseModel):
    """Response model for text analysis.

    This model defines the structure of the response
    returned by the text analysis endpoint.
    """

    entities: list[EntityResponse] = Field(
        ...,
        description="The entities found in the content",
    )

    meta: dict[str, Any] | None = Field(
        default_factory=dict,
        description="Statistics about the analysis",
    )


class AnalyzeStructuredDataRequest(BaseModel):
    """Request model for analyzing structured data.

    This model defines the input parameters for the structured data analysis endpoint.
    """

    data: Any = Field(..., description="The structured data to analyze")

    language: str | None = Field(
        default=None,
        description="Language code of the text (e.g., 'en', 'fr', 'es')",
    )

    entity_types: list[str] | None = Field(
        default=None,
        description="Types of entities to detect (defaults to all supported types)",
    )


class AnalyzeStructuredDataResponse(BaseModel):
    """Response model for structured data analysis.

    This model defines the structure of the response
    returned by the structured data analysis endpoint.
    """

    fields: list[StructuredFieldResponse] = Field(
        ...,
        description="List of fields with detected PII entities",
    )

    meta: dict[str, Any] | None = Field(
        default_factory=dict,
        description="Statistics about the analysis",
    )
