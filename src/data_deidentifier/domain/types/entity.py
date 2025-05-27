from dataclasses import dataclass


@dataclass
class Entity:
    """Represents a detected PII entity in content.

    This model captures information about a personally identifiable information (PII)
    entity detected in text or JSON content
    including its type, position, and confidence score.

    Attributes:
        type: The type of PII entity detected
        start: The starting position of the entity in the content
        end: The ending position of the entity in the content
        score: The confidence score of the detection (0.0 to 1.0)
        text: The actual text of the detected entity
        path: For JSON data, the dot notation path to the field containing the entity
    """

    type: str
    start: int
    end: int
    score: float
    text: str | None = None
    path: str | None = None  # For JSON data, dot notation path to the field

    def __post_init__(self) -> None:
        """Validate entity constraints."""
        if self.start < 0:
            raise ValueError(f"entity start position cannot be negative: {self.start}")

        if self.end < 0:
            raise ValueError(f"entity end position cannot be negative: {self.end}")

        if self.start > self.end:
            raise ValueError(
                f"entity start position ({self.start}) cannot be greater than "
                f"end position ({self.end})",
            )
