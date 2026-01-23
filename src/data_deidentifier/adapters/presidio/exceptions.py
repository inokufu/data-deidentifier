from data_deidentifier.domain.exceptions import DataDeidentifierError


class AnalysisError(DataDeidentifierError):
    """Raised when an error occurs during the text analysis process."""


class TextAnalysisError(AnalysisError):
    """Raised when an error occurs during the text analysis process."""


class StructuredDataAnalysisError(AnalysisError):
    """Raised when an error occurs during the structured data analysis process."""
