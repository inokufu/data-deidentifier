from typing import Any
from unittest.mock import Mock

import pytest

from src.data_deidentifier.domain.contracts.anonymizer.structured import (
    StructuredDataAnonymizerContract,
)
from src.data_deidentifier.domain.contracts.anonymizer.text import (
    TextAnonymizerContract,
)
from src.data_deidentifier.domain.services.anonymization.structured import (
    StructuredDataAnonymizationService,
)
from src.data_deidentifier.domain.services.anonymization.text import (
    TextAnonymizationService,
)
from src.data_deidentifier.domain.types.entity import Entity
from src.data_deidentifier.domain.types.structured_anonymization_result import (
    StructuredDataAnalysisField,
    StructuredDataAnonymizationResult,
)
from src.data_deidentifier.domain.types.text_anonymization_result import (
    TextAnonymizationResult,
)


@pytest.fixture
def sample_entity() -> Entity:
    """Sample entity for testing."""
    return Entity(type="PERSON", start=0, end=4, score=0.95, text="John")


@pytest.fixture
def sample_text_anonymization_result(sample_entity: Entity) -> TextAnonymizationResult:
    """Sample text anonymization result for testing."""
    return TextAnonymizationResult(
        anonymized_text="<PERSON> is a person",
        detected_entities=[sample_entity],
    )


@pytest.fixture
def sample_anonymized_data() -> dict[str, Any]:
    """Sample anonymized structured data for testing."""
    return {
        "name": "******",
        "email": "********",
        "age": 30,
        "user": {
            "address": {
                "city": "*******",
                "country": "France",
            },
        },
    }


@pytest.fixture
def sample_data_anonymization_result(
    sample_anonymized_data: dict[str, Any],
    sample_structured_fields: list[StructuredDataAnalysisField],
) -> StructuredDataAnonymizationResult:
    """Sample structured data anonymization result for testing."""
    return StructuredDataAnonymizationResult(
        anonymized_data=sample_anonymized_data,
        detected_fields=sample_structured_fields,
    )


@pytest.fixture
def mock_text_anonymizer() -> Mock:
    """Mock text anonymizer contract."""
    return Mock(spec=TextAnonymizerContract)


@pytest.fixture
def mock_text_anonymization_service(
    mock_text_anonymizer: Mock,
    mock_entity_validator: Mock,
) -> TextAnonymizationService:
    """Text anonymization service with mocked dependencies."""
    return TextAnonymizationService(
        anonymizer=mock_text_anonymizer,
        validator=mock_entity_validator,
    )


@pytest.fixture
def mock_data_anonymizer() -> Mock:
    """Mock structured data anonymizer contract."""
    return Mock(spec=StructuredDataAnonymizerContract)


@pytest.fixture
def mock_data_anonymization_service(
    mock_data_anonymizer: Mock,
    mock_entity_validator: Mock,
) -> StructuredDataAnonymizationService:
    """Structured data anonymization service with mocked dependencies."""
    return StructuredDataAnonymizationService(
        anonymizer=mock_data_anonymizer,
        validator=mock_entity_validator,
    )
