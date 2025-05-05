class DataDeidentifierError(Exception):
    """Base class for all exceptions in data-deidentifier."""


class AnalyzeError(DataDeidentifierError):
    """Base class for all analysis-related exceptions."""


class AnalysisError(AnalyzeError):
    """Raised when an error occurs during the analysis process."""


class EntityTypeValidationError(AnalyzeError):
    """Raised when entity types validation fails."""


class AnonymizationError(DataDeidentifierError):
    """Raised when an error occurs during the anonymization process."""
