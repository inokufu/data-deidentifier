from dataclasses import dataclass

from .structured_data import StructuredData


@dataclass
class StructuredDataAnonymizationResult:
    """Result of a structured data anonymization operation.

    This class encapsulates all information about a structured data
    anonymization operation, including the anonymized data and metadata.

    Attributes:
        anonymized_data: The structured data after anonymization
        operator: The anonymization operator used
        entity_stats: Statistics of anonymized entity types and their counts
    """

    anonymized_data: StructuredData
    operator: str
    entity_stats: dict[str, int] | None = None
