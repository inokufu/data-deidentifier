from enum import StrEnum


class SupportedLanguage(StrEnum):
    """Languages supported for PII detection and anonymization.

    Additional languages may be added in future releases.
    """

    ENGLISH = "en"
    FRENCH = "fr"
