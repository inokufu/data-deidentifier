from dataclasses import dataclass


@dataclass
class StructuredAnalysisField:
    """Represents a field/column with detected PII entity information.

    This model captures information about a field or column in structured data
    that contains personally identifiable information (PII).

    Attributes:
        field_name: Name of the field/column (dot notation for nested JSON)
        entity_type: The type of PII entity detected in this field
    """

    field_name: str
    entity_type: str


@dataclass
class StructuredAnalysisResult:
    """Result of a structured data analysis operation.

    This class encapsulates information about PII entities detected
    in structured data fields/columns.

    Attributes:
        fields: List of fields with detected PII entities
        language: Language code used for the analysis
        entity_stats: Statistics of detected entity types and their counts
    """

    fields: list[StructuredAnalysisField]
    language: str | None = None
    entity_stats: dict[str, int] | None = None

    @property
    def entity_mapping(self) -> dict[str, str]:
        """Get entity mapping as a dictionary for convenience."""
        return {field.field_name: field.entity_type for field in self.fields}
