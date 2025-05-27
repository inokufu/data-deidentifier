from pydantic import BaseModel, Field


class EntityResponse(BaseModel):
    """Response model for an entity found in the content.

    This model represents a PII entity detected in the analyzed text content.
    """

    type: str = Field(..., description="The type of PII entity detected")
    start: int = Field(
        ...,
        ge=0,
        description="The start position of the entity in the content",
    )
    end: int = Field(
        ...,
        ge=0,
        description="The end position of the entity in the content",
    )
    score: float = Field(
        ...,
        ge=0.0,
        description="The confidence score of the detection",
    )
    text: str | None = Field(default=None, description="The text of the entity")
    path: str | None = Field(
        None,
        description="The path to the field containing the entity (for JSON data)",
    )


class StructuredFieldResponse(BaseModel):
    """Response model for a structured data field containing PII.

    This model represents a field/column in structured data that contains PII.
    """

    field_name: str = Field(
        ...,
        description="Name of the field/column (dot notation for nested JSON)",
    )
    entity_type: str = Field(
        ...,
        description="The type of PII entity detected in this field",
    )
