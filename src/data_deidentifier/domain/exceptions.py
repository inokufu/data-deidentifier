class DataDeidentifierError(Exception):
    """Base class for all exceptions in data-deidentifier."""


class AnalyzeError(DataDeidentifierError):
    """Base class for all analysis-related exceptions."""


class AnonymizationError(DataDeidentifierError):
    """Base class for all anonymization-related exceptions."""


class TextAnalysisError(AnalyzeError):
    """Raised when an error occurs during the text analysis process."""


class EntityTypeValidationError(DataDeidentifierError):
    """Raised when entity types validation fails."""


class TextAnonymizationError(AnonymizationError):
    """Raised when an error occurs during the text anonymization process."""


class StructuredDataAnalysisError(AnalyzeError):
    """Raised when an error occurs during the structured data analysis process."""


class StructuredDataAnonymizationError(AnonymizationError):
    """Raised when an error occurs during the structured data anonymization process."""


class UnsupportedStructuredDataError(DataDeidentifierError):
    """Raised when the data type is not supported."""
