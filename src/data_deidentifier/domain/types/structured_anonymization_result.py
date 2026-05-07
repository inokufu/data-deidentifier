from dataclasses import dataclass

from .structured_data import StructuredData


@dataclass
class StructuredDataAnalysisField:
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
class StructuredDataAnonymizationResult:
    """Result of a structured data anonymization operation.

    This class encapsulates all information about a structured data
    anonymization operation, including the anonymized data and metadata.

    Attributes:
        anonymized_data: The structured data after anonymization
        detected_fields: List of fields with detected PII entities
    """

    anonymized_data: StructuredData
    detected_fields: list[StructuredDataAnalysisField]

    @property
    def field_mapping(self) -> dict[str, str]:
        """Get field mapping as a dictionary for convenience."""
        mapping: dict[str, list[str]] = {}
        for field in self.detected_fields:
            mapping.setdefault(field.field_name, []).append(field.entity_type)
        return {name: ", ".join(types) for name, types in mapping.items()}
