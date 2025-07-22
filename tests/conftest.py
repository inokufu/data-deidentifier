"""This file contains pytest fixtures available to all tests.

Fixtures are functions that pytest runs before tests to set up preconditions.
pytest automatically discovers this file and makes fixtures available
to all test modules without needing to import them.
"""

from unittest.mock import Mock

import pytest
from logger import LoggerContract

from src.data_deidentifier.domain.contracts.validator import EntityTypeValidatorContract
from src.data_deidentifier.domain.types.structured_anonymization_result import (
    StructuredDataAnalysisField,
)


@pytest.fixture
def mock_entity_validator() -> Mock:
    """Mock entity type validator contract."""
    mock_entity_validator = Mock(spec=EntityTypeValidatorContract)
    mock_entity_validator.validate_entity_types.return_value = []
    return mock_entity_validator


@pytest.fixture
def mock_logger() -> Mock:
    """Mock logger contract."""
    return Mock(spec=LoggerContract)


@pytest.fixture
def sample_structured_fields() -> list[StructuredDataAnalysisField]:
    """Sample structured data analysis fields for testing."""
    return [
        StructuredDataAnalysisField("name", "PERSON"),
        StructuredDataAnalysisField("email", "EMAIL"),
        StructuredDataAnalysisField("user.address.city", "LOCATION"),
    ]
