class DataDeidentifierError(Exception):
    """Base class for all exceptions in data-deidentifier."""


class AnonymizationError(DataDeidentifierError):
    """Base class for all anonymization-related exceptions."""


class EntityTypeValidationError(DataDeidentifierError):
    """Raised when entity types validation fails."""


class TextAnonymizationError(AnonymizationError):
    """Raised when an error occurs during the text anonymization process."""


class InvalidInputTextError(TextAnonymizationError):
    """Raised when text to anonymize is invalid."""


class StructuredDataAnonymizationError(AnonymizationError):
    """Raised when an error occurs during the structured data anonymization process."""


class InvalidInputDataError(DataDeidentifierError):
    """Raised when data to anonymize is invalid."""


class UnsupportedStructuredDataError(DataDeidentifierError):
    """Raised when the data type is not supported."""


class PseudonymizationError(DataDeidentifierError):
    """Base class for all pseudonymization-related exceptions."""


class TextPseudonymizationError(PseudonymizationError):
    """Raised when an error occurs during the text pseudonymization process."""


class StructuredDataPseudonymizationError(PseudonymizationError):
    """Raised when an error occurs during the data pseudonymization process."""


class PseudonymEnrichmentError(DataDeidentifierError):
    """Raised when an error occurs during pseudonym enrichment process."""
