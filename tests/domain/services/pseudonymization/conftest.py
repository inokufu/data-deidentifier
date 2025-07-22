from unittest.mock import Mock

import pytest
from logger import LoggerContract

from src.data_deidentifier.domain.contracts.enricher.manager import (
    PseudonymEnrichmentManagerContract,
)
from src.data_deidentifier.domain.contracts.pseudonymizer.structured import (
    StructuredDataPseudonymizerContract,
)
from src.data_deidentifier.domain.contracts.pseudonymizer.text import (
    TextPseudonymizerContract,
)
from src.data_deidentifier.domain.contracts.validator import EntityTypeValidatorContract
from src.data_deidentifier.domain.services.pseudonymization.structured import (
    StructuredDataPseudonymizationService,
)
from src.data_deidentifier.domain.services.pseudonymization.text import (
    TextPseudonymizationService,
)
from src.data_deidentifier.domain.types.entity import Entity
from src.data_deidentifier.domain.types.structured_pseudonymization_result import (
    StructuredDataPseudonymizationResult,
)
from src.data_deidentifier.domain.types.text_pseudonymization_result import (
    TextPseudonymizationResult,
)


@pytest.fixture
def mock_text_pseudonymizer() -> Mock:
    """Mock text pseudonymizer contract."""
    return Mock(spec=TextPseudonymizerContract)


@pytest.fixture
def mock_enricher() -> Mock:
    """Mock pseudonym enrichment manager contract."""
    return Mock(spec=PseudonymEnrichmentManagerContract)


@pytest.fixture
def mock_text_pseudonymization_service(
    mock_text_pseudonymizer: TextPseudonymizerContract,
    mock_entity_validator: EntityTypeValidatorContract,
    mock_logger: LoggerContract,
) -> TextPseudonymizationService:
    """Text pseudonymization service without enricher."""
    return TextPseudonymizationService(
        pseudonymizer=mock_text_pseudonymizer,
        validator=mock_entity_validator,
        logger=mock_logger,
        pseudonym_enricher=None,
    )


@pytest.fixture
def mock_text_pseudonymization_service_with_enricher(
    mock_text_pseudonymizer: TextPseudonymizerContract,
    mock_entity_validator: EntityTypeValidatorContract,
    mock_logger: LoggerContract,
    mock_enricher: PseudonymEnrichmentManagerContract,
) -> TextPseudonymizationService:
    """Text pseudonymization service with enricher."""
    return TextPseudonymizationService(
        pseudonymizer=mock_text_pseudonymizer,
        validator=mock_entity_validator,
        logger=mock_logger,
        pseudonym_enricher=mock_enricher,
    )


@pytest.fixture
def sample_pseudonymization_result() -> TextPseudonymizationResult:
    """Sample pseudonymization result for testing."""
    return TextPseudonymizationResult(
        pseudonymized_text="<PERSON_123> lives in <LOCATION_456>",
        detected_entities=[
            Entity(type="PERSON", start=0, end=4, score=0.95, text="John"),
            Entity(type="LOCATION", start=15, end=21, score=0.88, text="London"),
        ],
    )


@pytest.fixture
def mock_data_pseudonymizer() -> Mock:
    """Mock structured data pseudonymizer contract."""
    return Mock(spec=StructuredDataPseudonymizerContract)


@pytest.fixture
def mock_data_pseudonymization_service(
    mock_data_pseudonymizer: StructuredDataPseudonymizerContract,
    mock_entity_validator: EntityTypeValidatorContract,
    mock_logger: LoggerContract,
) -> StructuredDataPseudonymizationService:
    """Structured data pseudonymization service without enricher."""
    return StructuredDataPseudonymizationService(
        pseudonymizer=mock_data_pseudonymizer,
        validator=mock_entity_validator,
        logger=mock_logger,
        pseudonym_enricher=None,
    )


@pytest.fixture
def mock_data_pseudo_service_with_enricher(
    mock_data_pseudonymizer: StructuredDataPseudonymizerContract,
    mock_entity_validator: EntityTypeValidatorContract,
    mock_logger: LoggerContract,
    mock_enricher: PseudonymEnrichmentManagerContract,
) -> StructuredDataPseudonymizationService:
    """Structured data pseudonymization service with enricher."""
    return StructuredDataPseudonymizationService(
        pseudonymizer=mock_data_pseudonymizer,
        validator=mock_entity_validator,
        logger=mock_logger,
        pseudonym_enricher=mock_enricher,
    )


@pytest.fixture
def sample_pseudonymized_data() -> dict:
    """Sample pseudonymized structured data for testing."""
    return {
        "name": "<PERSON_123>",
        "email": "<EMAIL_456>",
        "age": 30,
        "user": {"address": {"city": "<LOCATION_789> (France)", "country": "France"}},
    }


@pytest.fixture
def sample_structured_pseudonymization_result(
    sample_pseudonymized_data: dict,
    sample_structured_fields: list,
) -> StructuredDataPseudonymizationResult:
    """Sample structured data pseudonymization result for testing."""
    return StructuredDataPseudonymizationResult(
        pseudonymized_data=sample_pseudonymized_data,
        detected_fields=sample_structured_fields,
    )
